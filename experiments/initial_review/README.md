# Initial technical review diagnostics

These are bounded **development checks**, not training, paper-figure reproduction or independent confirmation. The decision and interpretation are in [`docs/INITIAL_TECHNICAL_REVIEW.md`](../../docs/INITIAL_TECHNICAL_REVIEW.md).

From the repository root:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python experiments/initial_review/verify_numerics.py
matlab -batch "addpath('experiments/initial_review'); verify_matlab"
```

The Python driver creates `runs/initial_review/matlab_inputs.mat`; run it before MATLAB. The MATLAB driver uses the unchanged source directories under `baselines/matlab/` and isolates their identically named CRLB functions. It requires MATLAB, CVX and an available SDP solver; the recorded run used R2024a and SDPT3. Neither driver runs `train.py`, performs an optimizer step, invokes the original large Monte Carlo examples, or reads a pre-existing data bank.

The Python seed is `2026112301`. It uses six g values for derivatives, eight deterministic WLS inputs, 2048 generated frames for noise moments, 512 frames for the variance-inflation check, a paired equal-delay-bias example, and 4096 shared position-noise draws at each of three scales. MATLAB uses 32 saved Gaussian noise vectors for each of three scenes; both methods and the three scenes share these vectors. There is no sample recentering, noise rejection or exclusion of failed/negative-g estimates. The additional no-noise cases use either the project geometry or an explicitly identified original example geometry. Negative *true* g appears only in a labelled analytic-continuation diagnostic, never as a physical training sample.

`evidence/python_checks.json` and `matlab_checks.json` contain the actual outputs, including native MATLAB complex parts, warnings and all 192 noisy method outputs (96 inputs, two methods). `unit_tests.log` records the test run. `ambient_jacobian_before.json` preserves the pre-fix counterexample. `source_verification.json` records official archive URLs, byte counts, SHA256s and exact source matches; `bibliography_metadata.json` is bibliographic verification, not proof of full-text reading. `requirements.txt` records the installed Python versions. The downloaded ZIP archives and temporary logs remain under ignored `runs/initial_review/`.

For a clean Python installation, create a virtual environment and run `python -m pip install -r experiments/initial_review/evidence/requirements.txt` from this checkout. The requirements include the CPU wheel index and `-e .`, so they use the reviewed working files rather than silently fetching the unmodified base commit. On this host, system `python3 -m venv .venv` lacked ensurepip; `python3 -m pip --python .venv install -e . pytest` and `python3 -m pip --python .venv install torch --index-url https://download.pytorch.org/whl/cpu` completed the environment, followed by installation of pip into that environment. No system packages were replaced.

The source packages are publicly downloadable from the exact URLs in the source record. Compare SHA256 before using a fresh download; a future upstream change is a new source version. Original MATLAB files are intentionally not patched by these drivers. In particular, observed SUM failures are retained as evidence of defects and must not be used to claim superiority of another estimator.
