# Third-party notices and research provenance

The `src/tdoa_mpr/` Python modules, tests, research contract and working paper were authored specifically for this research repository. No universal repository-wide license for this original project code is asserted by this file; the repository owner should choose one before external reuse.

The active DeviceIoT SCO, SUM and GTRS functions are distributed by Yimao Sun and K. C. Ho of the Computational Intelligence Signal Processing Laboratory, University of Missouri. The source files retain the original copyright notices. The project adapter and sweep driver are separate files. [CISP redistribution terms](baselines/matlab/device_iot/CISP_LICENSE.txt) · [Archive, file hashes and paper citation](baselines/SOURCES.md)

The Cartesian `TDOALoc.m` release of the Chan–Ho method is credited to Ming Sun and K. C. Ho, Computational Intelligence Signal Processing Laboratory, University of Missouri. The source retains its 2009 copyright and October 2010 revision header. [CISP license](baselines/matlab/chan_ho1994/CISP_LICENSE.txt) · [Source and paper citation](baselines/SOURCES.md)

The third-party MATLAB snapshot under `baselines/matlab/sun2019/` is attributed to Yimao Sun, K. C. Ho and the Computational Intelligence Signal Processing Laboratory, University of Missouri. Its source copyright headers remain intact. The laboratory's original redistribution license is preserved at `baselines/matlab/sun2019/CISP_LICENSE.txt`; the public mirror commit and filenames are recorded at `baselines/matlab/sun2019/PROVENANCE.md`. All eight `.m` files were verified byte-for-byte against the official ZIP on 2026-11-23. No modifications to those original files were made.

The official Wang--Ho 2017 distribution is preserved under `baselines/matlab/wang2017/`, with its original source bytes, copyright headers, laboratory license and a provenance record. Its bounded execution checks and those of the 2019 source are not a claim of full paper reproduction; known numerical defects are documented in `docs/INITIAL_TECHNICAL_REVIEW.md`.

IEEEtran, BibTeX style and all LaTeX packages used by the paper are supplied by the user's TeX installation or the GitHub Actions container; no third-party IEEEtran class or style file is vendored here. Paper citations refer to original scientific sources, which are not reproduced in this repository.

The sibling AOA-MPR project and `research-lifecycle` are consulted for research/writing organization, not used as sources of TDOA numerical results.
