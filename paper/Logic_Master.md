# TDOA--MPR paper logic master (working, 2026-11-23)

This document implements the evidence-first / reference-calibrated argument discipline of `NonAttachmentCoder/research-lifecycle` (prewriting logic, technical core, reference use). It is not a completed experiment report.

## Question, mechanism, closest prior

**Question.** For one single-snapshot 3-D source observed by eight TDOA receivers, can a neural inference mechanism that repeatedly queries a stable MPR forward model and fuses correlated receiver evidence yield a useful direction / inverse-range risk tradeoff under varying distance, geometry and nominal/mismatched error statistics?

**Established prior.** Wang--Ho 2017 already provides source-range-invariant TDOA MPR and MLE/SDR. Sun--Ho--Wan 2019 supplies closed-form SUM and GTRS plus asymptotic performance. Sun et al. 2024 supplies NSP/INSP and a demonstrated equivalence to GTRS within its assumptions. Wang--Ho 2019 has convex alternatives. Sun et al. 2026 analyzes both strengths and limitations of MPR vs Cartesian. Wang--So--Li 2016 addresses NLOS robustness. **No claim here that MPR itself, a forward physics residual, or handling NLOS is independently novel.**

**Candidate mechanism.** Receiver-reference covariance is kept, including its off-diagonal structure; receiver-position covariance remains visible. A shared station encoder fuses the TDOA range-difference observations and model-dependent discrepancies. The next query is evaluated at the network's own state. A recurrent shared latent state produces a direction on S² and signed g. A matched no-query control determines whether the dynamic physics input matters. The whole method, not a traditional solver, is trained end to end.

## Claim-to-evidence map

| Manuscript claim | Source/evidence | Status |
|---|---|---|
| TDOA MPR unifies near/far | Wang--Ho TSP 2017 and subsequent work | Established prior, cited |
| Closed-form SUM/GTRS and NSP alternatives exist | Sun--Ho--Wan 2019; Sun et al. 2024 | Established prior, cited |
| A common reference correlates the seven TDOAs | Eq. Qr = D Qtoa D^T; unit/M-C checks | Derivable, implementation tests |
| Stable rational h supports exact g=0 | Algebraic rationalization; numerical limiting tests | Derivable, implementation tests |
| Local curvature sensitivity depends on geometry | Derivative of h at g=0 | Derivable; no performance assertion |
| Network is neural-first and uses its own physical queries | `src/tdoa_mpr/neural.py` forward | Implemented computational construction |
| Proposed network matches/improves Gaussian MPR risk | Publication-grade paired experiments vs qualified baselines | **Unverified** |
| Proposed network improves under NLOS/outliers or unseen geometry | Independent test scenes, matched learning controls and relevant robust references | **Unverified** |
| End-to-end runtime competitive | Full matched CPU/GPU timing | **Unverified** |

## Five-section story

I. **Introduction:** TDOA needs range-agnostic operation; traditional MPR has solved the representation problem. Correlated TDOA quality and unmodeled delays motivate learning, but classical NLOS robustness already exists. Introduce *specific computation* and tests, not generic neural claims.

II. **Measurement model:** emission-time cancellation, 7D reference-star covariance, reported receiver errors; exact signed-g MPR forward map and its derivatives; conditional CRLB vs approximate local information distinguish exact and first-order.

III. **Method:** scale inputs; covariance-aware station tokens; dynamic physical query; recurrent latent state; sphere/g readouts and declared saturation; joint point loss; complete inference budget. Each equation corresponds to code.

IV. **Results (prospective):** describe conditions, paired baselines, and success criteria before plotting; present no imaginary observed numbers. State unsupported baseline ports as pending. Gaussian figure validates efficiency, range/geometry figure tests physics, contamination tests generalization, ablations test specific novelty, time table measures costs.

V. **Conclusion:** summarize what has actually been established and what requires evidence. Revise after experiments, not before.

## Source roles

- Closest theoretical: Wang--Ho 2017; Sun--Ho--Wan 2019; Sun et al. 2024; Sun et al. 2026.
- Comparator implementation: Ho lab `TDOA_MLEMPR`, `TDOA_SUM_MPR`, `TDOA_GTRS_MPR` original MATLAB. See `baselines/SOURCES.md`.
- Robustness context: Wang--So--Li 2016; NLOS is not a vacant research field.
- Method-organizing precedents: Shlezinger et al. 2023; DA-MUSIC; recurrent inference machines; KalmanNet. Different modalities, no source-performance transfer.
- Writing structure: AOA--MPR manuscript's IEEEtran five-section presentation. No AOA mathematics, observations or performance is copied into this paper.
- Workflow principles: `research-lifecycle` evidence before conclusions, concise citation-led prose, matched comparison.

## Open scientific questions

1. Is a two-parameter angular plus inverse-range neural readout more stable than direct Cartesian in near/far regimes? Does saturation at |g|L<4 create failures?
2. Does encoding the full Qr correlation improve over only diagonal quality, and can a network use dense cross-station Qs after being trained only on diagonal Qs?
3. Does recurrent dynamic querying improve over same-capacity static-query/no-query alternatives on matched inputs and budget?
4. What actually constitutes an independent confirmation scenario for outliers, systematic timing bias, receiver displacement and geometry?
5. Are actual Gaussian results competitive with the **published** GTRS/SUM/MLE/NSP codes when same covariance and source configurations are used?

No answer is prejudged by the working manuscript.
