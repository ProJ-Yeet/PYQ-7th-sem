# -*- coding: utf-8 -*-
"""DFT, FFT and circular convolution solver for DSAP chapter 7.

    python dft.py            # self-tests, then every PYQ answer

Everything the chapter 7 notes print is produced here: the N-point DFT, the
stage-by-stage DIT and DIF butterfly arrays, circular convolution by the
direct shift-and-sum method and through the DFT, and linear convolution via
circular with zero padding.

Conventions, stated once:

  * W_N = e^{-j2pi/N}, so X[k] = sum_n x[n] W_N^{nk} with a MINUS sign in the
    exponent, and the IDFT carries the 1/N.

  * DIT takes its input in BIT-REVERSED order and gives output in natural
    order.  DIF is the mirror image: natural in, bit-reversed out.  Both run
    log2(N) stages of N/2 butterflies.  dit_stages() and dif_stages() return
    the array after every stage, which is what a butterfly diagram is
    labelled with, and what the notes tabulate.

  * A sequence shorter than N is ZERO PADDED on the right.  Many papers print
    a 6 or 7 entry sequence for an 8 point transform; that is what they mean,
    and pad() records how many zeros it added so the notes can say so.
"""
import cmath
import math

FAIL = []
OK = [0]


def chk(tag, got, want, tol=1e-9):
    if isinstance(want, (list, tuple)):
        same = len(got) == len(want) and all(
            abs(complex(a) - complex(b)) <= tol for a, b in zip(got, want))
    else:
        same = abs(complex(got) - complex(want)) <= tol
    if same:
        OK[0] += 1
    else:
        FAIL.append("%s\n     got  %s\n     want %s" % (tag, got, want))


# ------------------------------------------------------------- primitives ---
def W(N, k=1):
    """The twiddle factor W_N^k = e^{-j2pi k/N}."""
    return cmath.exp(-2j * cmath.pi * k / N)


def pad(x, N):
    """Zero pad (or report an over-long sequence). Returns (padded, n_zeros)."""
    x = [complex(v) for v in x]
    if len(x) > N:
        raise ValueError("sequence of %d will not fit an %d point DFT"
                         % (len(x), N))
    return x + [0j] * (N - len(x)), N - len(x)


def dft(x, N=None):
    """Direct O(N^2) DFT, the definition, used as the reference answer."""
    if N is None:
        N = len(x)
    xv, _ = pad(x, N)
    return [sum(xv[n] * W(N, n * k) for n in range(N)) for k in range(N)]


def idft(X):
    """Inverse DFT. The 1/N and the conjugated twiddle are the only changes."""
    N = len(X)
    Xv = [complex(v) for v in X]
    return [sum(Xv[k] * W(N, -n * k) for k in range(N)) / N for n in range(N)]


def bitrev(N):
    """The bit-reversed index order for an N point radix-2 transform."""
    bits = int(math.log2(N))
    out = []
    for i in range(N):
        r = 0
        for b in range(bits):
            if i >> b & 1:
                r |= 1 << (bits - 1 - b)
        out.append(r)
    return out


def is_pow2(N):
    return N > 0 and (N & (N - 1)) == 0


# -------------------------------------------------------------- radix-2 FFT ---
def dit_stages(x, N=None):
    """Decimation in time. Returns (stages, order_in, X).

    stages[s] is the array after stage s+1, so stages[-1] is X[k] in natural
    order. order_in is the bit-reversed input permutation the diagram's left
    column is labelled with."""
    if N is None:
        N = len(x)
    if not is_pow2(N):
        raise ValueError("radix-2 needs N a power of 2, not %d" % N)
    xv, _ = pad(x, N)
    order = bitrev(N)
    a = [xv[i] for i in order]
    stages = []
    size = 2
    while size <= N:
        half = size // 2
        b = list(a)
        for start in range(0, N, size):
            for j in range(half):
                t = W(size, j) * a[start + half + j]
                u = a[start + j]
                b[start + j] = u + t
                b[start + half + j] = u - t
        a = b
        stages.append(list(a))
        size *= 2
    return stages, order, list(a)


def dif_stages(x, N=None):
    """Decimation in frequency. Returns (stages, order_out, X).

    Input is in natural order; the array after the last stage is in
    BIT-REVERSED order, and order_out un-permutes it into X[k]."""
    if N is None:
        N = len(x)
    if not is_pow2(N):
        raise ValueError("radix-2 needs N a power of 2, not %d" % N)
    a, _ = pad(x, N)
    stages = []
    size = N
    while size >= 2:
        half = size // 2
        b = list(a)
        for start in range(0, N, size):
            for j in range(half):
                u = a[start + j]
                v = a[start + half + j]
                b[start + j] = u + v
                b[start + half + j] = (u - v) * W(size, j)
        a = b
        stages.append(list(a))
        size //= 2
    order = bitrev(N)
    X = [0j] * N
    for i, r in enumerate(order):
        X[r] = a[i]
    return stages, order, X


def ifft_via_fft(X):
    """The trick 72 Ash asks for: an IDFT from a forward DFT routine.
    conj -> forward DFT -> conj -> divide by N."""
    N = len(X)
    c = [complex(v).conjugate() for v in X]
    Y = dft(c, N)
    return [v.conjugate() / N for v in Y]


def complexity(N):
    """(direct multiplies, FFT multiplies, speed-up) for an N point DFT."""
    direct = N * N
    fft = (N / 2.0) * math.log2(N)
    return direct, fft, direct / fft


# ------------------------------------------------------------- convolution ---
def circconv(x, h, N=None):
    """Circular convolution by the definition, y[n] = sum_m x[m] h[(n-m) mod N]."""
    if N is None:
        N = max(len(x), len(h))
    xv, _ = pad(x, N)
    hv, _ = pad(h, N)
    return [sum(xv[m] * hv[(n - m) % N] for m in range(N)) for n in range(N)]


def circconv_via_dft(x, h, N=None):
    """The same thing through the DFT: IDFT(X1 . X2). This is the route the
    'find x3 if X3(k) = X1(k) X2(k)' questions are really asking for."""
    if N is None:
        N = max(len(x), len(h))
    X1, X2 = dft(x, N), dft(h, N)
    return idft([a * b for a, b in zip(X1, X2)])


def linconv(x, h):
    """Ordinary linear convolution, length len(x)+len(h)-1."""
    xv = [complex(v) for v in x]
    hv = [complex(v) for v in h]
    out = [0j] * (len(xv) + len(hv) - 1)
    for i, a in enumerate(xv):
        for j, b in enumerate(hv):
            out[i + j] += a * b
    return out


def linconv_via_circ(x, h):
    """Linear convolution done as a circular one. Returns (N, y). N must be
    at least L+M-1 or the tail wraps round and corrupts the head, which is
    exactly the point the 'zero padding' questions are testing."""
    N = len(x) + len(h) - 1
    return N, circconv(x, h, N)


def wrap_error(x, h, N):
    """How badly an N point circular convolution differs from the linear one.
    Zero when N >= L+M-1, non-zero below it: the aliasing in time."""
    lin = linconv(x, h)
    padded = lin + [0j] * max(0, N - len(lin))
    folded = [0j] * N
    for n, v in enumerate(padded):
        folded[n % N] += v
    circ = circconv(x, h, N)
    return max(abs(a - b) for a, b in zip(folded, circ)), folded


def parseval(x):
    """(sum |x[n]|^2, (1/N) sum |X[k]|^2). The two must agree."""
    N = len(x)
    X = dft(x)
    return (sum(abs(complex(v)) ** 2 for v in x),
            sum(abs(v) ** 2 for v in X) / N)


# ------------------------------------------------------------- formatting ---
def clean(v, tol=1e-9):
    """Snap floating-point dust to zero. An 8 point DFT of small integers
    produces exact integers in theory and things like -4.13e-16 in practice;
    printing that dust into the notes would be worse than useless."""
    if isinstance(v, (list, tuple)):
        return [clean(c, tol) for c in v]
    v = complex(v)
    re = 0.0 if abs(v.real) < tol else v.real
    im = 0.0 if abs(v.imag) < tol else v.imag
    return complex(re, im)


def fmt(v, nd=4):
    """One complex number, printed the way the notes print it."""
    v = clean(v)
    re, im = v.real, v.imag
    if im == 0.0:
        return "%.*g" % (nd + 1, re + 0.0)
    if re == 0.0:
        return "%sj%.*g" % ("-" if im < 0 else "", nd, abs(im))
    return "%.*g%sj%.*g" % (nd, re, "-" if im < 0 else "+", nd, abs(im))


def fmtseq(v, nd=4):
    return "{" + ", ".join(fmt(c, nd) for c in v) + "}"


# ------------------------------------------------------------- self-tests ---
def selftest():
    # --- the twiddle factors every paper needs by heart
    chk("W_4^0", W(4, 0), 1)
    chk("W_4^1", W(4, 1), -1j)
    chk("W_4^2", W(4, 2), -1)
    chk("W_4^3", W(4, 3), 1j)
    chk("W_8^1", W(8, 1), complex(1 / math.sqrt(2), -1 / math.sqrt(2)))
    chk("W_8^2", W(8, 2), -1j)
    chk("W_8^3", W(8, 3), complex(-1 / math.sqrt(2), -1 / math.sqrt(2)))
    chk("W_N^{k+N/2} = -W_N^k", W(8, 5), -W(8, 1))
    chk("W_N^{k+N} = W_N^k", W(8, 9), W(8, 1))

    # --- bit reversal
    chk("bitrev 4", bitrev(4), [0, 2, 1, 3])
    chk("bitrev 8", bitrev(8), [0, 4, 2, 6, 1, 5, 3, 7])
    chk("bitrev is an involution", [bitrev(8)[i] for i in bitrev(8)],
        list(range(8)))

    # --- DFT of the standard sequences
    chk("DFT of a delta is flat", dft([1, 0, 0, 0]), [1, 1, 1, 1])
    chk("DFT of a constant is a delta", dft([1, 1, 1, 1]), [4, 0, 0, 0])
    chk("IDFT undoes DFT", idft(dft([1, 2, 3, 4])), [1, 2, 3, 4], 1e-9)
    chk("X[0] is the sum", dft([1, 2, 3, 4])[0], 10)
    # a real sequence has a conjugate-symmetric spectrum
    Xs = dft([1, 2, 3, 3, 5, 0, 4, 6])
    chk("conjugate symmetry", [Xs[8 - k] for k in range(1, 8)],
        [Xs[k].conjugate() for k in range(1, 8)], 1e-9)

    # --- DIT and DIF must both reproduce the direct DFT, for every case
    cases = [[1, 2, 3, 4], [1, -2, 3, 2], [2, 1, 2, 1, 1, 2, 1, 2],
             [1, 1, 0, 0, 1, 1, 2, 0], [1, 2, 3, 3, 5, 0, 4, 6],
             [0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 2, 0, 1, 2, 0, 1], [1, -1, 3, 2, 1, 1, 3, -2]]
    for c in cases:
        ref = dft(c)
        chk("DIT == DFT %s" % (c[:3],), dit_stages(c)[2], ref, 1e-9)
        chk("DIF == DFT %s" % (c[:3],), dif_stages(c)[2], ref, 1e-9)
    # the stage count is log2 N, and every stage keeps the length
    st, _, _ = dit_stages([1, 2, 3, 4, 5, 6, 7, 8])
    chk("8 point DIT has 3 stages", len(st), 3)
    chk("every DIT stage has 8 entries", [len(s) for s in st], [8, 8, 8])
    st, _, _ = dif_stages([1, 2, 3, 4, 5, 6, 7, 8])
    chk("8 point DIF has 3 stages", len(st), 3)

    # the IDFT-from-FFT trick, which 72 Ash asks for by name
    chk("ifft_via_fft", ifft_via_fft(dft([1, 2, 3, 4])), [1, 2, 3, 4], 1e-9)
    chk("72 Ash IDFT", ifft_via_fft([6, -2 + 2j, -2, -2 - 2j]),
        [0, 1, 2, 3], 1e-9)

    # --- complexity, the figure the 9-paper bookwork question wants
    d, f, s = complexity(8)
    chk("N=8 direct multiplies", d, 64)
    chk("N=8 FFT multiplies", f, 12)
    chk("N=8 speed-up", s, 64 / 12.)
    chk("N=1024 direct", complexity(1024)[0], 1048576)
    chk("N=1024 FFT", complexity(1024)[1], 5120)
    chk("N=1024 speed-up", complexity(1024)[2], 204.8, 1e-9)

    # --- circular convolution, both routes, and against linear
    for x, h, N in [([1, 2, 3, 1], [4, 3, 2, 2], 4),
                    ([2, 1, 2, 1], [1, 2, 3, 4], 4),
                    ([1, 2, 1], [1, 2, 0, 1], 4),
                    ([1, -2, 5, 1, 2], [1, 2, -3, -2], 5)]:
        a = circconv(x, h, N)
        b = circconv_via_dft(x, h, N)
        chk("circconv both routes agree %s" % (x[:2],), a, b, 1e-9)
    # circular convolution is commutative
    chk("circconv commutes", circconv([1, 2, 3, 1], [4, 3, 2, 2], 4),
        circconv([4, 3, 2, 2], [1, 2, 3, 1], 4), 1e-12)
    # with enough points it IS the linear convolution
    x, h = [1, 1, 1, 1], [2, 3]
    N, y = linconv_via_circ(x, h)
    chk("linear needs L+M-1 points", N, 5)
    chk("circular at L+M-1 == linear", y, linconv(x, h), 1e-9)
    # and below that it wraps, by exactly the fold
    err, folded = wrap_error(x, h, 4)
    chk("4 point wraps the 5 point result", err, 0.0, 1e-9)
    chk("the wrap is the fold", circconv(x, h, 4), folded, 1e-9)
    chk("wrapped result differs from linear",
        1 if abs(circconv(x, h, 4)[0] - linconv(x, h)[0]) > 1e-6 else 0, 1)

    # --- Parseval
    for c in ([1, 2, 3, 4], [1, -1, 3, 2, 1, 1, 3, -2]):
        a, b = parseval(c)
        chk("Parseval %s" % (c[:2],), a, b, 1e-9)

    # --- the circular convolution property, stated in 4 papers
    x1, x2 = [1, 2, 3, 1], [4, 3, 2, 2]
    chk("DFT of a circular convolution is the product",
        dft(circconv(x1, x2, 4)),
        [a * b for a, b in zip(dft(x1, 4), dft(x2, 4))], 1e-9)


# ----------------------------------------------------------------- reports ---
FFT_PAPERS = [
    # (papers, N, kind, sequence, note)
    ("80 Bh", 8, "DIF", [2, 1, 2, 1, 1, 2, 1, 2], ""),
    ("81 Ba", 4, "DIT", [2, 2, 4], "3 entries, padded to 4"),
    ("82 Ba", 4, "DIF", [1, 4, -1], "3 entries, padded to 4"),
    ("80 Ba, 70 Ch", 8, "DIF", [1, 1, 0, 0, 1, 1, 2], "7 entries, padded to 8"),
    ("78 Bh", 8, "DIT", [1, 1, 1, 1, 0, 0, 0, 0], "u[n]-u[n-4]"),
    ("81 Bh", 8, "DIT", [1, -2, -4, 3, 0, 1], "6 entries, padded to 8"),
    ("80 Ba", 8, "DIT", [1, 1, 0, 0, 1, 1, 2], "7 entries, padded to 8"),
    ("79 Ba", 8, "DIF", [1, 2, 4, 3, 5, -1, 3], "7 entries, padded to 8"),
    ("76 Ch", 8, "DIF", [1, 2, 3, 3, 5, 0, 4, 6], ""),
    ("76 Ash", 8, "DIF", [1, 2, 3, 3, 5, 1, 4, 2], ""),
    ("82 Bh", 8, "DIT", [1, 0.5, -1, -0.5, 2, -1.5], "6 entries, padded to 8"),
    ("75 Ch", 4, "DIT", [1, -2, 3, 2], "X(3) and X(5) asked; N=4 so X(5)=X(1)"),
    ("75 Ash", 8, "DIT", [1, 2, 3, 4, 5, 6, 7, 8], "x[n]=n+1"),
    ("74 Ch", 8, "DIF", [1.5, -1, 1.8, 0.6, 3, 1.7], "6 entries; X(2), X(1) asked"),
    ("74 Ash", 8, "DIF", [0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0], ""),
    ("70 Bh", 8, "DIF", [0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0], "same as 74 Ash"),
    ("81 Ch", 8, "DIF", [-0.5, -0.5, 0.5, 0.5, 0, 0, 0, 0], ""),
    ("76 Bh", 4, "DIT", [0.5, 0.5, 0.5, 0.5], ""),
    ("70 Ma", 4, "DIT", [2, 0, 1, 2], "'4-pt DFT'"),
    ("73 Ch", 8, "DIF", [1, -1, 3, 2, 1, 1, 3, -2], ""),
    ("73 Shr", 8, "DIT", [1, -1, 2, 2, 1, 1, 2, 2], ""),
    ("72 Ch", 8, "DIT", [1, 1, 2, 4, 3, 1, 2, 1], ""),
    ("72 Ka", 8, "DIT", [1, 1, 0, 1, 0, 1, 2], "7 entries, padded to 8"),
    ("71 Ch, 70 Asa", 8, "DIT", [1, 0, 0, 0, 0, 0, 0, 0], "X(7) asked"),
    ("71 Shr, 71 Bh", 8, "DIT", [1, 1, 2, 0, 1, 2, 0, 1], "spectrum asked too"),
    ("69 Ch", 8, "DIF", [1, 1, 2, 2, 1, 1, 2, 1], ""),
    ("80 Ch, 73 Bh", 8, "DIT", [1, 0, 2, 0, -1, 1, 1], "7 entries, padded to 8"),
    ("72 Ma", 8, "DIF", [1, 0, 0, 0, -1, 1, 1], "7 entries, padded to 8"),
    ("74 Bh", 8, "DIT", [1, 1, 0, 0, 0], "5 entries, padded to 8"),
    ("73 Ma", 8, "DIT", [1, -1, 2], "3 entries, padded to 8"),
    ("74 Ma", 8, "DIT", [1, 1, 0, -1, 2], "5 entries, padded to 8"),
    ("66 Ma", 4, "DIT", [1, 3, 4, 5], ""),
    ("68 Bh", 4, "DIF", [1, -2, 2, 1], ""),
    ("69 Bh", 4, "DIT", [3.6, 5.5, 3.3, 6.3], ""),
    # the three papers that define the sequence by a formula, sampled n=0..7
    ("78 Ch", 8, "DIF", [0.5 * math.sin(n * math.pi / 6) for n in range(8)],
     "x[n] = 0.5 sin(n pi/6)"),
    ("77 Ch", 8, "DIF", [math.sin(3 * math.pi * n / 8) for n in range(8)],
     "x[n] = sin(3 pi n/8)"),
    ("75 Bh", 8, "DIF", [0.2 * n for n in range(8)],
     "x[n] = 0.2n; X(4) and X(7) asked"),
]

CIRC_PAPERS = [
    ("80 Bh, 80 Ba", [1, 2, 3, 1], [4, 3, 2, 2], 4, ""),
    ("81 Ba", [1, 2, 4, 5], [2, 1, 6, 8], 4, ""),
    ("72 Ch, 82 Bh", [1, 2, 3, 1], [1, 2, 1, -1, 1], 5, "h is 5 long, so N=5"),
    ("79 Ba", [1, -1, -2, 3, -1], [1, 2, 3], 5, ""),
    ("82 Ba", [1, 1, -1, -1, 2], [1, -1, -2], 5, ""),
    ("78 Bh, 74 Ma", [2, 1, 2, 1], [1, 2, 3, 4], 4, ""),
    ("78 Ch", [2, 1, 2, 1], [1, -2, -1, 3], 4, ""),
    ("75 Ash", [1, 2, -1, 1], [1, 3, 5, 7], 4, ""),
    ("75 Ch", [0, 0, 1, 1], [1, 1, 1, 1], 4, ""),
    ("76 Bh", [1, 0.5, 1, 0.5], [0, 1, 2, 3], 4, ""),
    ("71 Bh", [1, 2, 0, 3, 4], [2, -1, 2, -1, 2], 5, ""),
    ("67 Mng", [1, 2, 1], [1, 2, 0, 1], 4, ""),
    ("66 Ma", [1, 2], [1, 3, 4, 5], 4, ""),
    ("69 Bh", [1, 0, 1], [1, 0, 2, 1], 4, ""),
    ("71 Ch, 70 Asa, 79 Ch", [1, 2], [1, 1, 1, 1], 4, "y = u[n]-u[n-4]"),
]

PRODUCT_PAPERS = [
    ("76 Ch, 69 Ch", [1, 2, -2], [1, 2, 3, -1], 4),
    ("72 Ma", [1, 2, 3, -1], [2, 1, -3], 4),
    ("79 Bh", [1, 0, 0, 1], [2, 0, 2], 4),
    # 81 Ch, 75 Bh and 81 Bh all print the same pair of sequences. Only
    # 81 Bh states a workable N; see DEFECTIVE_PRODUCT below.
    ("81 Bh, 81 Ch, 75 Bh", [1, 3, 9, 27], [1, 2, 4, 8, 16], 5),
    ("73 Ch", [1, -2, 5, 1, 2], [1, 2, -3, -2], 5),
    ("73 Shr", [1, -2, 2, 1, 4], [2, 1, -3, -1], 5),
    ("80 Ch, 73 Bh", [1, 2, 3, -1, 5], [2, 1, -3], 5),
    ("73 Ma", [3, 2, 1, -1, -2], [1, 2, 3], 5),
    ("74 Ch", [1, 2, 0, 1, -2], [1, 0, 1, 1, 2], 5),
    ("72 Ka", [1, 2, 4], [-1, 2, 3, 1], 4),
    ("71 Shr", [1, 2, 3, 4], [1, 3, 5, 7], 4),
]

# Three papers set the identical pair x1 = 3^n (0<=n<=3), x2 = 2^n (0<=n<=4),
# and only one of them states an N that works. x2 has FIVE entries, so a
# 4-point DFT of it does not exist.
#   81 Bh  "5-point DFT of ..."                    -> fine, N = 5
#   81 Ch  "4-point DFT of ..."                    -> IMPOSSIBLE as printed
#   75 Bh  "DFT of sequence ..." with NO N at all  -> N is unstated, and the
#          only self-consistent choice is 5, exactly as 81 Bh spells out
# The Sorted PYQ Detailed document groups 75 Bh with 81 Ch under a "4-pt"
# heading. That heading is an inference, and it is the wrong one.
DEFECTIVE_PRODUCT = [
    ("81 Ch", [1, 3, 9, 27], [1, 2, 4, 8, 16], 4,
     "prints '4-point' for a 5 entry x2: no such DFT exists"),
    ("75 Bh", [1, 3, 9, 27], [1, 2, 4, 8, 16], None,
     "states no N; the Detailed document's '4-pt' heading is an inference"),
]

LINEAR_PAPERS = [
    ("74 Ch", [1, 1, 1, 1], [2, 3]),
    ("74 Bh", [-1, 1], [2, 3, 1, -2]),
    ("72 Ash", [1, 1, 1], [2, 2, 2]),
    ("77 Ch", [1, 1, 1], [1, 0, -3]),
]


def report():
    print("=" * 78)
    print("FFT COMPUTATIONS   (%d paper entries)" % len(FFT_PAPERS))
    print("=" * 78)
    for name, N, kind, x, note in FFT_PAPERS:
        X = dft(x, N)
        print("%-16s %d-pt %-3s  x = %s%s" %
              (name, N, kind, fmtseq(x, 3), ("   [" + note + "]") if note else ""))
        print("%-16s   X(k) = %s" % ("", fmtseq(X)))
    print()
    print("=" * 78)
    print("CIRCULAR CONVOLUTION   (%d paper entries)" % len(CIRC_PAPERS))
    print("=" * 78)
    for name, x, h, N, note in CIRC_PAPERS:
        y = circconv(x, h, N)
        print("%-22s N=%d  x=%s  h=%s%s" %
              (name, N, fmtseq(x, 3), fmtseq(h, 3),
               ("  [" + note + "]") if note else ""))
        print("%-22s   y = %s" % ("", fmtseq(y, 3)))
    print()
    print("=" * 78)
    print("x3 = IDFT(X1 . X2)   (%d paper entries)" % len(PRODUCT_PAPERS))
    print("=" * 78)
    for name, x1, x2, N in PRODUCT_PAPERS:
        y = circconv_via_dft(x1, x2, N)
        print("%-18s N=%d  x1=%s  x2=%s" % (name, N, fmtseq(x1, 3), fmtseq(x2, 3)))
        print("%-18s   x3 = %s" % ("", fmtseq(y, 3)))
    print()
    print("-" * 78)
    print("DEFECTIVE: a 4 point DFT is asked of a 5 entry sequence")
    for name, x1, x2, N, why in DEFECTIVE_PRODUCT:
        print("%-8s x1=%s (%d) x2=%s (%d)" %
              (name, fmtseq(x1, 3), len(x1), fmtseq(x2, 3), len(x2)))
        print("%-8s   %s" % ("", why))
        if N:
            try:
                circconv_via_dft(x1, x2, N)
                print("%-8s   !! expected this to be rejected" % "")
            except ValueError as e:
                print("%-8s   as printed: %s" % ("", e))
        print("%-8s   at N=5, as 81 Bh states: x3 = %s"
              % ("", fmtseq(circconv_via_dft(x1, x2, 5), 3)))
    print()
    print("=" * 78)
    print("LINEAR CONVOLUTION VIA CIRCULAR")
    print("=" * 78)
    for name, x, h in LINEAR_PAPERS:
        N, y = linconv_via_circ(x, h)
        print("%-10s x=%s h=%s -> N=%d   y = %s"
              % (name, fmtseq(x, 3), fmtseq(h, 3), N, fmtseq(y, 3)))
    print()
    print("=" * 78)
    print("COMPLEXITY")
    print("=" * 78)
    print("%8s %14s %14s %10s" % ("N", "direct N^2", "FFT (N/2)log2N", "speed-up"))
    for N in (8, 16, 32, 64, 256, 1024):
        d, f, s = complexity(N)
        print("%8d %14d %14g %10.4g" % (N, d, f, s))


if __name__ == "__main__":
    selftest()
    if FAIL:
        print("SELF-TEST FAILURES (%d of %d)" % (len(FAIL), len(FAIL) + OK[0]))
        for f in FAIL:
            print("  " + f)
        raise SystemExit(1)
    print("dft.py self-tests: %d/%d pass\n" % (OK[0], OK[0]))
    report()
