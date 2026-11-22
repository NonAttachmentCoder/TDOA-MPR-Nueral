# TDOA–MPR mathematical and experimental contract (v0.1)

## Identity and coordinates

One emission, one snapshot, \(M=8\) 3-D receivers, fixed Cartesian origin \(O\) (not the noisy reported reference location), known propagation speed \(c\). Sensor index 0 is the star-differencing reference. The Cartesian source position \(p=r u\), \(r>0\), \(u\in S^2\), \(g=1/r\). The target state is \((u,g)\). No near-/far-field regime label is an input. The exact plane-wave limit \(g=0\) is supported. **Signed estimate** \(\hat g\) is not clamped; negative values are an analytic continuation, not physically negative source range.

Inputs: \(y\in R^7\) meters, \(S_{\rm rep}\in R^{8\times3}\) meters, \(Q_r\in R^{7\times7}\) m², \(Q_s\in R^{24\times24}\) m² with stations ordered \([s_{0x},s_{0y},s_{0z},\ldots,s_{7z}]\). \(\tau=y/c\), \(Q_\tau=Q_r/c^2\). No conversion ambiguity: **network and code operate on range differences, not time units**. State truth \(u,g,S_{\rm true}\) is never an inference feature.

## Physical and statistical definitions

For all \(i\ne0\), with \(a_i=\|u-gs_i\|\), \(a_0=\|u-gs_0\|\),

\[
h_i(u,g,S)={-2u^T(s_i-s_0)+g(\|s_i\|^2-\|s_0\|^2)\over a_i+a_0}.
\]

For \(g>0\) this is exactly \(\|p-s_i\|-\|p-s_0\|\). At \(g=0\): \(-u^T(s_i-s_0)\). The denominator is well-defined provided the source is not exactly coincident with two receiver positions. The formula is numerically stable at \(g=0\), unlike direct subtraction divided by \(g\).

Define \(D\in R^{7\times8}\), each row \(D_i=e_i^T-e_0^T\) for \(i=1,\dots,7\). With independent or correlated *per-receiver* arrival-range errors \(e\sim(0,Q_{\rm toa})\), \(n_r=De\), \(Q_r=DQ_{\rm toa}D^T\). If arrival-time errors are in seconds, multiply by \(c\) before covariance formation. In particular equal independent arrival variance \(\sigma^2\) yields diagonal entries \(2\sigma^2\) and off-diagonal entries \(\sigma^2\). The seven differences, not twenty-eight dependent pairs, are the basic invertible representation.

Reported receiver locations: \(S_{\rm rep}=S_{\rm true}+E_s\), \(\operatorname{vec}(E_s)\sim (0,Q_s)\), independent of receiver arrival errors. Linearizing \(h\) around \(S_{\rm rep}\), \(C(u,g)=Q_r+J_s(u,g,S_{\rm rep})Q_sJ_s^T\). The Jacobian is with respect to the ordered 24 station coordinates. The linearized \(C\) is *only first-order*, not the exact marginal likelihood for noisy sensor positions.

For fixed \(Q_r\) and known \(S\), nominal Gaussian likelihood has negative log likelihood \( \frac12(y-h)^TQ_r^{-1}(y-h)\) up to constants. When incorporating a state-dependent \(C\), the marginal Gaussian approximation additionally involves \(\frac12\log\det C\); plain WLS with \(C\) held or recomputed is a **pseudo-likelihood** if that term is absent. The supplied numerical solver is labelled WLS, not an authenticated reproduction of original TDOA MLE.

## Local derivatives and information

Use a 3×2 orthonormal tangent basis \(E=[e_1,e_2]\) with \(E^Tu=0\). Let \(J_u=\partial h/\partial u\) denote ambient derivative of the normalized-\(u\) formula and \(J_g=\partial h/\partial g\). \(H=[J_uE,\;J_g]\in R^{7\times3}\). For small, zero-mean Gaussian perturbations, the local first-order information is \(F=H^TC^{-1}H\). Inverse \(F\) is called the **linearized local information bound** with position uncertainty; when \(Q_s=0\) and \(Q_r\) is fixed it reduces to the ordinary conditional Gaussian CRLB in local tangent coordinates. Near singular information is an actual limitation; do not silently regularize it to a favorable finite bound.

At \(g=0\) the angular sensitivity is \(-\Delta S E\), and the inverse-range sensitivity is \(\frac12\{\|P_u s_i\|^2-\|P_u s_0\|^2\}\), with \(P_u=I-uu^T\). These curvature terms can be weak for some geometries. They are independent of a guessed near/far threshold.

## Risk and units

Use \(R_u=E[\arccos(\mathrm{clip}(\hat u^Tu,-1,1))^2]\) in rad²; \(R_g=E[(\hat g-g)^2]\) in m⁻². Report both separately with paired confidence intervals; optional Cartesian position risk only at finite range and *not* as a replacement for direction and \(g\). Record negative \(\hat g\), solver failures, invalid outputs, and finite-sample support. Do not drop failures without a disclosed rule.

## Data and splits

Simulation happens at true \(S_{\rm true}\); reported \(S_{\rm rep}\) and nominal covariances are independently generated and exposed. Each frame has a shared receiver-0 error before TDOA differencing. A reference-station outlier therefore affects all seven differences together. Holdout / test geometries and seeds must be disjoint from model selection; present dev scripts are illustrative, **not** frozen confirmatory experiments. No source range or true receiver location can leak as an inference input. Synthetic contamination labels are for offline analysis only.

## Claim status

Established: MPR TDOA unification, 2017/2019/2024 cited results, exact rationalized identity, differenced covariance algebra.
Implemented prototype: forward/Jacobian/covariance/Monte Carlo generator/numerical WLS/neural candidate.
Not established: faithful official SUM/GTRS/NSP Python reproduction, asymptotic efficiency of the candidate, actual Gaussian or mismatch gains, stable inference timing, external generalization. Update only after real evidence.
