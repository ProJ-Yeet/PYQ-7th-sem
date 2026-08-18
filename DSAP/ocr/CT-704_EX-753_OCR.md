# DSAP / DSP — OCR archive

Full verbatim transcription of the scanned question papers used by the
DSAP sorted-PYQ documents.

Sources
-------
* `D:\College\PYQ\New PYQ\DSAP.pdf` — 47 pp.
  pp. 1–30  = **CT704** *Digital Signal Analysis and Processing* (BEI/BCT)
  pp. 31–47 = **EX753** *Digital Signal Processing* (BEX)
  (`New PYQ\4.1bei_dsap.pdf` is byte-identical to pp. 1–30 of the above.)
* `D:\College\PYQ\DSAP\CT-704_69-81.pdf` — 22 pp, the older CT704 scan.
  Used for the six papers that the new file does not contain.

Transcription rules
-------------------
* Verbatim, including the papers' own typos and OCR-visible spelling
  ("Drichlet's", "Billinear Tranformation", "Gibb's", "covert").
* Marks are given exactly as printed, in [square brackets].
* Where the scan is cut off or genuinely omits data, an
  `> NOTE:` line records it. Nothing is silently invented.

Page-order table — New PYQ\DSAP.pdf, CT704 section
--------------------------------------------------
| p  | Year / month  | Exam    | Programme | Code  |
|----|---------------|---------|-----------|-------|
| 1  | 2082 Bhadra   | Regular | BEI, BCT  | CT704 |
| 2  | *(blank)*     |         |           |       |
| 3  | 2081 Bhadra   | Regular | BCT, BEI  | CT704 |
| 4  | 2081 Baishakh | Back    | BEI, BCT  | CT704 |
| 5  | 2080 Bhadra   | Regular | BEI, BCT  | CT704 |
| 6  | 2080 Baishakh | Back    | BEI, BCT  | CT704 |
| 7  | 2079 Bhadra   | Regular | BEI, BCT  | CT704 |
| 8  | 2078 Bhadra   | Regular | BCT       | CT704 |
| 9  | *(blank)*     |         |           |       |
| 10 | 2078 Bhadra   | Regular | BCT       | CT704 | ← duplicate scan of p8
| 11 | 2076 Chaitra  | Regular | BCT       | CT704 |
| 12 | 2076 Ashwin   | Back    | BCT       | CT704 |
| 13 | 2075 Chaitra  | Regular | BCT       | CT704 |
| 14 | 2075 Ashwin   | Back    | BCT       | CT704 |
| 15 | 2074 Chaitra  | Regular | BCT       | CT704 |
| 16 | 2074 Ashwin   | Back    | BCT       | CT704 |
| 17 | 2073 Shrawan  | Back    | BCT       | CT704 |
| 18 | 2072 Chaitra  | Regular | BCT       | CT704 |
| 19 | 2072 Kartik   | Back    | BCT       | CT704 |
| 20 | 2071 Chaitra  | Regular | BCT       | CT704 |
| 21 | 2071 Shrawan  | Back    | BCT       | CT704 |
| 22 | 2070 Chaitra  | Regular | BCT       | CT704 |
| 23 | 2069 Bhadra   | Regular | BCT       | CT704 |
| 24 | 2068 Bhadra   | Regular | BCT       | CT704 |
| 25 | (cont.)       |         |           |       |
| 26 | 2069 Chaitra  | Regular | BCT       | CT704 |
| 27 | 2067 Mangsir  | Regular | BCT       | CT704 |
| 28 | (cont.)       |         |           |       |
| 29 | 2066 Magh     |         | BCT       | CT704 |
| 30 | (cont.)       |         |           |       |

> The pp. 15–21 and 24–30 rows are provisional until each page is read;
> they are corrected in place as the transcription below is written.

=======================================================================
# CT704 — Digital Signal Analysis and Processing
=======================================================================

## p1 — 2082 Bhadra, Regular, BE, BEI/BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Compare between energy signal and power signal. Determine whether the
   signal x[n] = e^{j(πn/2 + 4π/7)} is energy signal or power signal. [2+2]
2. Find the output of an LTI system whose impulse response is given by
   0.5^n{u[n]-u[n-3]} and input is given by {2,1,0.5,-1}. [5]
3. Define z-transform for a discrete time signal. Find the inverse
   z-transform for H(z) = z / (3z² - 4z + 1) using partial fraction
   method for 1/3 < |z| < 1. [1+5]
4. Draw the poles and zeros in the z-plane for the system with poles at
   0.45 ± j1.6 and zeros at 0.58 ± j2.06. Also plot the magnitude
   response (not in scale) of the system. [2+8]
5. Obtain the direct form I and direct form II realization of the
   following system:
   y[n] − 0.75y[n − 1] − 0.25y[n − 2] = x[n] + 0.5x[n − 1] [2+2]
6. Compute Lattice ladder coefficients and draw lattice structure for the
   given system
   H(z) = (2 − 0.7z⁻¹ + 0.5z⁻²) / (1 − 0.3z⁻¹ + 0.25z⁻²) [6]
7. Design a linear phase FIR system to meet the following specifications: [10]
   Passband edge = 2 kHz          Stopband edge = 5 kHz
   Stopband attenuation = 42 dB   Sampling frequency = 20 kHz
8. What is an optimal filter? Explain Remez exchange algorithm for FIR
   filter design with the help of a flow chart. [1+4]
9. Explain frequency warping effect in detail. The passband and stopband
   frequencies are 350Hz and 1,000Hz respectively. The attenuation at
   passband and stopband are -3dB and -10dB respectively. The sampling
   frequency is 5,000Hz. Design a digital low-pass Butterworth filter
   using bilinear transformation technique. [3+12]
10. Compute the circular convolution of the following sequences: [7]
    h(n) = {1, 2, 1, −1, 1}   and   x(n) = {1, 2, 3, 1}
11. Find 8-point DFT using DIF-FFT of the sequence
    x[n] = {1, 1/2, −1, −1/2, 2, −3/2}. [8]

## p3 — 2081 Bhadra, Regular, BE, BCT/BEI, IV/I, CT 704 [80 marks, 3 hrs]

1. Determine if the signal x[n] = cos(2πn/5) + sin(πn/3) is periodic or
   not. If the signal is periodic, find its fundamental period. [4]
2. Find the output of an LTI System with impulse response
   h[n] = 2δ[n+1] + 2δ[n-1] when an input of
   x[n] = δ[n] + 2δ[n-1] − δ[n-3] is applied to it. [5]
3. Define ROC of z-transform. Find the inverse z-transform using partial
   fraction expansion of
   X(z) = (2z³ − 5z² + z + 3) / ((z−1)(z−2))  for ROC |z| < 1 [1+5]
4. Plot the pole – zero in z plane and draw magnitude response (not to
   the scale) of the system described by difference equation
   y[n] – 0.4 y[n-1] + 0.25 y[n-2] = x[n] - 0.4 x[n-1] [3+7]
5. Compute the lattice and ladder coefficients and draw lattice-ladder
   structure for the given IIR system
   H(z) = (1 + z⁻¹ + z⁻²) / ((1 + 0.5z⁻¹)(1 + 0.3z⁻¹)(1 + 0.4z⁻¹)) [6+4]
6. Design a low pass FIR filter using suitable window to meet following
   specifications: [8]
   0.99 ≤ |H(e^{jw})| ≤ 1.01  for 0 ≤ |w| ≤ 0.3π
   |H(e^{jw})| ≤ 0.01         for 0.35π ≤ |w| ≤ π
7. What do you mean by optimum filter? Describe the Remez exchange
   algorithm for FIR filter design along with the flowchart. [1+6]
8. Design a digital low pass IIR filter using Bilinear transformation to
   meet following specifications: [12+3]
   0.9 ≤ |H(e^{jw})| ≤ 1  for 0 ≤ |w| ≤ π/2
   |H(e^{jw})| ≤ 0.2      for 3π/4 ≤ |w| ≤ π
   Use Butterworth approximation for design with sampling frequency of
   1Hz. Compare Impulse Invariance Method and Bilinear Transformation
   method.
9. How does FFT reduce computational complexity compared to direct
   calculation of DFT? Compute 8-point DFT of x[n] = {1, −2, −4, 3, 0, 1}
   using DIT-FFT algorithm. [2+7]
10. If X₁(k) and X₂(k) are the 5-point DFT of x₁(n) = 3ⁿ 0≤n ≤3 and
    x₂(n) = 2ⁿ 0≤n ≤4. Find x₃(n) if X₃(k) = X₁(k)X₂(k) [6]

## p4 — 2081 Baishakh, Back, BE, BEI/BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. A discrete-time LTI system is given by difference equation
   y(n) = x(n) + e^a y(n − 1). Check this system for BIBO stability. [5]
2. Find the output y(n) of LTI system having impulse response
   h(n) = (1/3)ⁿ u(n - 3) and input x(n) = (1/6)^{n−6} u(n). [6]
3. Determine the inverse z-transform of
   X(z) = 1 / (1 − 0.8z⁻¹ + 0.12z⁻²).
   (i) if ROC is |z| > 0.6  (ii) if ROC is |z| < 0.2
   (iii) if ROC is 0.2 < |z| < 0.6 [2+2+3]
4. Plot the pole-zero in z plane and draw the magnitude response (not to
   the scale) of the system described by difference equation
   y(n) = 0.67 x(n) – 0.3 x(n-1) + 2.75 y (n-1) [3+7]
5. a) Draw the cascaded form structure of
      H(z) = 10(1-0.25z⁻¹)(1-0.667z⁻¹)(1+2z⁻¹) /
             (1-0.75z⁻¹)(1-0.125z⁻¹){1-(0.5+j0.5)z⁻¹}{1-(0.5-j0.5)z⁻¹} [5]
   b) Draw the lattice structure for the given FIR filter and also check
      whether the system is stable.
      H(z) = 1 + (13/24) z⁻¹ + (5/8)z⁻² + (1/3)z⁻³ [5]
6. Design a linear phase FIR filter using suitable window to meet
   following specifications:
   0.99 ≤ |H(e^{jw})| ≤ 1.01,  for 0 ≤ |w| ≤ 0.3π
   |H(e^{jw})| ≤ 0.01, for 0.35π ≤ |w| ≤ π [10]
7. What is Gibbs phenomenon and how can it be minimized? Why Kaiser
   window is better than other fixed windows in FIR filter design? [3+3]
8. Differentiate between bilinear transformation and impulse invariance.
   Design a Butterworth digital IIR lowpass filter using bilinear
   transformation by taking T = 0.1 second, to satisfy the following
   specifications. [2+10]
   0.6 ≤ |H(e^{jω})| ≤ 1,  0 ≤ ω ≤ 0.35π
   |H(e^{jω})| ≤ 0.1,      0.7π ≤ ω ≤ π
9. Why Decimation in Time Fast Fourier Transform (DITFFT) Algorithm is
   better than direct computation of DFT? Find 4 point DFT of the
   sequence x(n) = {2,2,4} using DITFFT algorithm. [2+6]
10. Compute circular convolution of the following two sequences using
    DFT. x(n) = {1,2,4,5} and h (n) = {2,1,6,8} [6]

## p5 — 2080 Bhadra, Regular, BE, BEI/BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. A discrete time system has input x(n) and output y(n). The input
   output relation of the system is given by
   y(n) = Σ_{k=0}^{n} x(k)
   Check whether the system is memory less, time invariant and stable or
   not? [2+2+2]
2. Determine whether the given signal is periodic or not. If the signal
   is periodic, determine the fundamental period
   x[n] = e^{jπn/16} cos(nπ/17). [5]
3. Define the Region of Convergence (ROC) [1+6]
   Find the inverse of H(z) = (1 + 2z⁻¹ + z⁻²)/(1 - 0.75z⁻¹ + 0.125z⁻²);
   ROC 0.25 < |z| < 0.5
4. Plot the pole-zero on the z-plane and draw Magnitude response (not to
   the scale) of an LTI system described by the equation,
   y(n) = x(n) + 0.8x(n -1) + 0.8x(n − 2) + 0.49 y(n− 2). [3+7]
5. Draw the Lattice structure from the following system function.
   H(z) = 1 / (1 - 0.2z⁻¹ + 0.4z⁻² + 0.6z⁻³) [10]
6. Design the symmetric FIR Low Pass Filter (LPF) for which the desired
   frequency response is expressed as [10]
   H_d(W) = e^{-jWτ}, |W| ≤ Wc and 0 elsewhere. The length of the filter
   should be 7 and Wc = 1 rad/sample. Make use of the Hanning window.
7. Kaiser window is to be used to design a linear phase FIR filter that
   meets following specification [2+2+2]
   |H(e^{jω})| ≤ 0.01,        0.21π ≤ |ω| ≤ π
   0.95 ≤ |H(e^{jω})| ≤ 1.05, 0 ≤ |ω| ≤ 0.19π.
   Calculate the optimum value of ripple, attenuation and window length.
8. Using Bilinear transformation, design a Butterworth low pass filter
   which satisfies following conditions: [12]
   0.9 ≤ |H(e^{jw})| ≤ 1,  for 0 ≤ w ≤ π/2
   |H(e^{jw})| 0.2,        for 3π/4 ≤ w ≤ π
   Consider sampling frequency of 1 Hz.
9. Compute 8-point DIF-FFT of sequence x(n) = {2, 1, 2, 1, 1, 2, 1, 2}. [8]
10. Obtain the circular convolution of the following sequences:
    x₁(n) = {1, 2, 3, 1} and x₂(n) = {4, 3, 2, 2} [6]

> NOTE: Q8's second line is printed as "|H(e^{jw})| 0.2" — the ≤ sign is
> missing in the paper.

## p6 — 2080 Baishakh, Back, BE, BEI/BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Check whether following signals are periodic or not. If yes, state
   their periodic time. [2+2]
   a) x[n] = Sin(nπ) + Cos (nπ)
   b) x[n] = Sin(3nπ/5) + Cos (4nπ/7)
2. Find the output of LTI system having impulse response
   h[n] = (1/2)ⁿ* u[n] and input x[n] = 5e^{jπn/3} for -∞ < n < ∞. [5]
3. Define ROC. Find inverse z-transform of
   X(z) = (1+2z⁻¹+z⁻²)/(1-1.5z⁻¹+0.5z⁻²), ROC : |z| > 1. [1+5]
4. Differentiate between FIR system and IIR System. The poles of a system
   are located at 0.45 ± j1.6 and zeros at 0.58 ± j2.06. Map the poles
   and zeros in the z-plane and plot the magnitude response (not in
   scale) of the system. [4+6]
5. Compute Lattice-ladder coefficients and draw lattice structure for
   given system
   H (z) = (2 – 0.7z⁻¹ + 0.5z⁻²)/(1-0.3z⁻¹ + 0.25z⁻²). [6]
6. Realize the given system in Cascade Form of 2nd order section flow
   graph representation.
   H (z) = {(1-0.4 z⁻¹) (1+0.2 z⁻¹) (1-0.3e^{jπ/6} z⁻¹) (1-0.3e^{-jπ/6} z⁻¹)} /
           {(1-0.5e^{jπ/3} z⁻¹) (1-0.5e^{-jπ/3} z⁻¹) (1+0.7e^{jπ/4} z⁻¹)
            (1+0.7e^{-jπ/4} z⁻¹)}. [4]
7. In which case do we choose FIR filter and IIR filter? Design a linear
   phase FIR filter using Kaiser Window to meet the following
   specifications: [2+8]
   0.99 ≤ |H(e^{jw})| ≤ 1.01   for 0 ≤ w ≥ 0.016π
   |H(e^{jw})| ≤ 0.01          for 0.08π ≤ w ≤ 2π
8. Explain in detail about how Gibb's oscillation arise while using the
   rectangular window in FIR filter design. [5]
9. Design a low pass digital IIR filter by Billinear Tranformation method
   to an approximate Butterworth low pass filter, if passband edge
   frequency is 0.26 π radians and maximum deviation of 0.99 dB below
   0 dB gain in the passband. The maximum gain of -14.99 dB and frequency
   is 0.58π radians in stopband, Consider sampling frequency 0.5 Hz. [11]
10. Describe digital domain Spectral Transformation features and
    parameters for low pass to high pass in IIR Filter design. [4]
11. How fast is FFT? Find 8-point DFT of sequence
    x[n] = {1,1, 0, 0,1,1,2} using Decimation in Time Fast Fourier
    Transform(DITFFT) algorithm. [2+6]
12. Write the complexity of DFT and FFT? Obtain the circular convolution
    of the following sequences: [2+5]
    X₁[n] = {1, 2, 3, 1} and
    X₂[n] = {4, 3, 2, 2}

> NOTE: Q7's first specification is printed "for 0 ≤ w ≥ 0.016π" — the
> second inequality is reversed in the paper.
> NOTE: Q11's sequence is printed with 7 entries for an 8-point DFT.

## p7 — 2079 Bhadra, Regular, BE, BEI/BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Define energy and power signal. Determine whether the signal
   x[n] = cos[2πn/5] + sin[πn/3] is periodic or non-periodic and if it is
   periodic, find its fundamental period. [2+2]
2. Find the output of LTI system having input signal
   x[n] = δ[n] + 2δ[n-1] - δ[n-3] and h[n] = 2δ[n+1] + 2δ[n-1]. [5]
3. Find inverses Z-transform of X(z) = (2z⁴+2z³-3z+2)/(z²-1.5z-1),
   ROC: |z| < 0.5, using partial fraction expansion method. [6]
4. Plot the pole-zero in z-plane and draw the magnitude response (not to
   the scale) of the equation of the system describe by difference
   equation:
   y [n] - 0.35y [n-1] + 0.25 y [n-2] = x [n] -0.75 x [n-1]. [3+7]
5. Draw direct form I and Direct form II realization of the following
   system.
   y [n] – 0.25 y[n-2] + x [n] + 0.4x [n-1] + 0.5x [n-2] [2+2]
6. Given a 3-stage lattice filter for all zero polynomial with
   coefficients K₁ = 1/4, K₂ = 1/2 and K₃ = 1/3. Obtain the system
   function and FIR filter coefficients of this filter. [6]
7. Define Gibb's phenomenon. Design the FIR filter using Kaiser window
   technique for the specifications: [2+8]
   0.899 ≤ |H(e^{jw})| ≤ 1   for |w| ≤ 0.2π
   |H(e^{jw})| ≤ 0.01        for 0.4π ≤ w ≤ π
8. Discuss the Remez exchange algorithm for FIR filter design. [5]
9. Design a low pass discrete time Butterworth filter using bilinear
   transformation having following specifications: [11+4]
   Passband frequency (W_p) = 0.25π radians
   Stopband frequency (W_s) = 0.55π radians
   Passband ripple (δ_P) = 0.11
   Stopband ripple (δ_S) = 0.21. Consider sampling frequency of 0.5 Hz.
   Also, covert the obtained digital low pass filter to high pass filter
   with new pass band frequency, W'_P = 0.45π using digital domain
   transformation.
10. Why we need FFT? Find the 8-point DFT of the following sequence using
    radix-2 DITFFT algorithm. [2+6]
11. If X₁ (k) and X₂ (k) are DFT of sequence x₁[n] = {1, 0, 0, 1} and
    x₂[n] = {2, 0, 2} respectively then find the sequence X₃[n]; if DFT
    of x₃[n] is given by X₃ (k) = X₁ (k). X₂ (k) [7]

> NOTE: Q10 says "the following sequence" but NO sequence is printed on
> this page of the scan. Checked against the older CT-704_69-81.pdf copy
> of the same paper — see that entry below.

## p8 / p10 — 2078 Bhadra, Regular, BE, BCT, IV/I, CT 704 [80 marks, 3 hrs]

> p8 and p10 are two scans of the SAME paper (p9 is blank). Transcribed once.

1. Determine whether the signal x[n] = cos[πn/2] . cos[πn/4] is periodic
   or non periodic and if it is periodic, find its fundamental period. [4]
2. Find the output of LTI system having impulse response
   h[n] = u[n] – u[n-4] and input signal x[n] = (1/2)ⁿ u[n]. [5]
3. Define ROC. Find inverse z-transform of
   X(z) = (z³ + z² + 1.5z + 0.5)/(z³ + 1.5z² + 0.5z), ROC : |z| < ½. [1+5]
4. Determine the zero-input response for a second order system given by: [4]
   y[n] - 3y[n-1] - 4y[n-2] = x[n]
5. Plot the pole-zero in z-plane and draw magnitude response (not to the
   scale) of the system described by difference equation. [2+4]
   y[n] – 0.4 y[n-1] + 0.25 y [n-2] = x[n] - 0.4x[n-1]
6. The system function of a filter is
   H(z) = 1 + (13/24)z⁻¹ + (5/8)z⁻² + (1/3)z⁻³. Draw the Direct Form and
   Lattice Structure implementation of the above filter. [3+7]
7. Design a linear phase FIR filter using KAISER window to meet the
   following specifications: [8]
   |H(e^{jw})| ≤ 0.01;         0 ≤ |w| ≤ 0.25π
   0.95 ≤ |H(e^{jw})| ≤ 1.05;  0.35π ≤ |w| ≤ 0.6π
   |H(e^{jw})| ≤ 0.01;         0.65π ≤ |w| ≤ π
8. What is optimum filter? Show mathematical expression of Remez exchange
   algorithm for FIR filter design. [1+6]
9. Design a LPF Butterworth filter using Impulse Invariance Method (IIM)
   method with passband and stopband frequencies 200Hz and 500Hz
   respectively. The passband and stopband attenuations are 5dB and 12dB
   respectively. The sampling frequency is 5000Hz. What is pre-warping
   and why it is necessary? Explain. [12+3]
10. Differentiate between DFT and DTFT. Find the circular convolution of
    x₁[n]={2, 1, 2, 1} and x₂[n] = {1, 2, 3, 4} [2+6]
11. Find the 8 – point DFT of x[n] = u[n] – u[n-4] using FFT DIT
    algorithm. [7]

## p11 — 2076 Chaitra, Regular, BE, BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Define even and odd type discrete time signals with suitable example.
   Plot the signal x[-2n+3] where x[n] = {1, 2, 0, -1, -3, -4}. [2+3]
2. Determine whether the following system are: [5]
   a) y[n] = x[-n] is time-invariant or not.
   b) y[n] = x[n²] is linear or not.
3. Find the output of LTI system having input signal x[n] = u[n+1]-u[n-4]
   and impulse response h[n] = (1/2)ⁿ u[n-1]. [6]
4. Define ROC of z-transform. Find inverse z-transform using partial
   fraction expansion of
   X(z) = (z⁴ + 5z³ - 3z + 4)/ (z² - 1.5z - 1), ROC: |z| < 0.5. [2+6]
5. Draw the pole-zero in the z-plane for a system with poles at
   0.45 ± j1.06 and zeroes at 0.58±j2.06. Also plot the magnitude
   response (not to the scale) of the system. [2+6]
6. Compute Lattice and Ladder coefficients and Draw lattice-ladder
   structure for given IIR system
   H(z) = (0.5 - 2z⁻¹ + 3z⁻²)/(1- 0.5z⁻¹ - 0.7z⁻² + 0.3z⁻³). [6+4]
7. Realize the given system in Cascade form of 2nd order section in
   signal flow graph representation. [4]
   H(z) = {( 1 – 0.5z⁻¹)(1 + 0.35z⁻¹)(1 – 0.3e^{j2nπ/5}z⁻¹)(1 – 0.3e^{-j2nπ/5}z⁻¹)} /
          {(1 – 0.6e^{jnπ/3}z⁻¹)(1-0.6e^{-jnπ/3}z⁻¹)(1+0.5e^{j2nπ/7}z⁻¹)(1+0.5e^{-j2nπ/7}z⁻¹)}
8. Design the FIR filter using suitable window for the specifications: [6]
   0.899 ≤ |H(e^{jω})| ≤ 1,  for |ω| ≤ 0.2π
   |H(e^{jω})| ≤ 0.01, for 0.4π ≤ ω ≤ π
9. What is optimum filter? Show mathematical expression of Remez exchange
   algorithm for FIR filter design. [1+5]
10. Design a digital low pass Butterworth filter by applying bilinear
    transformation techniques for the given specifications: [10]
    Passband peak to peak ripple ≤ 1dB
    Passband edge frequency = 1.2KHz
    Stopband Attenuation ≥ 40dB
    Stopband edge frequency = 2.5 KHz
    Sample rate = 8KHz
11. Find 8-point DFT of sequence x[n] = {1, 2, 3, 3, 5, 0, 4, 6} using
    Decimation in frequency Fast Fourier Transform (DIFFFT) algorithm. [7]
12. Find x₃[n] if DFT of x₃[n] is given by X₃(k) = X₁(k) * X₂(k) where
    X₁(k) and X₂(k) are 4-point DFT of x₁[n]={1, 2, -2} and
    x₂[n] = {1, 2, 3, -1} respectively. [5]

## p12 — 2076 Ashwin, Back, BE, BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Explain Fourier transform multiplication property for two sequences.
   Write Drichlet's conditions for Fourier series. [4+3]
2. Find convolution between two signals x[n] = 2ⁿ4[−n], 0 < a < 1 and
   h[n] = 4[n] [6]
3. State Convolution property of Z-transform. Find inverse Z-transform of
   X(z) = z / {(z − 0.6)(z + 0.5)²}, ROC: |z| > 0.6 [3+6]
4. Describe stability and causality characteristics of LTI system in
   terms of Impulse Response and ROC of its transfer function with
   suitable examples. [4+3]
5. Compute Lattice and Ladder coefficients and Draw lattice-ladder
   structure for given IIR system
   H(z) = (0.7 – 1.5z⁻¹ + 0.5z⁻²) / (1 – 0.5z⁻¹ – 0.7z⁻² + 0.3z⁻³) [6+3]
6. For the system described by the following difference equation: [2+8]
   y[n] = 0.67x[n] − 0.3x[n − 1] + 2.75y[n − 1]
   Map the poles and zero in the z-plane and plot the phase response of
   the system.
7. Design a low pass discrete IIR filter by Bilinear Transformation
   method to an approximate Butterworth filter having specifications as
   below: [12]
   Pass bandedge frequency (ω_p) = 0.22 π radians
   Stop bandedge frequency (ω_s) = 0.54 π radians
   Passband ripple (δ_p) = 0.11
   Stopband ripple (δ_s) = 0.22,  Consider sampling frequency 0.5 Hz.
8. Why we need DFT? Find 8-point DFT of sequence
   x[n] = {1, 2, 3, 3, 5, 1, 4, 2} using Decimation in frequency Fast
   Fourier Transform (DIFFFT) algorithm. [2+8]
9. In which case do we choose FIR filter and IIR filter? Design a Kaiser
   Window to meet the following specifications. [2+4+4]
   0.99 ≤ |H(e^{jw})| ≤ 1.01,  for 0 ≤ w ≤ 0.16π
   |H(e^{jw})| ≤ 0.01,         for 0.18π ≤ w ≤ 2π
   Draw the flow chart for Remez- Exchange algorithm

> NOTE: Q2 is printed exactly as shown; "2ⁿ4[−n]" and "4[n]" are almost
> certainly "aⁿ u[−n]" and "u[n]" mangled in reproduction — the "0 < a < 1"
> condition confirms the intended base is `a`. Recorded as printed.

## p13 — 2075 Chaitra, Regular / Back, BE, BCT, IV/I, CT 704 [80 marks, 3 hrs]

1. Define Power and Energy type discrete time signal with suitable
   example. Differentiate between Fourier Series and Fourier Transform. [3+4]
2. Find the output of LTI system having impulse response h[n] with
   h[-2] = 3, h[0] = 2, h[1] = 1 and input signal x[n] = (2)ⁿ,
   for -1 ≤ n ≤3. Also check the answer. [5+2]
3. Plot the pole-zero in z-plane and draw magnitude response (not to
   scale) of the system described by differential equation
   y(n) − 0.3y(n−1) = 2x(n−2) + 0.7x(n−1) + 4x(n) [2+7]
4. Draw the lattice structure from the following system function
   H(t) = 1 / (1 + (2/3)z⁻¹ + (5/8)z⁻² + (2/3)z⁻³ + z⁻⁴) [9]
5. What is optimum filter? Show mathematical expression of Remez exchange
   algorithm for FIR filter design. [2+6]
6. List out the properties of Region of convergence and locate the ROC of
   the following signal
   x[n] = (0.1)ⁿ u[n] + (0.3)ⁿ u[−n−1] [4+6]
7. Using bilinear transformation, design a digital filter using
   Butterworth approximation which satisfies the following conditions
   0.8 ≤ | He^{JW} | ≤1 for 0 ≤ W ≤ 0.2Π
   | He^{JW} | ≤ 0.2 for 0.6Π ≤ W ≤ Π [10]
8. How fast is FFT? Find X(3) and X(5) for given sequence
   x[n] = {1, -2, 3, 2} using DITFFT algorithm. [2+8]
9. Differentiate between linear convolution and circular convolution
   compute circular convolution of signals
   X₁[n] = {0, 0, 1, 1} and X₂[n] = {1, 1, 1, 1} [3+7]

> NOTE: the Exam. cell prints "Regular / Back" in one box. Treated as
> Regular (same convention as the Data Mining 2075 Chaitra paper).
> NOTE: Q4 prints "H(t)" where "H(z)" is meant.

## p14 — 2075 Ashwin, Back, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Determine whether the following sequences are linear or not: [3+3]
   a) y[n] = x²[n]
   b) y[n] = cos((5π/8)n + π/4)
2. Find the output of LTI system having impulse response
   h[n] = 2ⁿ * {u[n] − u[n − 3]} and input signal
   x[n] = δ[n] + δ[n − 1] + δ[n − 2]. [5]
3. List out the properties of Region of convergence and locate the ROC of
   the following signal. [3+6]
   x[n] = (0.6)ⁿ u[n] + (0.25)ⁿ u[n]
4. Draw the poles and zeros in the z-plane for a system with poles at
   0.45±j1.06 and zeros at 0.58±j2.06. Also plot the magnitude response
   of the system. [2+8]
5. Draw the Lattice structure from the following system function: [7+3]
   1 / (3 + (39/24)Z⁻¹ + (15/8)Z⁻² + (3/9)Z⁻³)
   And represent 5/8 and −5/8 in sign magnitude, 1's complement and 2's
   complement format.
6. Design a digital low-pass filter with the following specification: [12]
   i) Pass-band magnitude constant to 0.7 dB below the frequency of 0.15 π
   ii) Stop-band attenuation at least 14 dB for the frequencies between
       0.6π to π
   Use Butterworth approximation as a prototype and use bilinear
   transformation method to obtain the digital filter.
7. Design a linear phase FIR filter using Kaiser Window to meet the
   following specifications: [8+4]
   0.99 ≤ |H(e^{jw})| ≤ 1.01,  for 0 ≤ w ≤ 0.19π
   |H(e^{jw})| ≤ 0.01,         for 0.21π ≤ w ≤ π
   Draw the flow chart for Optimum filter design.
8. How fast is FFT compare to DFT? Draw the butterfly diagram of 8-point
   DFT of a sequence as x[n] = n + 1 using Decimation in Time FFT
   algorithm. [3+7]
9. State the circular convolution property of DFT. Find the circular
   convolution of: [1+5]
   x₁(n) = {1, 2, -1, 1} and x₂(n) = {1, 3, 5, 7}

> NOTE: Q9's two sequences sit on the very last line of the scan and are
> partly clipped by the page edge; read at Matrix(4.5,4.5) as
> "{1,2,-1,1}" and "{1,3,5,7}".

## p15 — 2074 Chaitra, Regular, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Plot the sequence x[n] = u[n] − u[n − 3] + 5δ[n − 4] = nu[n − 6].
   List out the properties of LTI system. [3+2]
2. Determine whether the following system are: [3+3]
   a) y[n] = y[n − 4] + x[n − 4] is Time-invariant or not
   b) y[n] = x²[n] is Linear or Nor-linear
3. Define a ROC. What are the properties of ROC of z-transform? Find the
   inverse Z-transform of X(z) = (2z² + 2z² + 3z + 5)/(z² − 0.1z − 0.2),
   ROC : |z| < 0.4. [1+3+5]
4. The poles of a system are located at: 0.45-0.77i and -2±0.3i. Map the
   poles and zero in the z-plane and plot the magnitude response of the
   system. [2+8]
5. Obtain the Direct Form I and Direct Form II realization of the
   following system. [5]
   3y[n] + y[n − 1] + 2y[n − 4] = 2x[n] + x[n − 3]
6. Determine the lattice coefficients coefficients corresponding to the
   FIR filter with the system function: [5]
   H(z) = A₃(z) = 1 + (52/96)z⁻¹ + (25/40)z⁻² + (1/3)z⁻³
7. Design a digital low-pass filter with the following specification: [12]
   i) Pass-band magnitude constant to 0.7 dB below the frequency of 0.15π
   ii) Stop-band attenuation at least 14 dB for the frequencies between
       0.6π to π
       Use Butter worth approximation as a prototype and use impulse
       invariance method to obtain the digital filter.
8. Design a FIR linear phase filter using Kaiser window that meets the
   following specifications: [9+3]
   |H(e^{jw})| ≤0.01, 0≤ |w| ≤ 0.25π
   0.95≤ |H(ejw)| ≤ 1.05 , 0.35π ≤|w|≤0.6π
   |H(e^{jw})| ≤0.01, 0.65π ≤ |w| ≤ π
   Also determine the minimum length (M+1) of the impulse response and
   Kaiser window parameter β.
9. Why do we need DFT? Draw the butterfly structure to compute the DFT of
   the following signal using Radix-2 DIFFFT algorithm, and compute X(2)
   and X(1) only
   x[n] = {1.5, −1, 1.8, 0.6, 3, 1.7} [3+7]
10. Define zero padding. Find the linear convolution through circular
    convolution with padding of zeros for the following sequences:
    x[n] = {1,1,1,1} and h[n]{2,3}. [1+5]

> NOTE: Q1 prints "=" where "+" is clearly meant before nu[n−6].
> NOTE: Q3's numerator prints "2z² + 2z²" — the first term is almost
> certainly 2z³. Recorded as printed.
> NOTE: Q6 prints the word "coefficients" twice.

## p16 — 2074 Ashwin, Back, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Define Energy and Power type discrete time signal. Check whether
   signal x[n] = e^{j(πn/3+π/4)} is periodic or not. If it is periodic,
   state its periodic time. [2+2]
2. Find the output of LTI system having impulse response
   h[n] = (1/2)ⁿ {u[n + 2] − u[n − 2]} and input signal
   x[n] = {2, 1, 0.5, -1}. Also check the answer. [3+2]
3. State and explain the properties of a Region of Convergence (ROC).
   Find the inverse z-transform of
   X(z) = z²[1 − (3/2)z⁻¹](1 + z⁻¹)(1 − z⁻¹) [3+3]
4. Plot the pole-zero in z-plane and Draw Magnitude Response (not to the
   scale) of the system described by difference equation
   y[n] − 0.4y[n − 1] + 0.2y[n − 2] = x[n] + 0.5x[n − 1] + 0.6x[n − 2]
   + 0.8x[n − 3] [3+7]
5. Draw the direct form and Lattice structure of a filter with system
   function H(z) = 1+0.7z⁻¹+1.2z⁻²-z⁻³. [3+7]
6. Why Kaiser window is better than other fixed windows in FIR filter
   design? Find out first six coefficients of impulse response of a low
   pass FIR filter having Pass band edge frequency ω_p = 0.2π, Stop band
   edge frequency ω_s = 0.5π and Stop band attenuation α_s = 41dB using
   any appropriate window function. [2+6]
7. What is an optimum filter? Show mathematical expression of the Remez
   exchange algorithm for FIR filter design with flow chart. [1+6]
8. Design a low pass discrete IIR filter by Bilinear Transformation
   method to an approximate Butterworth filter having specifications as
   below: [15]
   Pass bandedge frequency (ω_p) = 0.27 π radians
   Stop bandedge frequency (ω_s) = 0.58 π radians
   Passband ripple (δ_p) = 0.11
   Stopband ripple (δ_s) = 0.21, Consider sampling frequency 0.5 Hz.
9. Compute the 8-point DFT of the sequence
   x[n] = {1/2, 1/2, 1/2, 1/2, 0,0,0,0} using Decimation in Frequency
   Fast Fourier Transform (DIF-FFT) algorithm. [7]
10. What is a zero padding? If X₁(k) and X₂(k) are DFT of sequence
    x₁[n] = {1, 2, 0, 1, -2} and x₂[n] = {1, 0, 1, 1, 2} respectively
    then find the sequence x₃[n]; If DFT of x₃[n] is given by
    X₃(k) = X₁(k), X₂(k). [1+7]

## p17 — 2073 Shrawan, New Back (2066 & Later Batch), BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Explain the process of calculating fourier series coefficients. [3]
2. Determine the system output y(n) of the following signals:
   h(n) = {1,1,1} and x(n) = {1,1,1,1} [6]
3. Define a ROC. Find inverse Z-transform of
   X(z) = z/{(z − 0.4)(z + 1.5)²}, ROC: |z| < 0.4 [1+5]
4. State linear constant coefficient difference equation and
   corresponding system function.
   Determine the output sequence of the system with impulse response
   h[n] = (1/2)ⁿ u[n] when the input signal is
   x[n] = 10 − 5sin(πn/2) + 20cos πn  −∞ < n < ∞. [3+7]
5. The system function of a filter is
   H(z) = 2 + 1.8z⁻¹ − 1.6z⁻² + z⁻³. Draw the Direct Form and Lattice
   Structure implementation of the above filter. [3+7]
6. Explain in detail about how rectangular window is used in FIR filter
   design. How Gibb's oscillations arise in this process. [6]
7. Explain about Remaz exchange algorithm with suitable derivation and
   flow chart. [9]
8. Using bilinear transformation, design a butterworth low pass filter
   which satisfies the following Magnitude Response. [12]
   0.89125 ≤ |H(e^{jw})| ≤ 1   for 0 ≤ ω ≤ 0.2π
   |H(e^{iw})| ≤ 0.17783       for 0.3π ≤ ω ≤ π
9. Explain briefly about bilinear transformation method of IIR filter
   design. [3]
10. Why do we need DFT? Find 8-point DFT of sequence
    x[n] = {1,−1,2,2,1,1,2,2} using Fast Fourier Transform algorithm. [2+6]
11. Find x₃[n] if DFT of x₃[n] is given by X₃(k) = X₁(k) X₂(k) where
    X₁(k) and X₂(k) are 5-point DFT of x₁[n] = {1,−2,2,1,4} and
    x₂[n] = {2,1,−3,−1} respectively. [7]

## p18 — 2072 Chaitra, Regular, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. How fourier series coefficients are calculated? Explain. [4]
2. Find the output of LTI system having impulse response h[n] with
   h[-2] = 1, h[0] = 2, h[1] = 3 and input signal x[n] with x[0] = 1/2,
   x[2] = 2, x[3] = 3. Also check the answer. [3+2]
3. Explain the properties of Region of Convergence with examples. [6]
4. Describe stability and causality characteristics of LTI system in
   terms of Impulse Response and ROC of its transfer function with
   suitable examples. [4]
5. Plot the pole-zero in z-plane and Draw Magnitude Response (not to the
   scale) of the system described by difference equation. [2+4]
   y[n] − 0.4y[n − 1] + 0.1y[n − 2] = x[n] + 0.6x[n − 1]
6. Determine the Direct Form I and Direct Form II realization of the
   following system. [5]
   y(n) = −0.1y(n − 1) + 0.2y(n − 2) + 3x(n) + 3.6x(n − 2) + 0.6x(n − 2)
7. Compute the lattice coefficients and draw the lattice structure of
   following FIR system. [5]
   H(z) = 1 + 2z⁻¹ + z⁻²
8. Describe how digital FIR filter can be design by window method. Why
   Kaiser window is better than other fixed windows in FIR filter
   design? [5+3]
9. What is an optimum filter? Show mathematical expression of Remez
   exchange algorithm for FIR filter design. [1+6]
10. Explain about the advantages of selecting bilinear transformation
    method over impulse invariance method (I I M). Design a digital low
    pass Butterworth filter using impluse invariant transformation with
    pass band and stop band frequencies 200Hz and 500Hz respectively. The
    pass band and stop band attenuation are -5dB and -12dB respectively.
    The sampling frequency is 5kHz. Use IIM method. [3+12]
11. Find the FFT of the signal x[n]{1,1,2,4,3,1,2,1} using DIT-FFT
    algorithm. [8]
12. Compute Circular Convolution of h(n) = {1, 2, 1, -1, 1} and
    x[n] = {1, 2, 3, 1}. [7]

## p19 — 2072 Kartik, New Back (2066 & Later Batch), BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Define energy and power signal. Check the signal x[n] = u[n] and
   x[n] = δ[n] is Energy or Power type. [2+3]
2. Find the output of LTI system having impulse response
   h[n] = (1/3)ⁿ {u[n+1]-u[n-2]} and input signal x[n] = {2,1,0.5,3}. [5]
3. State the properties of region of convergence (ROC). Drive the
   convolution property of Z-transform. [3+3]
4. Find the output of LTI System having impulse response
   h[n] = (1/2)ⁿ u[n] and input signal x[n] = 5e^{jπn/3} for
   -∞ < n < ∞. [4]
5. Plot Magnitude Response (not to the scale) of the system described by
   difference equation. [6]
   y[n]-0.5y[n-1]+0.3y[n-2] = x[n]+0.7x[n-1]
6. Determine the Direct Form II realization of the following system [4]
   y(n) = −0.1y(n − 1) + 0.72y(n − 2) + 0.7x(n) − 0.252x(n − 2)
7. Compute the lattice coefficients and draw the lattice structure of
   following FIR system [6]
   H(z) = 1 + 2z⁻¹ − 3z⁻² + 4z⁻³
8. Draw the flowchart of Remez-Exchange theorem and explain it. Design an
   FIR linear phase filter using Kaiser window to meet the following
   specifications: [6+8]
   0.99 ≤ |H(e^{jw})| ≤ 1.01, for 0 ≥ w ≥ 0.19π
   |H(e^{jw})| ≤ 0.01, for 0.21π ≤ w ≤ π
9. Design a low pass digital filter by Bilinear Transformation method to
   an approximate Butterworth filter, if passband edge frequency is
   0.25 π radians and maximum deviation of 1 dB below 0 dB gain in the
   passband. The maximum gain of -15 dB and frequency is 0.45 π radians
   in stopband, Consider sampling frequency 1Hz. [15]
10. Find 8-point DFT of sequence x[n] = {1,1,0,1,0,1,2} using Decimation
    in Time Fast Fourier Transform (DITFFT) algorithm. [7]
11. Why we need DFT? If X₁(k) and X₂(k) are DFT of sequence
    x₁[n] = {1,2,4} and x₂[n] = {-1,2,3,1} respectively, then find the
    sequence x₃[n], if DFT of x₃[n] is given by X₃(k) = X₁(k) X₂(k). [2+6]

> NOTE: Q8's first specification prints "for 0 ≥ w ≥ 0.19π".
> NOTE: Q10 lists 7 entries for an 8-point DFT.

## p20 — 2071 Shrawan, New Back (2066 & Later Batch), BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Find the odd and even part of the following signal: [4+5]
   *(FIGURE: stem plot of x[n] over −4 ≤ n ≤ 4. Values shown: x[n] = 1
   for n = −4,−3,−2,−1,0 and x[n] = 2 for n = 1,2,3,4. Cropped to
   `images/dsap_71shr_stem.png`.)*
   A discrete time LTI system has input signal and impulse response as,
   x[n] = {1 for −1 ≤ n ≤ 1; 0 elsewhere} and
   h[n] = {1 for −1 ≤ n ≤ 1; 0 elsewhere}
   Find the output of the system using graphical method.
2. Find the inverse z transform of: [6]
   X(Z) = (1+2z⁻¹+z⁻²)/(1+1.5z⁻¹+0.5z⁻²), |z| > 1
   using partial fraction method.
3. Why do we need difference equation? State linear constant coefficient
   difference equation and corresponding system function.
   Consider an LTI system with impulse response h[n]=(1/2)ⁿ u[n].
   Determine y[n], if the input is x[n] = Ae^{jnπ} [2+3+5]
4. If a 3 stage lattice filter for all pole polynomial has coefficients.
   K₁ = 1/4, K₂ = 1/2 and K₃ = 1/3 Obtain the system function of this
   filter. [5]
5. What is the importance of quantization in Digital Signal Processing?
   Which one is better rounding or truncation? Explain about limit cycles
   in recursive system? Define dead band. [1+1+2+1]
6. Explain in detail about how rectangular window is used in FIR filter
   design. How Gibb's oscillations arise in this process. [6]
7. What is a Remez exchange algorithm? Derive its equation and draw its
   flow chart. [9]
8. Design a low pass digital filter by Bilinear Transformation method to
   an approximate Butter worth filter it passband frequency is 0.2π
   radians and maximum deviation of 1 db below 0 dB gain in the pass
   band. The maximum gain of -15 db and frequency is 0.4π radians in stop
   band, consider sampling frequency 1 Hz. [15]
9. A system has input signal x[n] = {1,2,3,4} and impulse response
   h[n] = {1,3,5,7} and the DFT of x[n] is X[k] and the DFT of h[n] is
   H[k]. Find the output of the system y[n] if G[k] = X[k].H[k] [7]
10. Find DFT for {1, 1, 2, 0, 1, 2, 0, 1} using FFT DIT butterfly
    algorithm and plot the spectrum. [6+2]

## p21 — 2071 Chaitra, Regular, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Find the even and odd part of signal x[n], [3]
   x[n] = {1 for −4 ≤ n ≤ 0;  2 for 1 ≤ n ≤ 4}
2. A discrete time LTI system has impulse response h(n) = {1,3,2,−1,1}
   for -1 ≤ n ≤ 3. Determine the system output y(n) if the input x(n) is
   given by x(n) = 2δ(n) - δ(n-1). [6]
3. Define ROC. Find inverse Z-transform of [1+5]
   X(z) = 1/{(z - 0.5)(z + 2)} , if
   i) ROC: 0.5 < |z| < 2
   ii) ROC: |z| < 0.5
   iii) ROC: |z| > 2
4. The poles of a system are located at: 0.45+0.77i and -2 ± 0.3i and
   zeroes at: 1.2 ± 3i. Map the poles and zero in the z-plane and plot
   the magnitude response of the system. [2+8]
5. Compute Lattice coefficients and draw lattice structure for given IIR
   system H (z) = 1/(1-0.01z⁻¹ − 0.23z⁻²+0.5z⁻³). Also check the
   stability of given system. [4+2+1]
6. What is limit cycle effect in recursive system? Describe with one
   example showing how it occurs. [3]
7. Design a low pass FIR filter having Pass band edge frequency
   ω_p = 0.3π, Stop band edge frequency ω_s = 0.5π and Stop band
   attenuation α_s = 40 dB using any appropriate window function. [8]
8. What is optimum filter? Show mathematical expression of Remez exchange
   algorithm for FIR filter design. [1+6]
9. What is the advantage of bilinear transformation? Design a low pass
   discrete time Butterworth filter applying bilinear transformation
   having specifications as follows: [2+9+4]
   Pass band frequency (w_p) = 0.25 π radians
   Stop band frequency (w_s) = 0.55 π radians
   Pass band ripple (δ_p) = 0.11
   and stop band ripple (δ_s) = 0.21
   Consider sampling frequency 0.5 Hz.
   Also, convert the obtained digital low-pass filter to high-pass filter
   with new pass band frequency (w'_P) = 0.45 π using digital domain
   transformation.
10. Why do we need Discrete Fourier Transform (DFT) although we have
    Discrete-time Fourier Transform (DTFT)? Find circular convolution
    between x[n] = {1, 2} and y[n] = u[n] − u[n-4]. [2+5]
11. How fast is FFT? Draw the butterfly diagram and compute the value of
    X(7) using 8 pt DIT-FFT for the following sequences: [2+6]
    x(n) = {1, 0, 0, 0, 0, 0, 0, 0}

## p22 — 2070 Chaitra, Regular, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Determine which of the following signals are periodic and compute
   their fundamental period: [3]
   i) Cos(πn²/8)
   ii) Cos(n/2) cos(πn/4)
2. Find output, y(n) when: h(n) = {5,4,3,2} and x(n) = {1,0,3,2} [6]
3. List out the properties of Region of Convergence. Find the Z-transform
   and locate the ROC of the signal. [2+4]
   x[n] = (−1/3)ⁿ u[n] − (1/3)ⁿ u[−n−1]
4. Find the output of LTI System having impulse response [4]
   h[n] = (1/3)ⁿ u[n] and input signal x[n] = 5e^{jπn/2} for -∞ < n < ∞.
5. Plot Magnitude Response (not to the scale) of the system described by
   difference equation. y[n] - 0.3 y[n-1]+0.225y[n-2] = x[n] + 0.5x[n-1] [6]
6. Determine the Cascade Form realization of the following system. [4]
   y[n] − (3/4)y[n − 1] + (1/8)y[n − 2] − x[n] − 2x[n − 1] = 0
7. Compute the lattice coefficients and draw the lattice structure of
   following FIR system
   H(z) = 1 + 3.1z⁻¹ + 5.5z⁻² + 4.2z⁻³ + 2.3z⁻⁴ [6]
8. Describe how FIR filter can be designed by window method. Discuss the
   characteristics of different type of window function. [4+4]
9. What is an optimum filter? Show mathematical expression of Remez
   exchange algorithm for FIR filter design. [1+6]
10. Using bilinear transformation method, design a digital filter using
    Butterworth approximation which satisfiers the following conditions: [10]
    0.8 ≤ |He^{jw}| ≤ 1   for 0 ≤ w ≤ 0.2π
    |He^{jw}| ≤ 0.2       for 0.6π ≤ w ≤ π
11. A digital LPF with cut off frequency w_c = 0.2575 π is given as
    H(Z) = (0.1 + 0.4z⁻¹)/(1 − 0.6z⁻¹ + 0.1z⁻²)
    Design a digital high pass filter with w'_c = 0.3567π. [5]
12. Define Padding zones. Find 8-point DFT of sequence. [1+6]
    x[n] = {1,1,0,0,1,1,2} using Decimation in Time Fast Fourier
    Transform (DITFFT) algorithm.
13. Why we need DFT? State and prove Circular Convolution property of
    DFT. [2+2+4]

> NOTE: Q12 lists 7 entries for an 8-point DFT.

## p23 — 2069 Bhadra, Regular / Back, BE, BCT, IV/II, EG774CT [80 marks, 3 hrs]

1. Plot the sequence x[n] = u[n + 8] − u[n − 4]. [3]
2. What is the period of following signals? [4]
   (a) x[n] = cos((11π/3)n)
   (b) x[n] = e^{j(7/5)n}
3. What is a sampling? How are the spectrum of continuous time signal and
   the spectrum of signal obtained by sampling the continuous time signal
   related? Illustrate with diagram. [6]
4. Write about the following properties of discrete time system: [5]
   [a] linearity, [b] time invariance, [c] memory, [d] causality,
   [e] stability.
5. Find the frequency response H(e^{jω}) of the system characterized by
   difference equation y[n] − 0.8 y[n − 1] + 0.15 y[n − 2] − x[n] = 0.
   Plot the frequency response of the system. [6]
6. Realize the system function
   H(z) = 1 / ((1 − 0.5z⁻¹)(1 − 0.7e^{−jπ/4}z⁻¹)(1 − 0.7e^{jπ/4}z⁻¹)(1 − 0.3z⁻¹))
   in terms of cascade of second order sections. Draw the block diagram
   of the cascade realization. [6]
7. Write about the sign magnitude and 2's complement representation of
   binary fractional number. Write about truncation error and rounding
   error. [6]
8. Describe digital Butterworth filter design using impulse invariance
   technique. What are the limitations of impulse invariance technique? [15]
9. Derive the expression for frequency response of symmetric linear phase
   filter of length M, where M is odd. [6]
10. Use the Hanning window to design a digital low-pass FIR filter with
    Pass band frequency (ω_p) = 0.25π and Stop band frequency
    (ω_s) = 0.3π. [8]
11. Perform circular convolution of the sequences x[n] = [1 0 1] and
    h[n] = [1 0 2 1]. [5]
12. Write about multiplication and convolution property of Discrete
    Fourier Transform. [6]
13. Draw the flow diagram of four point decimation in time Fast Fourier
    Transform algorithm. [4]

## p24 — 2068 Bhadra, Regular / Back, BE, BCT, IV/II [80 marks, 3 hrs]

1. Find the energy and power of the signal x[n] = u[n]. [5]
2. Find the period of the signal x[n] = Σ_{m=−∞}^{∞} δ[n − 2 − 3m]. Find
   the Fourier series coefficients of the signal x[n]. [6]
3. State whether or not the system y[n] = e^{x[2n]} is (a) linear
   (b) time invariant (c) memoryless (d) causal. Where x[n] is input to
   system and y[n] is output of system. [5]
4. Convolve the sequences x[n] = 3ⁿu[−n − 5] and y[n] = u[n − 5]. [5]
5. Find the frequency response of the linear time invariant system
   characterized by difference equation
   y[n] − (10/24)y[n − 1] + (1/24)y[n − 2] = x[n]. If input to the system
   is x[n] = sin((π/3)n) + sin((π/5)n) then determine output y[n] of the
   system. [7]
6. Realize the overall system function: [9]
   H(z) = ((1 − (1/5)e^{−jπ/5}z⁻¹)(1 − (1/3)z⁻¹)(1 − (1/5)e^{jπ/5}z⁻¹)) /
          ((1 − (4/5)z⁻¹)(1 − (1/7)e^{jπ/7}z⁻¹)(1 − (1/5)z⁻¹)(1 − (1/7)e^{−jπ/7}z⁻¹))
   In terms of direct from I and direct from II structures. Draw the
   corresponding block diagrams of direct from I and direct from II
   structures.
7. How the spectrum of continuous time signal is related to spectrum of
   corresponding discrete time signal obtained by sampling the continuous
   time signal? Explain. Discuss what is aliasing and how it occurs. [8]
8. If passband edge frequency ω_p = 0.25π, stopband edge frequency
   ω_s = 0.45π, passband ripple δ_p = 0.17 and stopband ripple
   δ_p = 0.27 then design a digital lowpass Butterworth filter using
   bilinear transformation technique. [18]
9. Use Blackman window method to design a digital low-pass FIR filter
   with passband edge frequency ω_p = 0.24π, stopband edge frequency
   ω_s = 0.34π where main lobe width of Blackman window is 12π/M, M is
   filter length. [9]
10. Use the Fast Fourier Transform decimation in frequency algorithm to
    find the discrete Fourier Transform of the sequence
    x[n] = [1 −2 2 1]. [8]

> NOTE: Q8 prints "δ_p" for BOTH the passband and the stopband ripple;
> the second is meant to be δ_s.
> NOTE: this paper's header prints no subject code.

## p25 — 2070 Ashad, New Back (2066 & Later Batch), BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Find the even and odd part of signal x[n], [3]
   x[n] = {1 for −4 ≤ n ≤ 0;  2 for 1 ≤ n ≤ 4}
2. Illustrate the significance of convolution summation in digital signal
   analysis. Compute the convolution of the following signals:
   h(n) = {1,0,1} and x(n) = {1,−2,−2,3,4} [2+4]
3. Define Region of Convergence. Find inverse Z - transform of
   X(z) = z/{(z−1)(z−2)²}, ROC: |Z| < 1 [1+5]
4. Given H(z) for a system with the following difference equation: [2+6+2]
   y(n) = x(n) + x(n − 2)
   Plot its poles and zeros in Z plane. Determine its magnitude response.
   Also, determine whether system is causal and stable.
5. Draw lattice structure for given pole - zero system [6]
   H(z) = (0.5 + 2z⁻¹ + 0.6z⁻²)/(1 − 0.3z⁻¹ + 0.4z⁻²)
6. What do you mean by Limit Cycle? How it occurs in recursive system? [1+3]
7. What is the condition satisfied by Linear phase FIR filter? Show that
   the filter with h(n) = {−1,0,1} is a linear phase filter. [2+4]
8. Use Hanning window method to design a digital low-pass FIR filter with
   pass-band edge frequency (w_p) = 0.25π, stop-band edge frequency
   (w_s) = 0.35π where main lobe width of Hanning window is 8π/M, M is
   the filter length. [9]
9. Why Spectral Transformation is required? [2]
10. Design a low pass digital filter by impulse invariance method to an
    approximate Butterworth filter, if passband edge frequency is 0.2 π
    radians and maximum deviation of 0.5 dB below 0 dB gain in the
    passband. The maximum gain of -15 dB and frequency is 0.35 π radian
    in stopband, consider sampling frequency 1Hz. [13]
11. Why do we need Discrete Fourier Transform (DFT) although we have
    Discrete-time Fourier Transform (DTFT)? Find circular convolution
    between x[n] = {1,2} and y[n] = u[n] − u[n − 4]. [2+5]
12. How fast is FFT? Draw the butterfly diagram and compute the value of
    x(7) using 8 pt DIT-FFT for the following sequences: [2+6]
    x(n) = {1,0,0,0,0,0,0,0}

## p26 — 2069 Chaitra, Regular, BE, BCT, IV/I, CT704 [80 marks, 3 hrs]

1. Define Energy and Power type signal with suitable example. Check the
   signal x[n]=Cos(2nπ/5) + Sin(π n/3) is periodic or not. [2+2]
2. Define LTI system. Find the output of LTI system having impulse
   response h [n] = 2u [n] - 2u [n-4] and input signal
   x [n] = (1/3)ⁿ u[n]. [1+4]
3. State the properties of region of convergence (ROC)? Derive the time
   shifting property of Z-transform. [3+3]
4. Why do we need Difference Equation? Draw Pole-zero in Z-Plane and plot
   magnitude response (not to the scale) of the system described by
   difference equation [2+2+6]
   y [n]- 0.4 y [n-1] +0.2y [n-2] = x[n] + 0.1x [n-1] -0.06x [n-2]
5. Determine the Direct Form II realization of the following system [4]
   y(n) = -0.1y (n-1) + 0.72y (n-2) + 0.7x(n) - 0.252x (n-2)
6. Compute the lattice coefficients and draw the lattice structure of
   following FIR system H(z) = 1+2z⁻¹ - 3z⁻² + 4z⁻³ [6]
7. Design a digital FIR filter for the design of the low pass filter
   having ω_p = 0.3π, ω_s = 0.5π, α_s = 40 dB using suitable window
   function. [8]
8. What is optimum filter? Describe Remez exchange algorithm for FIR
   filter design with flow chart. [1+6]
9. What is the advantage of bilinear transformation? Design a low pass
   discrete time Butterworth filter applying bilinear transformation
   having specifications as follows: [2+9+4]
   Pass band frequency (w_p) = 0.25π radians
   Stop band frequency (w_s) = 0.55π radians
   Pass band ripple (δ_p) = 0.11
   And stop band ripple (δ_s) = 0.21
   Consider sampling frequency 0.5Hz
   Also, convert the obtained digital low-pass filter to high-pass filter
   with new pass band frequency (w'_p) = 0.45π using digital domain
   transformation.
10. Why do we need FFT? Find 8-point DFT of sequence
    x [n] = {1,1,2,2,1,1,2,1} using Decimation in frequency FFT (DIFFT)
    algorithm. [2+7]
11. Find x₃[n] if DFT of x₃[n] is given by X₃(k) = X₁(k) X₂(k) where
    X₁(k) and X₂(k) are 4-point DFT of x₁[n] = {1,2,-2} and
    x₂[n] = {1,2,3,-1} respectively. [6]

## p27–p28 — 2067 Mangsir, Regular / Back, BE, BCT, IV/II [80 marks, 3 hrs]

1. Compute and plot even and odd component of the sequence
   x(n) = 2u[n] − 2u[n − 4] where u[n] is unit step sequence. [2]
2. Write whether or not the following sequences are periodic and write
   the period. [4]
   a) x[n] = cos((5π/3)n)
   b) x[n] = sin(πn/√2 + π/8)
3. Find the discrete Fourier coefficients of the periodic sequence with
   period N = 11 defined over a period as
   x[n] = {1, |n| ≤ 2;  0, 2 < |n| ≤ 5} [4]
4. Show whether or not the system y(n) = nx[2(n − 2)], n > 0 is
   (a) linear, (b) time invariant, (c) memoryless. [5]
5. Find the system function H(z) of the system characterised by
   difference equation y[n] − (5/6)y[n − 1] − (1/6)y[n − 2] − x[n] = 0.
   Find the poles and zeros of the system. Use the pole-zero diagram to
   plot the approximate frequency response magnitude of the system. [10]
6. Realize the system function
   H(z) = ((1 − (1/3)z⁻¹)(1 − (1/4)z⁻¹)(1 − (1/8)z⁻¹)) /
          ((1 − (5/6)z⁻¹)(1 − (1/6)z⁻¹)(1 − (3/4)e^{−jπ/4}z⁻¹)(1 − (3/4)e^{−jπ/4}z⁻¹))
   in terms of cascade of second order sections. Draw the block diagram
   of the cascade realization.
7. Show by giving examples that the quantization error by truncation for
   sign magnitude number, e_tsm, lies in the range
   −(2⁻ᵇ − 2^{−b_u}) ≤ e_tsm ≤ (2⁻ᵇ − 2^{−b_u}) and that for the 2's
   complement number, e_t2c, lies in the range
   −(2⁻ᵇ − 2^{−b_u}) ≤ e_t2c ≤ 0. b_u is the number of bits before
   quantization and b is the number of bits after quantization.
8. How does an IIR filter differ from an FIR filter?
9. Find the system function for digital filter using impulsive invariance
   technique from the analog Butterworth filter transfer function
   H(s) = 1 / ((s + 1.3)(s − 1.3e^{j2π/3})(s − 1.3e^{−j2π/3}))
   T = 1 second, and draw the block diagram of the system function, H(z),
   realized in terms of second order sections. [15]
10. Show that the filter with impulse response h[n], 0 ≤ n ≤ N − 1, where
    h[n] = h[N − 1 − n], is a linear phase filter. [6]
11. Use the window method to design a digital low-pass FIR filter with
    Pass band frequency (ω_p) = 0.35π, Stop band frequency (ω_s) = 0.45π
    with stop-band attenuation of at least 54dB. [8]
12. Perform circular convolution of the sequences x₁[n] = [1,2,1],
    0 ≤ n ≤ 2 and x₂[n] = [1,2,0,1], 0 ≤ n ≤ 3. [5]
13. The duality property of Discrete Fourier Transform (DFT) is, if
    x[n] --DFT--> X[k] then X[n] --DFT--> nx[[−k]]_N. For input sequence
    x[n] an algorithm can compute DFT using the formula
    X[k] = Σ_{n=0}^{N−1} x[n]e^{−j(2π/N)kn}. How can this same formula be
    used to find inverse discrete Fourier transform (IDFT) of input
    sequence as X[k] with output sequence as x[n] (use duality
    property)? [8]

> NOTE: the marks for Q3, Q4, Q5, Q6, Q7 and Q8 are clipped by the right
> page edge on p27; Q3 shows "[4", Q4 shows "[", Q5 shows "[1".
> Q5's mark is read as [10] from the visible "[1" plus the paper's
> 80-mark total. Q6, Q7, Q8 marks are not recoverable from this scan.
> NOTE: Q6's denominator prints the factor (1 − (3/4)e^{−jπ/4}z⁻¹) twice;
> the second is meant to be the conjugate (1 − (3/4)e^{+jπ/4}z⁻¹).

## p29–p30 — 2066 Magh, Regular / Back, BE, BCT (059 & Later Batch), IV/II [80 marks, 3 hrs]

1. Plot the sequence x(n) = u(n) − u(n − 5) + 5δ(n − 6) + nu(n − 7)
   − nu(n − 9) where u(n) is the unit step sequence and δ(n) is unit
   sample sequence. [2]
2. Write whether or not the following sequences are periodic and write
   the period. [4]
   a) x(h) = cos((3π/8)n + π/4)
   b) x(n) = sing(0.8n)
3. Find the expression for discrete Fourier series of the sequence [4]
   x(n) = Σ_{m=−∞}^{∞} δ(n − 4m).
4. Show whether or not the following systems are (a) linear; (b) time
   invariant, (c) causal, (d) memoryless, (e) BIBO stable. [10]
   a) y(n) = 2^{log2(x(n))} + 2^{log2(x(n))}
   b) y(n) = sin{x(n) − x(n − 1)}
5. Perform circular convolution of the sequences x₁(n) = [1,2],
   0 ≤ n ≤ 1 and x₂(n) = [1,3,4,5], 0 ≤ n ≤ 3. [4]
6. Show the computation of DFT of sequence x(n) = [1,3,4,5] using
   decimation in time FFT algorithm and find the values of X(k). [6]
7. Let a system be characterized by difference equation. [10]
   y(n) − 0.5y(n − 1) − 0.25y(n − 2) − x(n) = 0, where input
   x(n) = 0.2ⁿ u(n), initial conditions y(−1) = 2, y(−2) = 4.
   Find (a) zero input response of the system, (b) zero state response of
   the system, (c) total response of the system, (d) system function H(z)
   (e) poles of H(z).
8. Find the lattice-ladder filter structure for the LTI system with
   system function. [6]
   H(z) = (1/2 + (1/3)z⁻¹ + (1/4)z⁻² + (1/5)z⁻³) /
          (1 + (1/5)z⁻¹ + (2/5)z⁻² + (3/5)z⁻³)
9. For the first order filter, y(n) = Q{a y(n − 1)} + x(n), the product
   term "a y(n − 1)" has been quantized by rounding it to 3 bits.
   y(−1) = 0, x(n) = 0.875δ(n), a = −0.5. Show whether the filter goes
   into limit cycle. What is the period of limit cycle? [4]
10. Design a digital low-pass Butterworth filter using Billinear
    transformation. Filter specifications are as follows: Pass band
    frequency (ω_p) = 0.3π, Stop band frequency (ω_s) = 0.4π, Pass band
    ripple (δ_p) = 0.11, Stop band ripple (δ_s) = 0.21. [15]
    a) Find the order of filter (N)
    b) Find the cutoff frequency (ω_c)
    c) Find the poles (s_k) of the squared magnitude response of analog
       Butterworth filter
    d) Find H(s)
    e) Find the digital Butterworth filter H(z)
11. Design a digital low-pass FIR filter with the following
    specifications using Kaiser Window. Pass band frequency
    (ω_p) = 0.25π, stop band frequency (ω_s) = 0.65π, Pass band ripple
    (δ_p) = 0.035, Stop band ripple (δ_s) = 0.035.
    a) Find the order of filter (N)
    b) Find the cutoff frequency (ω_c)
    c) Find the value of shape parameter (β)
    d) Find Kaiser window (w(n))
    e) Find the filter impulse response (h(n))
    Some modified Bessel function values are as given below.

    | x     | 0 | 1.3165 | 1.7237 | 1.8455 | 1.9271 | 1.93   | 1.9903 | 2      |
    |-------|---|--------|--------|--------|--------|--------|--------|--------|
    | J₀(x) | 1 | 1.4826 | 1.8926 | 2.0508 | 2.1675 | 2.1718 | 2.2642 | 2.2796 |

> NOTE: Q2(b) prints "sing(0.8n)" — presumably sin(0.8n).
> NOTE: Q4(a) prints the same term twice; the paper's intent is unclear.
> NOTE: Q11's mark is not printed on the scan.
