# Classical TDOA–MPR comparisons

The source-author reference implementations are **not vendored** in this initial commit. This avoids copying external software without checking all notices and avoids falsely labelling a homemade numerical estimator as a published method.

The executable `tdoa_mpr.baseline.solve_mpr_wls` is a multi-start nonlinear WLS sanity-check. Its objective/initialization/solver are different from Wang–Ho 2017 MPR–MLE, Sun–Ho–Wan 2019 SUM/GTRS, and Sun et al. 2024 NSP/INSP. Report it as **Numerical WLS**, never as a reproduction of these methods.

See `SOURCES.md` for official URLs and the required reproduction contract. Future author-code comparisons should first freeze units/reference index, station ordering, Gaussian covariance, root/branch selection, signed inverse range, convergence flags, and MATLAB-vs-Python per-frame outputs.
