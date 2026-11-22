# TDOA-MPR planned publication experiments (prospective v0)

**Status: DESIGN, not frozen empirical results.** This contract describes experiment questions, axes, metrics, and pitfalls; it is to be frozen *before* running confirmatory simulations. Existing `evaluate.py` is a development tool. The paper's five figure slots and table are intentionally unfilled.

## Universal settings

Single source, one snapshot, eight receivers, 3-D, known c, one trained network for all source ranges and geometries. TDOA observations are `y_i=c(t_i-t_0)` in m, Qr is m² full 7×7 and Qs is m² full 24×24. The common receiver-0 error is generated once per snapshot before forming seven differences; never draw seven independent Gaussian errors and call them nominal TDOA. Report S_rep only; S_true is private.

Primary risks are paired squared spherical angular error (rad²) and signed inverse-range MSE (m^-2). Quote n independent geometries/scenes and frame counts, intervals, invalid counts, and negative g. A zero-g point estimate has radial MSE \(g^2\) and is a mandatory interpretive reference at large distance. Do not substitute Cartesian position risk near the far-field limit. In the conditional Gaussian Qs=0 case use the tangent-coordinate CRLB; with Qs>0 use the **first-order local information approximation** and label it.

Before comparing, validate official MATLAB MPR-MLE, SUM, GTRS and, if available, NSP/INSP across paired saved inputs. Report exact code provenance and failure behavior. The local `solve_mpr_wls` is *not* an official baseline. Match iteration ceilings, precision and initialization fairness as far as the original methods allow; report differences. NLOS-robust comparators are desirable when assumptions and resources align.

## Main figure/table design

| Item | Variable / control | Main question | Expected interpretation to test, not result |
|---|---|---|---|
| Fig. 1: Gaussian | Sweep arrival standard deviation, e.g. 0.03–3 m, and separate station-position noise, e.g. 0–1 m | Does joint risk approach published MPR solutions and local Gaussian information? | Neural penalty may depend on SNR and covariance calibration |
| Fig. 2: distance and network | Source distance e.g. 30–80,000 m plus exact g=0; compare two equal-RMS but different transverse geometry layouts | Can a single model continuously use direction and curvature information? | Inverse-range derivative can remain finite at g=0 but geometrically weak |
| Fig. 3: contaminated arrival times | Independent receiver events p=0/0.05/0.10/0.20, std multiplier 8; separately force only reference receiver | Does evidence aggregation handle common-reference-correlated outliers? | A reference error corrupts all seven difference entries jointly |
| Fig. 4: bias and wrong station reports | Positive excess delay and systematic differential clock offsets; reported-position shift at one receiver | Which unseen errors can learned fusion mitigate? | Unseen systematic faults might cause large neural biases |
| Fig. 5: ablation | Dynamic query vs matched no-query; full vs diagonal Qr; same train data/loss/seed/steps/params | Is the proposed physical/covariance mechanism necessary? | Remove feature routes by re-training controls, not test-time masking |
| Table I: timing | MPR-MLE, SUM/GTRS, available NSP, numerical WLS, candidate neural full/control | Complete end-to-end CPU B=1 and batch B=128; GPU if implemented | Include pre/postprocessing, memory movement, initialization, iterations |

Suggested axes and values above are *design candidates*. Do not assign a trial count or claim "pre-registered" until the actual benchmark seed, layouts, checkpoints, noise laws and selection rule have been fixed. The final paper must state whether a mismatched family was seen in training. Any result used to choose weights is development evidence, not a blind confirmation.

## Implementation constraints revealed by current code

- The released simulator supports Gaussian independent receiver arrival errors, receiver outlier variance inflation, positive receiver delay bias, and noisy reported receiver positions. Differential persistent clock offsets, paired fixed geometry A/B sets, and explicit exact g=0 test generator are **planned, not implemented**. Matched no-query and diagonal-Qr network controls are now implemented as training flags; their fairness and statistical value remain untested.
- The neural implementation accepts dense Qr and Qs, but training samples currently have Qs diagonal. Correlated Qs generalization must be tested; input shape alone does not imply it.
- Range-distribution and geometry priors are presently illustrative. Their upper/lower bounds are in `SimulationConfig`. Any final study must disclose and freeze them.
- Numerically stable signed g extension is mathematical; negative true ranges must not be manufactured as physical training data.
- The 2024 projection-method claims belong to the cited paper. The present repo cannot attribute any experimental performance to NSP until verified source or independently qualified implementation is available.
