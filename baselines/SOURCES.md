# Published TDOA–MPR reference algorithms and provenance

Official listing: https://cisp.ece.missouri.edu/code.html
Official code terms: https://cisp.ece.missouri.edu/code/license.txt
The source is maintained by K. C. Ho's Computational Intelligence Signal Processing group (University of Missouri).

| Paper / algorithm | Official code name | Intended role | State |
|---|---|---|---|
| Wang and Ho (TSP 2017), DOI 10.1109/TSP.2016.2630030 | TDOA_MLEMPR, TDOA_SDRMPR_3D, TDOALocCRLB_MPR | MPR iterative maximum likelihood; SDR initialization; bound | inventoried, not ported |
| Sun, Ho and Wan (TSP 2019), DOI 10.1109/TSP.2018.2879622 | TDOA_SUM_MPR, TDOA_GTRS_MPR, TDOALocCRLB_MPR, Cov_SUM_MPR, Bias_SUM_MPR, Cov_GTRS_MPR, Bias_GTRS_MPR | closed-form MPR reference, theoretical performance | inventoried, not ported |
| Sun et al. (TSP 2024), DOI 10.1109/TSP.2024.3352923 | NSP, INSP, NSPBS (check author implementation availability independently) | projection-based comparisons | paper identified; code availability not asserted |
| Wang and Ho (TWC 2019), DOI 10.1109/TWC.2019.2903037 | convex relaxation | additional reference | not ported |

The first two source bundles are listed on the official site as `TDOALoc_MLEMPR.zip` and `TDOALoc_AlgbSolMPR.zip`. Their MATLAB examples use paper-specific units and covariance conventions; source outputs should not be silently treated as equivalent to the new position-error protocol.

**Required before source reproduction claim:** obtain authorized files; preserve notices; record source version/sha, original license and citation; run original examples; compare original MATLAB to any translation on identical saved frames, including near/transition/far, zero- and negative-estimate cases and failure flags; verify full covariance/reference ordering. A solver started at a favorable true state is not a fair baseline.

No published TDOA solver's claimed theoretical accuracy is assigned to `src/tdoa_mpr/baseline.py`. Its role is simply an independently checkable optimization comparator.
