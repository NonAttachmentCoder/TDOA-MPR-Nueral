# TDOA–MPR–Neural

Physics-embedded neural inference for **single-snapshot, single-source, eight-receiver 3-D time-difference-of-arrival (TDOA)** localization in modified polar representation (MPR). The repository name retains its historical spelling `TDOA-MPR-Nueral`; the Python import is `tdoa_mpr`.

**Status (2026-11-23): research prototype and IEEE working manuscript, NOT experimentally validated.** The classical numerical WLS provided here is original reference code, **not** a port or reproduction of Ho's SUM/GTRS/NSP algorithms. A separate, attributed MATLAB 2019 code snapshot from a public mirror is preserved but not yet verified against the official distribution. No neural accuracy or superiority is claimed.

## Research problem

Visible inputs are reference-star range differences `y` in meters (shape `[7]`), reported stations `S_rep` in meters (`[8,3]`), their complete nominal measurement covariance `Q_r` (`[7,7]`, m²), and station-position covariance `Q_s` (`[24,24]`, m²). The output is unit direction `u` and **signed** inverse range `g` in m⁻¹. Physical ground truth is `g=1/r>0`; the analytic continuation admits `g=0` and negative estimates for diagnostic and optimization purposes. Propagation speed is known; no shared clock drift, moving source, multi-source separation, or raw-RF delay estimation is modeled.

For reference receiver 0, the stable range-difference forward map is

```text
h_i(u,g,S) = [-2 u·(s_i-s_0) + g (||s_i||²-||s_0||²)]
              / [||u-g s_i|| + ||u-g s_0||], i = 1,...,7.
h_i(u,0,S) = -u·(s_i-s_0).
```

TDOA references are statistically dependent because they share a receiver. The software represents the *full* covariance. Its first-order station-position propagation is local, not an exact marginalized likelihood.

## Start here

```bash
python -m pip install -e '.[neural,plot]'
python -m unittest discover -s tests -v
python -m tdoa_mpr.train --steps 200 --batch-size 128 --output runs/dev.pt
python -m tdoa_mpr.evaluate --checkpoint runs/dev.pt --samples 64 --output runs/dev.json
```

Matched architectural development controls can be trained with `--no-physical-query` or `--diagonal-qr`; they preserve network parameter counts and must be **retrained** on the same data schedule. Training and evaluation are opt-in commands. Neither is invoked when importing this package. Do not compare a trained checkpoint on the same random seeds used for model selection; the included CLI is a smoke-test and development framework, not a completed paper experiment. A short CPU smoke run is not a robustness demonstration.

## Where things live

| Path | Responsibility |
|---|---|
| `CONTRACT.md` | observation units, covariance, physical interpretation and estimation metrics |
| `src/tdoa_mpr/physics.py` | exact MPR forward map, local Jacobians and first-order Fisher information |
| `src/tdoa_mpr/covariance.py` | reference-star differencing and station-position propagation |
| `src/tdoa_mpr/simulation.py` | independent, per-frame TDOA/position-error simulations |
| `src/tdoa_mpr/baseline.py` | explicit numerical nonlinear WLS check, **not** published SUM/GTRS |
| `src/tdoa_mpr/neural.py` | provisional neural-first dynamic physical-query estimator |
| `src/tdoa_mpr/train.py`, `evaluate.py` | reproducible smoke-training and development evaluation |
| `baselines/` | attributed 2019 MATLAB source snapshot, download/verification plan and restrictions |
| `tests/` | limits, covariance, Jacobians, invariance and model execution |
| `paper/` | IEEEtran LaTeX paper, BibTeX, argument map and prospective experiments |
| `HANDOFF.md` | current verified state and next research decisions |

## Closest prior literature

1. Y. Wang and K. C. Ho, “TDOA positioning irrespective of source range,” *IEEE TSP*, 65(6), 1447–1460, 2017, DOI [10.1109/TSP.2016.2630030](https://doi.org/10.1109/TSP.2016.2630030).
2. Y. Sun, K. C. Ho, Q. Wan, “Solution and analysis of TDOA localization of a near or distant source in closed form,” *IEEE TSP*, 67(2), 320–335, 2019, DOI [10.1109/TSP.2018.2879622](https://doi.org/10.1109/TSP.2018.2879622).
3. Y. Sun et al., “Projection-Based Algorithm and Performance Analysis for TDOA Localization in MPR,” *IEEE TSP*, 72, 896–911, 2024, DOI [10.1109/TSP.2024.3352923](https://doi.org/10.1109/TSP.2024.3352923).
4. Official source entry and license: [K. C. Ho laboratory](https://cisp.ece.missouri.edu/code.html), [license](https://cisp.ece.missouri.edu/code/license.txt).

See `baselines/SOURCES.md` for how the official implementations will be qualified. The proposed contribution is **not** the known MPR near/far unification; it is a *testable* organization of correlated TDOA evidence and dynamic physics queries by a neural estimator.

Research/writing principles follow [NonAttachmentCoder/research-lifecycle](https://github.com/NonAttachmentCoder/research-lifecycle); factual claims, theoretical deductions, predicted performance and obtained results are separated.
