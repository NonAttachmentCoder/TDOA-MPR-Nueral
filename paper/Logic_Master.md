# Argument of the TDOA–MPR manuscript

## Research question

In one seven-receiver snapshot, does evaluating the physical TDOA map again at an updated direction and inverse range help a learned estimator use directional and radial information? The intended outputs are a unit direction and a signed inverse-range estimate. The first comparison covers the published fixed array and clean Gaussian noise. A separate planned test places an arrival error at the reference or at an ordinary receiver.

## What makes the question testable

A small angular displacement can explain part of a radial change in the predicted TDOAs. Projecting the whitened inverse-range derivative off the angular Jacobian gives the radial information left after fitting direction. This standard nuisance-parameter calculation explains why accurate bearing and appreciable relative radial uncertainty can coexist. The recurrent candidate computes the range differences and local receiver directions at its current estimate. Its inputs include the dense nominal covariance. The information projection serves as an analytical diagnostic in this manuscript.

## Prior work and evidence

| Claim | Support | Scope |
|---|---|---|
| MPR describes near-field localization and far-field direction finding. | Wang–Ho 2017, Sun–Ho–Wan 2019 and subsequent MPR methods. Sun et al. (2026) analyze the MPR–Cartesian comparison. | Established prior work. |
| The radial derivative can be partly or wholly absorbed by a direction change. | Tangent Jacobian and Schur complement in Section II. | Local calculation for known stations, a fixed positive definite Gaussian covariance and the indicated rank conditions. |
| The candidate makes two physical queries in three shared recurrent passes. | The first pass has zero predicted differences. The second and third use the preceding estimate. | Implemented forward computation. |
| The four released classical estimators separate in the nominal sweeps. | Matched MATLAB frames and raw method outputs. At 460 km Chan–Ho inverse-range MSE was 20.00 dB above the nominal bound. The three DeviceIoT MPR methods were within 0.2 dB at this point. | One array, one bearing, the same centered bank of 32 draws at each point. |
| Repeated queries improve neural estimation or help with timing biases. | Requires paired training and evaluation of refreshed, frozen-first-query and no-query alternatives. | Open. No learned curve is available in the paper. |

Existing robust TDOA work includes Wang–So–Li (2016) and Wang–Ho–Wang (2023). The latter studies full-set measurements. This project supplies six reference differences. Representing shared-reference correlation, changing coordinates or displaying a Cartesian threshold does not by itself establish a learning contribution. [Manuscript and references](IEEEtran_TDOA_MPR.tex) · [Source implementations](../baselines/SOURCES.md)

## Argument by section

1. Explain the ambiguity between direction, curvature and a receiver-level delay. Establish the known role of MPR and identify what a physical query can change.
2. Derive the exact forward map and the radial information conditional on fitting direction. Separate the known-station Gaussian bound from first-order station-error propagation.
3. Describe the implemented readouts, stage-specific inputs, marginal residual scaling and training objective. Give the development sampling assumptions.
4. Measure classical errors using paired data. Interpret inverse-range MSE together with the relative bound. Specify the neural control that would isolate refreshing a query.
5. State the conditional classical finding and the remaining empirical question about learned inference.

## Decisive comparison

Hold the observations, model capacity, readout count and training budget fixed. Compare the candidate with a version that reuses the first effective predicted differences and receiver bearings during the final pass while still updating the hidden state. Include the existing no-query control. Evaluate both direction and inverse range, and report radial bias. Agreement with the frozen-query control would leave any gain from refreshing the query unestablished. Assess nominal Gaussian accuracy and receiver-delay mismatch separately. The mismatch and neural comparisons require their own data and an agreed training budget. [Pilot data and figures](../experiments/seven_station_pilot/) · [Experiment contract](EXPERIMENT_CONTRACT.md)
