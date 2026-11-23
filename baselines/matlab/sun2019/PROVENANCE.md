# Third-party Sun–Ho–Wan 2019 MATLAB source snapshot

- Primary paper: Y. Sun, K. C. Ho and Q. Wan, IEEE Transactions on Signal Processing 67(2):320–335 (2019), DOI 10.1109/TSP.2018.2879622.
- Laboratory's official entrypoint: https://cisp.ece.missouri.edu/code.html
- Laboratory license (BSD-2-Clause-like): https://cisp.ece.missouri.edu/code/license.txt
- This repository's exact source of copied text: public GitHub mirror https://github.com/Mrneet/Algebraic_TDOA_Localization_MPR at commit `b0a9aeaa076c8d3e75558015b0225e0b36163709`.
- Source files remain copied as-is, including original author copyright headers, with no method edits. On 2026-11-23 the official [ZIP distribution](https://cisp.ece.missouri.edu/code/TDOALoc_AlgbSolMPR/TDOALoc_AlgbSolMPR.zip) was downloaded successfully. All eight `.m` files are **byte-identical** to this snapshot. Archive SHA256: `e8551e410310384f7c7fb015c96cde9109eabce92d3a85e5083d12a423e407ef`. The saved license matches the official license after newline normalization.
- Source identity is verified; general numerical qualification is **not complete**. Bounded MATLAB R2024a checks found a negative-elevation error and an equatorial singular case in the original SUM routine, and a nonsymmetric output from `Cov_SUM_MPR`. GTRS passed the inspected deterministic and small Gaussian checks. See `docs/INITIAL_TECHNICAL_REVIEW.md` and `experiments/initial_review/evidence/` for exact scope, hashes and raw outputs. No Python port or evaluation-CLI integration is claimed.
- MATLAB inputs are columns of station locations `senPos [3,M]`, receiver-0-first range differences `rd [M-1,1]` in meters and `Q [M-1,M-1]` in meters squared. The Python API uses receiver rows `[M,3]`. The original routines require the reference at the coordinate origin; translate input stations and map the output back to the fixed global MPR origin. They do not accept `Qs`. The review verifies this coordinate adapter only for known stations, not an uncertain-reference statistical extension.
- The author's scripts may internally construct a Cartesian position from `1/g`, producing undefined or unbounded values at `g=0`. Preserve their native failure/singularity behavior; do not turn them into a fake exact far-field baseline.
- If a port is created later, place it outside this immutable source directory with a qualification report and verified fixture outputs.

## Source blob identifiers (public mirror)

- `Bias_GTRS_MPR.m`: `b34a505db180312926bc5ef886f63a5c0b9019d5`
- `Bias_SUM_MPR.m`: `a02b09abe503f77bceae38ecc0add562c403ba11`
- `Cov_GTRS_MPR.m`: `3a97f41e13de29b59790a8bfdcc21bf8f847e027`
- `Cov_SUM_MPR.m`: `200626c7c15567dd2b271fd909cb4147490cdbd1`
- `Example.m`: `909a18ac9def0180d3842ae3247906e669efe4c5`
- `TDOALocCRLB_MPR.m`: `1c492ec35809dc839679432c63e51b10923d9659`
- `TDOA_GTRS_MPR.m`: `a7bddd1602b9adb527f22f27bc34feebc393e224`
- `TDOA_SUM_MPR.m`: `f7ad9b5dcafb6291a8f4af7a5399903c9c7f1f0d`
