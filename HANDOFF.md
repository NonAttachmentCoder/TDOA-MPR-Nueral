# TDOA-MPR-Neural handoff (2026-11-23)

## Authorization and research aim

The user authorized building a new TDOA-specific analog of AOA-MPR-Nueral in `NonAttachmentCoder/TDOA-MPR-Nueral`, including initial runnable code and IEEE research-manuscript draft, using `NonAttachmentCoder/research-lifecycle` for evidence-centered logic. The request does **not** authorize inventing measured results or representing unverified ports as the source algorithms.

## Current contents

- `CONTRACT.md`: 8-receiver known-c range-difference model, full Qr/Qs, fixed global MPR origin, signed-g extension, station-error caveat and separate direction/g risks.
- `src/tdoa_mpr/physics.py`: rationalized stable exact forward map, tangent Jacobians and local information.
- `src/tdoa_mpr/covariance.py`, `simulation.py`: full reference differencing, first-order nuisance covariance, independent Gaussian and optional contamination generator.
- `src/tdoa_mpr/baseline.py`: independent multi-start nonlinear WLS numerical comparator; not official published MLE/SUM/GTRS.
- `src/tdoa_mpr/neural.py`, `train.py`, `evaluate.py`: initial neural-first repeated physical query, training loss and *development* run entry points; no trained evidence claimed.
- `tests/`, `.github/workflows/tests.yml`: analytical limits, finite differences, covariance checks, model forward/backward.
- `paper/IEEEtran_TDOA_MPR.tex`, BibTeX, Logic_Master, EXPERIMENT_CONTRACT: complete early argument and prospective study with results explicitly pending.
- `baselines/SOURCES.md`: author-code reference and required port qualification.
- `README.md`: installation and usage.

## Primary prior work and constraints

2017 Wang/Ho TDOA MPR MLE/SDR; 2019 Sun/Ho/Wan SUM/GTRS; 2024 Sun et al. projection NSP/INSP; 2019 Wang/Ho convex relaxations; 2026 Sun et al. MPR-vs-Cartesian theory; 2016 Wang/So/Li NLOS robust algorithms. Official listings/license: https://cisp.ece.missouri.edu/code.html and https://cisp.ece.missouri.edu/code/license.txt.

## Verification and next action

1. Verify GitHub Actions result for the latest main commit. Fix actual test failures, not assumptions. Check compilation of IEEEtran/BibTeX manuscript (and bibliography references).
2. Obtain and qualify official Ho MATLAB examples under license; audit units, TDOA signs, covariance, reference ordering, and exact output identity. Do not call Python WLS an original source-paper algorithm.
3. Review whether candidate neural information paths and bounded g readout are scientifically appropriate before expensive training. A short training smoke test is permitted but is not a paper result.
4. Freeze a small paired P0 for Gaussian/reference contamination vs matched ablations before any formal testing; keep confirmation scenes unopened.
5. Populate manuscript plots, results and conclusion **only after** measured evidence exists. Keep failed and negative results.

No long-running training process was launched as part of this repository bootstrap. No paper claims of Gaussian/NLOS gains have been established.
