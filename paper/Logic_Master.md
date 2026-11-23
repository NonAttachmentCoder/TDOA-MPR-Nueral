# Scientific argument of the TDOA–MPR manuscript

## Research question

How much inverse-range information survives uncertainty in bearing in a single TDOA snapshot, and can an estimator use that information by evaluating the physical model at successive estimates? The target is a unit direction and signed inverse range. The Gaussian results condition on the seven published receiver positions, one bearing and known propagation speed.

## Claims and evidence

| Claim | Evidence and scope |
|---|---|
| MPR connects point localization with direction finding as inverse range approaches zero. | Wang–Ho (2017) established the representation. Sun–Ho–Wan (2019) derived SUM and GTRS. The published MPR–Cartesian comparison and subsequent methods define the prior-art boundary. |
| A fitted plane wave can absorb part of the delay due to wavefront curvature. | Section II minimizes the Mahalanobis distance between predicted means over unit plane-wave directions. At a rank-three array its far-field expansion has coefficient equal to the square root of the radial Fisher information after eliminating the direction nuisance. When this information is positive, the reciprocal distance approaches the relative radial standard-deviation bound in ratio. Both results follow from the measurement model and nuisance-parameter projection. |
| The separation decreases appreciably on the published distance sweep. | Table I evaluates the global minimum from the six known mean differences. At a marginal variance of 1 m² it falls from 48.83 at 20 km to 2.16 at 460 km. The relative inverse-range standard-deviation bound rises from 2.07% to 46.39%. These numbers are deterministic properties of this array and bearing. |
| The estimator recomputes predicted differences and local bearings at two successive states. | Section III corresponds to three shared recurrent passes in the implementation. The first has zero predicted differences. The two subsequent passes evaluate the model at the preceding readouts. The plane-wave fit uses known truth for analysis and is outside the estimator. |
| Absolute inverse-range errors can be close to the nominal bound while relative range resolution is poor. | Figure 1 measures four published estimators on the same 32 centered draws per setting. At 460 km, the three DeviceIoT inverse-range MSEs are within 0.2 dB of the nominal bound. The Cartesian Chan–Ho gap is 20.00 dB. |
| Refreshing the physical query improves neural estimation or helps with receiver-level timing errors. | Open. The Gaussian curves contain only classical estimators. Neither those curves nor the wavefront-distance calculation measures learned accuracy. |

[Manuscript](IEEEtran_TDOA_MPR.tex) · [Table and figure reproduction](../experiments/seven_station_pilot/) · [Source implementations](../baselines/SOURCES.md)

## Comparison needed for the learned method

Compare updated queries with reuse of the first effective query on the final pass. The frozen-query control retains the first predicted differences and local receiver bearings while updating the hidden state and the other state inputs. Match observations, parameter count, number of readouts and training budget. The implemented no-query control measures the combined effect of physical feedback. Assess spherical direction error, signed inverse-range error and radial bias on paired evaluation frames.

Time-of-arrival contamination requires separate evidence. Place a matched excess delay at the reference or one other receiver before differencing and distinguish the resulting common shift from a single affected difference. Performance under varying geometries, correlations or station-position errors is outside the nominal comparison. Formal training and independent evaluation require their agreed data and resource budget. [Experiment contract](EXPERIMENT_CONTRACT.md)
