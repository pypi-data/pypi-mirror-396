import numpy as np
import math
from fmot.fqir import TensorProto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fmot.fqir.writer import FQIRWriter


def _get_mod_seq(order):
    """Returns the order of `k`s in (index % 2**order) == k subsequences for partial bit order
    reversal.

    Example:
    # trivial order-0 case:
    _get_mod_seq(0) --> [0]

    # order-1: even, odd subsequences
    # (index % 2 == 0), (index % 2 == 1)
    _get_mod_seq(1) --> [0, 1]

    # order-2:
    # (index % 4 == 0), (index % 4 == 2), (index % 4 == 1), (index % 4 == 3)
    _get_mod_seq(2) --> [0, 2, 1, 3]
    """
    mset = [0]
    for ord in range(order):
        ord = 2**ord

        new_mset = []
        for x in mset:
            new_mset.append(x)
            new_mset.append(x + ord)
        mset = new_mset

    return mset


def get_partial_bit_reversal_permutation_matrix(N: int, order: int):
    """Returns a matrix that performs partial bitorder reversal (as part of FFT)

    Arguments:
        N (int): length of the input signal
        order (int): number of decomposition stages
    """
    m = np.zeros((N, N))
    perm_set = _get_mod_seq(order)
    base = 2**order

    k = 0
    for p in perm_set:
        for j in range(N // base):
            m[j * base + p, k] = 1
            k += 1
    return m.T


def get_fft_matrix(N: int):
    return np.fft.fft(np.eye(N)).T


def get_ifft_matrix(N: int):
    return np.fft.ifft(np.eye(N)).T


def get_rfft2fft_matrices(n: int):
    """Reconstruct full FFT from RFFT via sparse matrix multiplication.

    Returns
        - mat_real: Tensor of shape (n_fft, n_rfft)
        - mat_imag: Tensor of shape (n_fft, n_rfft)

    Full FFT can be reconstructed from rfft as:

    ```python
        fft_real = mat_real @ rfft_real
        fft_imag = mat_imag @ rfft_imag
    ```
    """
    n_rfft = n // 2 + 1

    mat_real = np.zeros((n_rfft, n))
    mat_imag = np.zeros((n_rfft, n))

    mat_real[:n_rfft, :n_rfft] = np.eye(n_rfft)
    mat_imag[:n_rfft, :n_rfft] = np.eye(n_rfft)

    rem = n - n_rfft
    m_rev = np.eye(rem)[::-1]

    mat_real[1 : rem + 1, n_rfft:] = m_rev
    mat_imag[1 : rem + 1, n_rfft:] = -m_rev

    return mat_real.T, mat_imag.T


def get_complex_twiddle(n, inv=False) -> np.ndarray:
    sign = -1
    if inv:
        sign = 1
    base = np.exp(sign * 1j * np.pi / n)
    w = np.power(base, np.arange(n))
    return w


def _fft_real_x(
    writer: "FQIRWriter", x: TensorProto, order: int, quanta: int = None
) -> tuple[TensorProto, TensorProto]:
    N = x.shape[0]
    assert N % 2**order == 0

    if quanta is None:
        quanta = x.quanta + int(math.ceil(math.log2(N)))

    l_sub = N // 2**order

    if order >= 1:
        m_perm = get_partial_bit_reversal_permutation_matrix(N, order)
        m_perm = writer.add_parameter(m_perm, precision="int8", quanta=0)
        x = writer.matmul(m_perm, x, quanta=x.quanta, round=False)
        subvectors = writer.split(x, [l_sub] * 2**order)
    else:
        subvectors = [x]

    m_fft = get_fft_matrix(l_sub)
    # multiply RFFT matrix by 127/128 so that we can use quanta=-7 without clipping
    # we will invert this later on
    m_fft = m_fft * 127 / 128
    m_fft_re = writer.add_parameter(m_fft.real, precision="int8", quanta=-7)
    m_fft_im = writer.add_parameter(m_fft.imag, precision="int8", quanta=-7)

    q_curr = x.quanta + int(math.ceil(math.log2(l_sub)))
    q_curr = min(q_curr, quanta)
    subvectors_re = [writer.matmul(m_fft_re, x, quanta=q_curr) for x in subvectors]
    subvectors_im = [writer.matmul(m_fft_im, x, quanta=q_curr) for x in subvectors]

    # butterflies
    while len(subvectors_re) > 1:
        l_curr = subvectors_re[0].shape[0]
        twid = get_complex_twiddle(l_curr, inv=False)
        twid_re = writer.add_parameter(twid.real, precision="int16", quanta=-14)
        twid_im = writer.add_parameter(twid.imag, precision="int16", quanta=-14)

        q_curr = min(q_curr + 1, quanta)

        new_subvectors_re = []
        new_subvectors_im = []

        for even_re, even_im, odd_re, odd_im in zip(
            subvectors_re[::2],
            subvectors_im[::2],
            subvectors_re[1::2],
            subvectors_im[1::2],
        ):
            odd_re, odd_im = writer.complex_multiply(
                odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta
            )
            a_re = writer.add(even_re, odd_re, quanta=q_curr)
            a_im = writer.add(even_im, odd_im, quanta=q_curr)
            b_re = writer.sub(even_re, odd_re, quanta=q_curr)
            b_im = writer.sub(even_im, odd_im, quanta=q_curr)

            new_re = writer.cat([a_re, b_re])
            new_im = writer.cat([a_im, b_im])

            new_subvectors_re.append(new_re)
            new_subvectors_im.append(new_im)

        subvectors_re = new_subvectors_re
        subvectors_im = new_subvectors_im

    y_re = subvectors_re[0]
    y_im = subvectors_im[0]

    # invert the scaling of 127/128
    y_re = writer.multiply(y_re, 128 / 127, quanta=y_re.quanta)
    y_im = writer.multiply(y_im, 128 / 127, quanta=y_re.quanta)

    return y_re, y_im


def _fft_real_x_looped(
    writer: "FQIRWriter", x: TensorProto, order: int, quanta: int = None, minloopdepth=4
) -> tuple[TensorProto, TensorProto]:
    N = x.shape[0]
    assert N % 2**order == 0

    if quanta is None:
        quanta = x.quanta + int(math.ceil(math.log2(N)))

    l_sub = N // 2**order

    if order >= 1:
        m_perm = get_partial_bit_reversal_permutation_matrix(N, order)
        m_perm = writer.add_parameter(m_perm, precision="int8", quanta=0)
        x = writer.matmul(m_perm, x, quanta=x.quanta, round=False)

    n_subvectors = 2**order

    m_fft = get_fft_matrix(l_sub)
    # multiply RFFT matrix by 127/128 so that we can use quanta=-7 without clipping
    # we will invert this later on
    m_fft = m_fft * 127 / 128
    q_curr = x.quanta + int(math.ceil(math.log2(l_sub)))
    q_curr = min(q_curr, quanta)

    if n_subvectors == 1:
        m_fft_re = writer.add_parameter(m_fft.real, precision="int8", quanta=-7)
        m_fft_im = writer.add_parameter(m_fft.imag, precision="int8", quanta=-7)

        y_re = writer.matmul(m_fft_re, x, quanta=q_curr)
        y_im = writer.matmul(m_fft_im, x, quanta=q_curr)

        return y_re, y_im

    with writer.for_loop_writer(
        n_iter=n_subvectors, x_to_slice=[x], x_recurse_init=[]
    ) as lwriter:
        (x_curr,) = lwriter.sliced_inputs

        m_fft_re = lwriter.add_parameter(m_fft.real, precision="int8", quanta=-7)
        m_fft_im = lwriter.add_parameter(m_fft.imag, precision="int8", quanta=-7)

        sub_re = lwriter.matmul(m_fft_re, x_curr, quanta=q_curr)
        sub_im = lwriter.matmul(m_fft_im, x_curr, quanta=q_curr)

        subvectors_re = lwriter.return_concatenated(sub_re)
        subvectors_im = lwriter.return_concatenated(sub_im)

    # looped butterflies
    while n_subvectors >= max(minloopdepth, 2):
        l_curr = N // n_subvectors

        with writer.for_loop_writer(
            n_iter=n_subvectors // 2,
            x_to_slice=[subvectors_re, subvectors_im],
            x_recurse_init=[],
        ) as lwriter:
            re_curr, im_curr = lwriter.sliced_inputs

            twid = get_complex_twiddle(l_curr, inv=False)
            twid_re = lwriter.add_parameter(twid.real, precision="int16", quanta=-14)
            twid_im = lwriter.add_parameter(twid.imag, precision="int16", quanta=-14)

            q_curr = min(q_curr + 1, quanta)

            even_re, odd_re = lwriter.split(re_curr, [l_curr, l_curr])
            even_im, odd_im = lwriter.split(im_curr, [l_curr, l_curr])

            odd_re, odd_im = lwriter.complex_multiply(
                odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta
            )
            a_re = lwriter.add(even_re, odd_re, quanta=q_curr)
            a_im = lwriter.add(even_im, odd_im, quanta=q_curr)
            b_re = lwriter.sub(even_re, odd_re, quanta=q_curr)
            b_im = lwriter.sub(even_im, odd_im, quanta=q_curr)

            new_re = lwriter.cat([a_re, b_re])
            new_im = lwriter.cat([a_im, b_im])

            subvectors_re = lwriter.return_concatenated(new_re)
            subvectors_im = lwriter.return_concatenated(new_im)

        n_subvectors = n_subvectors // 2

    if minloopdepth > 1:
        # unlooped butterflies
        l_curr = N // n_subvectors
        subvectors_re = writer.split(subvectors_re, [l_curr] * n_subvectors)
        subvectors_im = writer.split(subvectors_im, [l_curr] * n_subvectors)

        while n_subvectors > 1:
            l_curr = N // n_subvectors
            twid = get_complex_twiddle(l_curr, inv=False)
            twid_re = writer.add_parameter(twid.real, precision="int16", quanta=-14)
            twid_im = writer.add_parameter(twid.imag, precision="int16", quanta=-14)

            q_curr = min(q_curr + 1, quanta)

            new_subvectors_re = []
            new_subvectors_im = []

            for even_re, odd_re, even_im, odd_im in zip(
                subvectors_re[::2],
                subvectors_re[1::2],
                subvectors_im[::2],
                subvectors_im[1::2],
            ):
                odd_re, odd_im = writer.complex_multiply(
                    odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta
                )
                a_re = writer.add(even_re, odd_re, quanta=q_curr)
                a_im = writer.add(even_im, odd_im, quanta=q_curr)
                b_re = writer.sub(even_re, odd_re, quanta=q_curr)
                b_im = writer.sub(even_im, odd_im, quanta=q_curr)

                new_subvectors_re.append(writer.cat([a_re, b_re]))
                new_subvectors_im.append(writer.cat([a_im, b_im]))

            subvectors_re = new_subvectors_re
            subvectors_im = new_subvectors_im
            n_subvectors = n_subvectors // 2

        y_re = subvectors_re[0]
        y_im = subvectors_im[0]

    else:
        y_re = subvectors_re
        y_im = subvectors_im

    # invert the scaling of 127/128
    y_re = writer.multiply(y_re, 128 / 127, quanta=y_re.quanta)
    y_im = writer.multiply(y_im, 128 / 127, quanta=y_re.quanta)

    return y_re, y_im


def _fft_complex_x(
    writer: "FQIRWriter",
    x_re: TensorProto,
    x_im: TensorProto,
    order: int,
    quanta: int = None,
) -> tuple[TensorProto, TensorProto]:
    N = x_re.shape[0]
    assert N % 2**order == 0

    if quanta is None:
        quanta = max(x_re.quanta, x_im.quanta) + int(math.ceil(math.log2(N)))

    l_sub = N // 2**order

    if order >= 1:
        m_perm = get_partial_bit_reversal_permutation_matrix(N, order)
        m_perm = writer.add_parameter(m_perm, precision="int8", quanta=0)
        x_re = writer.matmul(m_perm, x_re, quanta=x_re.quanta, round=False)
        x_im = writer.matmul(m_perm, x_im, quanta=x_im.quanta, round=False)
        subvectors_re = writer.split(x_re, [l_sub] * 2**order)
        subvectors_im = writer.split(x_im, [l_sub] * 2**order)
    else:
        subvectors_re = [x_re]
        subvectors_im = [x_im]

    m_fft = get_fft_matrix(l_sub)
    # multiply RFFT matrix by 127/128 so that we can use quanta=-7 without clipping
    # we will invert this later on
    m_fft = m_fft * 127 / 128
    m_fft_re = writer.add_parameter(m_fft.real, precision="int8", quanta=-7)
    m_fft_im = writer.add_parameter(m_fft.imag, precision="int8", quanta=-7)

    q_curr = max(x_re.quanta, x_im.quanta) + int(math.ceil(math.log2(l_sub)))
    q_curr = min(q_curr, quanta)

    new_subs_re = []
    new_subs_im = []
    for sub_re, sub_im in zip(subvectors_re, subvectors_im):
        s_re = writer.sub(
            writer.matmul(m_fft_re, sub_re, quanta=q_curr),
            writer.matmul(m_fft_im, sub_im, quanta=q_curr),
            quanta=q_curr,
        )
        s_im = writer.add(
            writer.matmul(m_fft_re, sub_im, quanta=q_curr),
            writer.matmul(m_fft_im, sub_re, quanta=q_curr),
            quanta=q_curr,
        )
        new_subs_re.append(s_re)
        new_subs_im.append(s_im)

    subvectors_re = new_subs_re
    subvectors_im = new_subs_im

    # butterflies
    while len(subvectors_re) > 1:
        l_curr = subvectors_re[0].shape[0]
        twid = get_complex_twiddle(l_curr, inv=False)
        twid_re = writer.add_parameter(twid.real, precision="int16", quanta=-14)
        twid_im = writer.add_parameter(twid.imag, precision="int16", quanta=-14)

        q_curr = min(q_curr + 1, quanta)

        new_subvectors_re = []
        new_subvectors_im = []

        for even_re, even_im, odd_re, odd_im in zip(
            subvectors_re[::2],
            subvectors_im[::2],
            subvectors_re[1::2],
            subvectors_im[1::2],
        ):
            odd_re, odd_im = writer.complex_multiply(
                odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta
            )
            a_re = writer.add(even_re, odd_re, quanta=q_curr)
            a_im = writer.add(even_im, odd_im, quanta=q_curr)
            b_re = writer.sub(even_re, odd_re, quanta=q_curr)
            b_im = writer.sub(even_im, odd_im, quanta=q_curr)

            new_re = writer.cat([a_re, b_re])
            new_im = writer.cat([a_im, b_im])

            new_subvectors_re.append(new_re)
            new_subvectors_im.append(new_im)

    y_re = subvectors_re[0]
    y_im = subvectors_im[0]

    # invert the scaling of 127/128
    y_re = writer.multiply(y_re, 128 / 127, quanta=y_re.quanta)
    y_im = writer.multiply(y_im, 128 / 127, quanta=y_re.quanta)

    return y_re, y_im


def fft(
    writer: "FQIRWriter",
    x_re: TensorProto,
    x_im: TensorProto,
    order: int,
    quanta: int = None,
    loopmethod: bool = True,
) -> tuple[TensorProto, TensorProto]:
    """
    Computes the FFT of the signal

    Arguments:
        x_re (TensorProto): real-part of input signal
        x_im (TensorProto): imag-part of input signal. If `None`, uses a kernel optimized for
            the full FFT of a real signal.
        order (int): number of decomposition stages
        quanta (int, optional): output quanta. If `None`, then `quanta = x.quanta + ceil(log2(N))`
            for signal of length `N`.

    Returns:
        tuple[TensorProto, TensorProto]: real and imaginary components from the FFT
    """
    if x_im is not None:
        return _fft_complex_x(writer, x_re, x_im, order, quanta)
    else:
        if loopmethod:
            return _fft_real_x_looped(writer, x_re, order, quanta)
        else:
            return _fft_real_x(writer, x_re, order, quanta)


def _rfft_via_half_fft(
    writer: "FQIRWriter", x: TensorProto, order: int, quanta: int = None
):
    """
    RFFT via packing trick using a single FFT of length N//2.
    Returns bins 0..N//2 (same as np.fft.rfft).

    DOESN'T WORK!
    """
    N = x.shape[0]
    assert N % 2 == 0, "N must be even"
    n2 = N // 2

    # 1) Pack even/odd into complex vector
    z_re, z_im = writer.deinterleave(x, 2)

    # 2) One complex FFT of length n2
    Z_re, Z_im = fft(writer, z_re, z_im, max(order - 1, 0), quanta=quanta)

    # 3) Recover E and O from Z[k] and conj(Z[-k])
    # \tilde Z[k] = conj(Z[-k])
    idx_neg = (-np.arange(n2)) % n2  # k -> (-k) mod n2
    perm = np.zeros((n2, n2))
    for i, j in enumerate(idx_neg):
        perm[j, i] = 1
    perm = writer.add_parameter(perm, precision="int8", quanta=0)
    Z_tilde_re = writer.matmul(perm, Z_re, quanta=Z_re.quanta)
    Z_tilde_im = writer.matmul(
        perm, writer.multiply(Z_im, -1, quanta=Z_im.quanta), quanta=Z_im.quanta
    )

    q_curr = max(Z_re.quanta, Z_im.quanta)
    # E = 0.5 * (Z + Z_tilde)
    E_re = writer.add(Z_re, Z_tilde_re, quanta=q_curr + 1)
    E_im = writer.add(Z_im, Z_tilde_im, quanta=q_curr + 1)
    E_re = writer.multiply(E_re, 0.5, quanta=q_curr)
    E_im = writer.multiply(E_im, 0.5, quanta=q_curr)

    # O = (0.5j) * (Z_tilde - Z)
    O_im = writer.sub(Z_tilde_re, Z_re, quanta=q_curr + 1)
    O_re = writer.sub(Z_re, Z_tilde_re, quanta=q_curr)
    O_im = writer.multiply(O_im, 0.5, quanta=q_curr)
    O_re = writer.multiply(O_re, 0.5, quanta=q_curr)

    # 4) Twiddle and combine for k = 0..n2
    # W_N^k, length n2
    k = np.arange(n2)
    twid = np.exp(-2j * np.pi * k / N)
    twid_re = writer.add_parameter(twid.real, quanta=-14)
    twid_im = writer.add_parameter(twid.imag, quanta=-14)

    # out[:n2] = E + twid * O
    # out[n2] = (E - twid * O)[0]
    O_re, O_im = writer.complex_multiply(twid_re, twid_im, O_re, O_im, quanta=q_curr)
    out_re = writer.add(E_re, O_re)
    out_im = writer.add(E_im, O_im)

    out_re1 = writer.sub(E_re, O_re)
    out_im1 = writer.sub(E_im, O_im)
    out_re1, _ = writer.split(out_re1, [1, n2 - 1])
    out_im1, _ = writer.split(out_im1, [1, n2 - 1])

    out_re = writer.cat([out_re, out_re1])
    out_im = writer.cat([out_im, out_im1])

    return out_re, out_im


def _rfft_via_fft(
    writer: "FQIRWriter",
    x: TensorProto,
    order: int,
    quanta: int = None,
    loopmethod=True,
):
    """
    RFFT via FFT of length N.
    """
    N = x.shape[0]
    n1 = int(math.floor(N / 2 + 1))

    y_re, y_im = fft(writer, x, None, order, quanta, loopmethod=loopmethod)

    y_re, _ = writer.split(y_re, [n1, N - n1])
    y_im, _ = writer.split(y_im, [n1, N - n1])

    return y_re, y_im


def rfft(
    writer: "FQIRWriter",
    x: TensorProto,
    order: int,
    quanta: int = None,
    loopmethod=True,
):
    """
    Computes the RFFT of the signal

    Arguments:
        x (TensorProto): input signal
        order (int): number of decomposition stages
        quanta (int, optional): output quanta. If `None`, then `quanta = x.quanta + ceil(log2(N))`
            for signal of length `N`.

    Returns:
        tuple[TensorProto, TensorProto]: real and imaginary components from the RFFT
    """

    # note: _rfft_via_half_fft might be more efficient, but current is not working properly
    return _rfft_via_fft(writer, x, order, quanta, loopmethod=loopmethod)


# def ifft(writer: "FQIRWriter", X_re: TensorProto, X_im: TensorProto, order: int, quanta: int=None):

#     N = X_re.shape[0]

#     if quanta is None:
#         quanta = max(X_re.quanta, X_im.quanta) - int(math.ceil(math.log2(N)))

#     l_sub = N // 2**order

#     if order >= 1:
#         m_perm = get_partial_bit_reversal_permutation_matrix(N, order)
#         m_perm = writer.add_parameter(m_perm, precision="int8", quanta=0)
#         X_re = writer.matmul(m_perm, X_re, quanta=X_re.quanta, round=False)
#         X_im = writer.matmul(m_perm, X_im, quanta=X_im.quanta, round=False)
#         subvectors_re = writer.split(X_re, [l_sub] * 2**order)
#         subvectors_im = writer.split(X_im, [l_sub] * 2**order)
#     else:
#         subvectors_re = [X_re]
#         subvectors_im = [X_im]

#     m_ifft = get_ifft_matrix(l_sub)
#     # multiply IFFT matrix by 127/128 so that we can use quanta=-7 without clipping
#     # we will invert this later on
#     m_ifft = m_ifft * 127/128
#     q_mat = -7 - int(math.ceil(math.log2(l_sub)))

#     assert np.max(np.abs(m_ifft.real)) <= 2 ** (q_mat + 7)
#     assert np.max(np.abs(m_ifft.real)) >= 2 ** (q_mat + 6)

#     m_ifft_re = writer.add_parameter(m_ifft.real, precision="int8", quanta=q_mat)
#     m_ifft_im = writer.add_parameter(m_ifft.imag, precision="int8", quanta=q_mat)

#     q_curr = max(X_re.quanta, X_im.quanta) + int(math.ceil(math.log2(l_sub)))
#     q_curr = min(q_curr, quanta)
#     print(q_curr)

#     if order == 0:
#         q_curr = quanta

#     new_subs_re = []
#     new_subs_im = []
#     for sub_re, sub_im in zip(subvectors_re, subvectors_im):
#         s_re = writer.sub(
#             writer.matmul(m_ifft_re, sub_re, quanta=q_curr),
#             writer.matmul(m_ifft_im, sub_im, quanta=q_curr),
#             quanta=q_curr
#         )
#         s_im = writer.add(
#             writer.matmul(m_ifft_re, sub_im, quanta=q_curr),
#             writer.matmul(m_ifft_im, sub_re, quanta=q_curr),
#             quanta=q_curr
#         )
#         new_subs_re.append(s_re)
#         new_subs_im.append(s_im)

#     subvectors_re = new_subs_re
#     subvectors_im = new_subs_im

#     # butterflies
#     while len(subvectors_re) > 1:
#         l_curr = subvectors_re[0].shape[0]
#         twid = get_complex_twiddle(l_curr, inv=True)
#         twid_re = writer.add_parameter(twid.real, precision="int16", quanta=-14)
#         twid_im = writer.add_parameter(twid.imag, precision="int16", quanta=-14)

#         q_curr = min(q_curr+1, quanta)

#         new_subvectors_re = []
#         new_subvectors_im = []

#         for even_re, even_im, odd_re, odd_im in zip(subvectors_re[::2], subvectors_im[::2], subvectors_re[1::2], subvectors_im[1::2]):
#             odd_re, odd_im = writer.complex_multiply(odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta)
#             a_re = writer.add(even_re, odd_re, quanta=q_curr)
#             a_im = writer.add(even_im, odd_im, quanta=q_curr)
#             b_re = writer.sub(even_re, odd_re, quanta=q_curr)
#             b_im = writer.sub(even_im, odd_im, quanta=q_curr)

#             new_re = writer.cat([a_re, b_re])
#             new_im = writer.cat([a_im, b_im])

#             new_subvectors_re.append(new_re)
#             new_subvectors_im.append(new_im)

#         subvectors_re = new_subvectors_re
#         subvectors_im = new_subvectors_im

#     y_re = subvectors_re[0]
#     y_im = subvectors_im[0]

#     # invert the scaling of 127/128
#     y_re = writer.multiply(y_re, 128/127, quanta=y_re.quanta)
#     y_im = writer.multiply(y_im, 128/127, quanta=y_re.quanta)

#     return y_re, y_im


def ifft(
    writer: "FQIRWriter",
    X_re: TensorProto,
    X_im: TensorProto,
    order: int,
    quanta: int = None,
):
    N = X_re.shape[0]

    if quanta is None:
        quanta = X_re.quanta + int(math.ceil(math.log2(N)))
        print(f"{quanta=}")

    l_sub = N // 2**order

    if order >= 1:
        m_perm = get_partial_bit_reversal_permutation_matrix(N, order)
        m_perm = writer.add_parameter(m_perm, precision="int8", quanta=0)
        X_re = writer.matmul(m_perm, X_re, quanta=X_re.quanta, round=False)
        X_im = writer.matmul(m_perm, X_im, quanta=X_im.quanta, round=False)
        subvectors_re = writer.split(X_re, [l_sub] * 2**order)
        subvectors_im = writer.split(X_im, [l_sub] * 2**order)
    else:
        subvectors_re = [X_re]
        subvectors_im = [X_im]

    m_ifft = get_ifft_matrix(l_sub)
    # multiply IFFT matrix by 127/128 so that we can use quanta=-7 without clipping
    # we will invert this later on
    m_ifft = m_ifft * 127 / 128 * l_sub
    q_mat = -7

    m_ifft_re = writer.add_parameter(m_ifft.real, precision="int8", quanta=q_mat)
    m_ifft_im = writer.add_parameter(m_ifft.imag, precision="int8", quanta=q_mat)

    q_curr = max(X_re.quanta, X_im.quanta) + int(math.ceil(math.log2(l_sub)))
    q_curr = min(q_curr, quanta)

    if order == 0:
        q_curr = quanta

    new_subs_re = []
    new_subs_im = []
    for sub_re, sub_im in zip(subvectors_re, subvectors_im):
        s_re = writer.sub(
            writer.matmul(m_ifft_re, sub_re, quanta=q_curr),
            writer.matmul(m_ifft_im, sub_im, quanta=q_curr),
            quanta=q_curr,
        )
        s_im = writer.add(
            writer.matmul(m_ifft_re, sub_im, quanta=q_curr),
            writer.matmul(m_ifft_im, sub_re, quanta=q_curr),
            quanta=q_curr,
        )
        new_subs_re.append(s_re)
        new_subs_im.append(s_im)

    subvectors_re = new_subs_re
    subvectors_im = new_subs_im

    # butterflies
    while len(subvectors_re) > 1:
        l_curr = subvectors_re[0].shape[0]
        twid = get_complex_twiddle(l_curr, inv=True)
        twid_re = writer.add_parameter(twid.real, precision="int16", quanta=-14)
        twid_im = writer.add_parameter(twid.imag, precision="int16", quanta=-14)

        q_curr = min(q_curr + 1, quanta)

        new_subvectors_re = []
        new_subvectors_im = []

        for even_re, even_im, odd_re, odd_im in zip(
            subvectors_re[::2],
            subvectors_im[::2],
            subvectors_re[1::2],
            subvectors_im[1::2],
        ):
            odd_re, odd_im = writer.complex_multiply(
                odd_re, odd_im, twid_re, twid_im, quanta=odd_re.quanta
            )
            a_re = writer.add(even_re, odd_re, quanta=q_curr)
            a_im = writer.add(even_im, odd_im, quanta=q_curr)
            b_re = writer.sub(even_re, odd_re, quanta=q_curr)
            b_im = writer.sub(even_im, odd_im, quanta=q_curr)

            new_re = writer.cat([a_re, b_re])
            new_im = writer.cat([a_im, b_im])

            new_subvectors_re.append(new_re)
            new_subvectors_im.append(new_im)

        subvectors_re = new_subvectors_re
        subvectors_im = new_subvectors_im

    y_re = subvectors_re[0]
    y_im = subvectors_im[0]

    # invert the scaling of 127/(128 * N**2) and adjust quanta
    factor = 128 / (127 * N**2)
    y_re = writer.multiply(
        y_re, factor, quanta=y_re.quanta - math.floor(2 * math.log2(N))
    )
    y_im = writer.multiply(
        y_im, factor, quanta=y_re.quanta - math.floor(2 * math.log2(N))
    )

    return y_re, y_im


def _irfft_via_ifft(
    writer: "FQIRWriter",
    n: int,
    X_re: TensorProto,
    X_im: TensorProto,
    order: int,
    quanta: int = None,
):
    n1 = X_re.shape[0]
    assert n in [n1 * 2 - 2, n1 * 2 - 1]

    m_re, m_im = get_rfft2fft_matrices(n)
    m_re = writer.add_parameter(m_re, precision="int8", quanta=0)
    m_im = writer.add_parameter(m_im, precision="int8", quanta=0)

    X_re = writer.matmul(m_re, X_re, quanta=X_re.quanta)
    X_im = writer.matmul(m_im, X_im, quanta=X_im.quanta)

    if quanta is None:
        quanta = X_re.quanta - int(math.ceil(math.log2(X_re.shape[0])))

    y, _ = ifft(writer, X_re, X_im, order, quanta)
    return y


def irfft(
    writer: "FQIRWriter",
    n: int,
    X_re: TensorProto,
    X_im: TensorProto,
    order: int,
    quanta: int = None,
):
    return _irfft_via_ifft(writer, n, X_re, X_im, order, quanta)
