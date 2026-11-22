# Classical TDOA–MPR comparisons

The repository now contains a **third-party source snapshot** of the Sun--Ho--Wan 2019 MATLAB implementations under `matlab/sun2019/`. It was fetched verbatim from a public mirror referencing the same Ho-laboratory material, with its original attribution headers and the [lab license](https://cisp.ece.missouri.edu/code/license.txt). See `matlab/sun2019/PROVENANCE.md`: the official CISP bytes could **not** be cross-verified, and the MATLAB source is **not** yet qualified to the current Python simulation/geometry contract.

The executable `tdoa_mpr.baseline.solve_mpr_wls` is an independently written multi-start nonlinear WLS sanity-check. Its objective/initialization/solver are different from Wang--Ho 2017 MPR--MLE, Sun--Ho--Wan 2019 SUM/GTRS, and Sun et al. 2024 NSP/INSP. Report it as **Numerical WLS**, never as a reproduction of these methods.

See `SOURCES.md` for official URLs and the required reproduction contract. Future author-code comparisons must first freeze units/reference index, geometry origin and station ordering, Gaussian covariance, root/branch selection, signed inverse range, convergence flags, and MATLAB-vs-Python per-frame outputs.
