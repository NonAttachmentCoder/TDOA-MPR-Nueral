# TDOA–MPR mathematical and experimental contract (v0.2)

## Identity and coordinates

One emission, one snapshot, \(M=7\) fixed 3-D receivers from the 2019 example, fixed Cartesian origin \(O\), known propagation speed \(c\). Receiver 0 at the origin is the differencing reference. The Cartesian source position is \(p=r u\), \(r>0\), \(u\in S^2\), \(g=1/r\). The estimator returns \((u,g)\) without a regime label. The map supports the plane-wave limit \(g=0\). Negative estimates of \(g\) are retained under the signed analytic continuation.

The inputs are \(y\in R^6\) in m, \(S_{\rm rep}\in R^{7\times3}\) in m, \(Q_r\in R^{6\times6}\) and \(Q_s\in R^{21\times21}\) in m² with stations ordered \([s_{0x},s_{0y},s_{0z},\ldots,s_{6z}]\). The conversion to seconds is \(\tau=y/c\), \(Q_\tau=Q_r/c^2\). Only the range differences, reported positions and nominal covariances enter inference.

## Physical and statistical definitions

For all \(i\ne0\), with \(a_i=\|u-gs_i\|\), \(a_0=\|u-gs_0\|\),

\[
h_i(u,g,S)={-2u^T(s_i-s_0)+g(\|s_i\|^2-\|s_0\|^2)\over a_i+a_0}.
\]

For \(g>0\) this is exactly \(\|p-s_i\|-\|p-s_0\|\). At \(g=0\): \(-u^T(s_i-s_0)\). The denominator is well-defined provided the source is not exactly coincident with two receiver positions. The formula is numerically stable at \(g=0\), unlike direct subtraction divided by \(g\).

Define \(D\in R^{6\times7}\) with rows \(D_i=e_i^T-e_0^T\), \(i=1,\dots,6\). For receiver arrival-range errors of covariance \(Q_{\rm toa}\), \(n_r=De\) and \(Q_r=DQ_{\rm toa}D^T\). The figure axis \(d\) is the marginal variance of a range difference in dB relative to 1 m². With \(\sigma_n^2=10^{d/10}\) m², each independent arrival has variance \(\sigma_n^2/2\), and \(Q_r=\sigma_n^2(I_6+\mathbf1\mathbf1^T)/2\).

Both official sweeps have \(S_{\rm rep}=S_{\rm true}\) and \(Q_s=0\). For separate station-error studies, \(S_{\rm rep}=S_{\rm true}+E_s\) with station-major covariance \(Q_s\) independent of arrival errors. Linearizing around \(S_{\rm rep}\) gives \(C(u,g)=Q_r+J_s Q_s J_s^T\) with respect to the 21 station coordinates. This approximates propagation of finite position errors to first order.

For fixed \(Q_r\) and known \(S\), nominal Gaussian likelihood has negative log likelihood \( \frac12(y-h)^TQ_r^{-1}(y-h)\) up to constants. When incorporating a state-dependent \(C\), the marginal Gaussian approximation additionally involves \(\frac12\log\det C\); plain WLS with \(C\) held or recomputed is a **pseudo-likelihood** if that term is absent. The supplied numerical solver is labelled WLS, not an authenticated reproduction of original TDOA MLE.

## Local derivatives and information

Use a 3×2 orthonormal tangent basis \(E=[e_1,e_2]\) with \(E^Tu=0\). Let \(J_u=\partial h/\partial u\) denote the ambient derivative of the normalized-\(u\) formula and let \(J_g=\partial h/\partial g\). Then \(H=[J_uE,\;J_g]\in R^{6\times3}\) and the local information is \(F=H^TC^{-1}H\). For fixed Gaussian \(Q_r\) and known stations its inverse is the conditional CRLB. For station uncertainty label it as a first-order local approximation and report singular cases.

At \(g=0\) the angular sensitivity is \(-\Delta S E\), and the inverse-range sensitivity is \(\frac12\{\|P_u s_i\|^2-\|P_u s_0\|^2\}\), with \(P_u=I-uu^T\). These curvature terms can be weak for some geometries. They are independent of a guessed near/far threshold.

## Risk and units

Use \(R_u=E[\arccos(\mathrm{clip}(\hat u^Tu,-1,1))^2]\) in rad²; \(R_g=E[(\hat g-g)^2]\) in m⁻². Report both separately with paired confidence intervals; optional Cartesian position risk only at finite range and *not* as a replacement for direction and \(g\). Record negative \(\hat g\), solver failures, invalid outputs, and finite-sample support. Do not drop failures without a disclosed rule.

## Data and splits

The primary experiments use the two fixed-angle sweeps from the 2019 MATLAB example. Each sweep shares noise draws across grid points and subtracts the ensemble mean as in the example. Each estimator receives the same observations. The classical estimators are DeviceIoT SCO, SUM and GTRS in MPR and the Chan–Ho two-stage estimator in Cartesian coordinates, all with their released settings. The figure protocol uses squared azimuth plus elevation error and the corresponding angle-coordinate CRLB. The project also records spherical direction risk separately. [Original example](baselines/matlab/sun2019/Example.m) · [Experiment contract](paper/EXPERIMENT_CONTRACT.md)

The neural development sampler uses the same fixed stations, covariance family and zero position error. It draws directions uniformly on the sphere and samples distance and noise independently so the evaluation direction and sweep identity cannot supply training targets. Development draws are independent across frames. Independent confirmation requires separate draws from those used for development or model selection.

## Claim status

Established: MPR TDOA unification, 2017/2019/2024 cited results, exact rationalized identity, differenced covariance algebra.
Implemented prototype: forward/Jacobian/covariance/Monte Carlo generator/numerical WLS/neural candidate.
Comparative Gaussian accuracy, behavior under mismatch, runtime and generalization of the neural candidate await experiments. [Source provenance for the four executable MATLAB baselines](baselines/SOURCES.md)
