# TDOA-MPR-Neural handoff (2026-11-23)

## Authorization and research aim

The user authorized building a new TDOA-specific analog of AOA-MPR-Nueral in `NonAttachmentCoder/TDOA-MPR-Nueral`, including initial runnable code and IEEE research-manuscript draft, using `NonAttachmentCoder/research-lifecycle` for evidence-centered logic. The request does **not** authorize inventing measured results or representing unverified ports as the source algorithms.

## Current experiment decision

Use seven fixed receivers (reference 0), six range differences, full 6×6 Qr and 21×21 Qs. The 2019 Example.m defines the two sweeps. Compare the released DeviceIoT MPR methods (SCO, SUM, GTRS) and the CISP Chan–Ho Cartesian estimator on the same draws. Preserve native positions and failures. Cartesian inverse range is the reciprocal norm of the displacement from the reference station. Use the original DMPR paper-demo layout for the angle and inverse-range panels. [Run and plot instructions](experiments/README.md) · [Source record](baselines/SOURCES.md)

## Current contents

- `CONTRACT.md`: 7-receiver known-c range-difference model, full Qr/Qs, fixed global MPR origin, signed-g extension, station-error caveat and separate direction/g risks.
- `src/tdoa_mpr/physics.py`: rationalized stable exact forward map, tangent Jacobians and local information.
- `src/tdoa_mpr/covariance.py`, `simulation.py`: full reference differencing, first-order nuisance covariance, independent Gaussian and optional contamination generator.
- `src/tdoa_mpr/baseline.py`: historical eight-station WLS diagnostic for reproducing the initial review.
- `src/tdoa_mpr/neural.py`, `train.py`, `evaluate.py`: initial neural-first repeated physical query, training loss, trainable matched no-query/diagonal-Qr controls and *development* run entry points; no validated performance claimed.
- `tests/`, `.github/workflows/tests.yml`: analytical limits, finite differences, covariance checks, model forward/backward.
- The [working manuscript](paper/IEEEtran_TDOA_MPR.pdf) includes the 32-frame Gaussian pilot. The [paired data](experiments/seven_station_pilot/) are sufficient to regenerate both main panels. Neural, mismatch and confirmation results remain prospective.
- `baselines/matlab/sun2019/`: attributed MATLAB 2019 source snapshot from a public mirror, with CISP license; all eight `.m` files verified byte-identical to the official ZIP in the initial technical review. `baselines/matlab/wang2017/` now preserves the five official 2017 files as well. Source identity does not imply numerical qualification.
- `baselines/SOURCES.md`: author-code reference and required port qualification.
- `README.md`: installation and usage.

## Primary prior work and constraints

2017 Wang/Ho TDOA MPR MLE/SDR; 2019 Sun/Ho/Wan SUM/GTRS; 2024 Sun et al. projection NSP/INSP; 2019 Wang/Ho convex relaxations; 2026 Sun et al. MPR-vs-Cartesian theory; 2016 Wang/So/Li NLOS robust algorithms. Official listings/license: https://cisp.ece.missouri.edu/code.html and https://cisp.ece.missouri.edu/code/license.txt.

## Verification and next action

1. For either published sweep use `run_cisp_sweep` and evaluate the saved MAT file. MATLAB's source noise bank is mean-centered and reused across sweep points. Each method must use exactly the same draws. The known GTRS series mix-ups in the 2019 plotting script are avoided by selecting each method's outputs by name.
2. A comparison at one fixed array, bearing, Qs=0 and TDOA correlation 1/2 measures conditional performance. Variable geometry, station uncertainty and adaptation to correlation require different evidence.
3. Formal training and confirmation depend on a separately agreed budget and design. Only fill manuscript results from measured, appropriately identified experiments.

## Reusable lessons from the independent initial review

See `docs/INITIAL_TECHNICAL_REVIEW.md` and `experiments/initial_review/` before baseline or architecture work. The review recommends **Modify**, with formal training and material method changes reserved for the next discussion.

- Official bytes are not a correctness certificate. The 2019 SUM code audited at that time fails a negative-elevation noiseless case by 180°, has an equatorial singular case, and returns an invalid theoretical covariance through a missing transpose. DeviceIoT SUM uses a different elevation formula. Attribute findings to the exact file version.
- The archived 2019 SUM/GTRS and 2017 3-D MLE assume reference-centered coordinates. Center inputs and map direction/g back to the fixed global origin; uncertain reference coordinates additionally require a statistical treatment. Original angle-MSE and TDOA noise-power conventions differ from this project's spherical risk and receiver-arrival sigma.
- A normalized-input forward function needs the normalization chain rule in its ambient Jacobian. Tangent-only checks cannot detect its omission. The Python interface is corrected; its tangent physics is unchanged.
- Curvature magnitude alone does not measure radial identifiability. Remove the direction nuisance component (Schur complement/projection) before interpreting inverse-range information; even a noncoplanar equal-aperture geometry can have zero first-order radial information.
- Accepting a dense covariance is not evidence of learning it. The archived eight-station generator gave zero data gradient to 552 off-diagonal Qs columns. In the current fixed seven-station protocol the entire Qs input is zero.
