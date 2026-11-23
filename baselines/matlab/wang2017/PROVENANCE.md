# Wang–Ho 2017 official MATLAB source

Downloaded on 2026-11-23 from the [official CISP distribution](https://cisp.ece.missouri.edu/code/TDOALoc_MLEMPR/TDOALoc_MLEMPR.zip), linked by the [laboratory code index](https://cisp.ece.missouri.edu/code.html).

- Paper: Y. Wang and K. C. Ho, “TDOA Positioning Irrespective of Source Range,” IEEE TSP 65(6):1447–1460, 2017, DOI [10.1109/TSP.2016.2630030](https://doi.org/10.1109/TSP.2016.2630030).
- Archive SHA256: `ab253d5f4a6a7d60c200dc5c49b6f7f9b22e590aaf5f7a1b90b578678d0118ba`.
- All five `.m` files preserve the exact original bytes, including encoding, function-name inconsistencies and the 2018 updates to the original 2017 release. File hashes are in `experiments/initial_review/evidence/source_verification.json`.
- `CISP_LICENSE.txt` is the exact official license downloaded on the same date. Copyright notices are retained.
- MATLAB input is `[3,M]` station columns, `[M-1,1]` range differences in meters, dense `Q` in m². The 3-D MLE output order is `[azimuth; elevation; inverse range]`. MLE assumes a zero reference position. These routines do not take `Qs`.
- `TDOA_SDRMPR_3D.m` internally declares `TDOA_CVXMPR_3D`; MATLAB R2024a accepts the supplied filename in the audit. Do not silently rename or edit the archived source.
- Executed with MATLAB R2024a, CVX/SDPT3: four project diagnostic cases and one noiseless case using the author's Fig. 3 geometry, always initialized by the original SDR. This is **not** reproduction of the full paper figures or a convergence/efficiency guarantee. Exact `g=0`, broad noisy coverage and failure handling remain unqualified.

The bounded driver is `experiments/initial_review/verify_matlab.m`; findings and limits are in `docs/INITIAL_TECHNICAL_REVIEW.md`. Adaptations must live outside this source directory and retain their own identity.
