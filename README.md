# TDOA–MPR–Neural

Physics-embedded neural inference for **single-snapshot, single-source, seven-receiver 3-D time-difference-of-arrival (TDOA)** localization in modified polar representation (MPR). The repository name retains its historical spelling `TDOA-MPR-Nueral`; the Python import is `tdoa_mpr`.

The main experiments use the seven fixed receivers and the noise and distance sweeps from Sun, Ho and Wan (2019). The classical baselines are **SCO, SUM and GTRS** from DeviceIoT and the **Chan–Ho Cartesian estimator** from CISP. The neural model is a research candidate. Comparative neural accuracy and independent confirmation are pending. [Experiment contract](paper/EXPERIMENT_CONTRACT.md) · [Baseline sources](baselines/SOURCES.md)

The manuscript quantifies the separation of a finite-range source from its closest plane wave, specifies the recurrent estimator, and reports the four classical methods on paired noise and distance sweeps with 32 frames per point. [Read the working paper (PDF)](paper/IEEEtran_TDOA_MPR.pdf) · [LaTeX source](paper/IEEEtran_TDOA_MPR.tex) · [Raw observations, scores and table reproduction](experiments/seven_station_pilot/)

## Research problem

Visible inputs are reference-star range differences `y` in meters (shape `[6]`), reported stations `S_rep` in meters (`[7,3]`), their complete nominal measurement covariance `Q_r` (`[6,6]`, m²), and station-position covariance `Q_s` (`[21,21]`, m²). The output is unit direction `u` and **signed** inverse range `g` in m⁻¹. Physical ground truth is `g=1/r>0`; the analytic continuation admits `g=0` and negative estimates for diagnostic and optimization purposes. Propagation speed is known; no shared clock drift, moving source, multi-source separation, or raw-RF delay estimation is modeled.

For reference receiver 0, the stable range-difference forward map is

```text
h_i(u,g,S) = [-2 u·(s_i-s_0) + g (||s_i||²-||s_0||²)]
              / [||u-g s_i|| + ||u-g s_0||], i = 1,...,6.
h_i(u,0,S) = -u·(s_i-s_0).
```

TDOA references are statistically dependent because they share a receiver. The software represents the *full* covariance. The main sweeps have known stations and Qs=0. The general geometry library also supports first-order propagation of station uncertainty.

## Start here

```bash
python -m pip install -e '.[neural,plot]'
python -m unittest discover -s tests -v
matlab -batch "addpath('experiments'); run_cisp_sweep('noise',4,'runs/cisp/noise_4.mat')"
python -m tdoa_mpr.evaluate --sweep runs/cisp/noise_4.mat --figures runs/cisp/figures --output runs/cisp/noise_4.json
```

This example uses four frames per grid point for a wiring check. The distance sweep uses the same commands with `range` and its own output paths. Add `--checkpoint` to compare a seven-station model on the saved observations. The opt-in neural development sampler uses the source array and covariance across unknown directions. [Run instructions](experiments/README.md)

## Where things live

| Path | Responsibility |
|---|---|
| `CONTRACT.md` | observation units, covariance, physical interpretation and estimation metrics |
| `src/tdoa_mpr/physics.py` | exact MPR forward map, local Jacobians and first-order Fisher information |
| `src/tdoa_mpr/covariance.py` | reference-star differencing and station-position propagation |
| `src/tdoa_mpr/simulation.py` | seven-station development frames with known positions and common-reference noise |
| `src/tdoa_mpr/baseline.py` | archived numerical WLS diagnostic for the initial review |
| `src/tdoa_mpr/neural.py` | provisional neural-first dynamic physical-query estimator |
| `src/tdoa_mpr/train.py`, `evaluate.py` | reproducible smoke-training and development evaluation |
| `baselines/` | official DeviceIoT and Chan–Ho estimators, source provenance and 2019 scenario reference |
| `tests/` | limits, covariance, Jacobians, invariance and model execution |
| `paper/` | IEEEtran LaTeX paper, BibTeX, argument map and prospective experiments |
| `HANDOFF.md` | current verified state and next research decisions |

## Closest prior literature

1. Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range,” *IEEE TSP*, 65(6), 1447–1460, 2017, DOI [10.1109/TSP.2016.2630030](https://doi.org/10.1109/TSP.2016.2630030).
2. Y. Sun, K. C. Ho, Q. Wan, “Solution and analysis of TDOA localization of a near or distant source in closed form,” *IEEE TSP*, 67(2), 320–335, 2019, DOI [10.1109/TSP.2018.2879622](https://doi.org/10.1109/TSP.2018.2879622).
3. Y. Sun et al., “Computationally Attractive and Location Robust Estimator for IoT Device Positioning,” *IEEE Internet of Things Journal*, 9(13), 10891–10907, 2022. [DOI](https://doi.org/10.1109/JIOT.2021.3127690).
4. Y. Sun et al., “Projection-Based Algorithm and Performance Analysis for TDOA Localization in MPR,” *IEEE TSP*, 72, 896–911, 2024, DOI [10.1109/TSP.2024.3352923](https://doi.org/10.1109/TSP.2024.3352923).
5. Official source entry and license: [K. C. Ho laboratory](https://cisp.ece.missouri.edu/code.html), [license](https://cisp.ece.missouri.edu/code/license.txt).

The initial eight-station audit is available as a [historical technical review](docs/INITIAL_TECHNICAL_REVIEW.md). The proposed contribution is **not** the known MPR near/far unification; it is a *testable* organization of correlated TDOA evidence and dynamic physics queries by a neural estimator.

Research/writing principles follow [NonAttachmentCoder/research-lifecycle](https://github.com/NonAttachmentCoder/research-lifecycle); factual claims, theoretical deductions, predicted performance and obtained results are separated.
