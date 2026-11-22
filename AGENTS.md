# Project instructions

- Start from `CONTRACT.md`, `HANDOFF.md` and the exact implementation before changing assumptions.
- Do not copy AOA data, trained weights, baselines, or paper results into TDOA. Preserve published TDOA algorithm identities.
- The Ho-laboratory MATLAB routines are external third-party material. Check their license and cite them. Do not label an unverified Python implementation GTRS/SUM/NSP.
- State units and receiver differencing reference in every interface. Treat the 7×7 TDOA covariance as dense.
- A local first-order propagation covariance is not an exact model for finite station-position errors.
- Neural model candidates may be changed after honest, controlled comparisons; no results in a working manuscript may be presented as observed until an experiment supplies them.
- Apply `research-lifecycle` as evidence-led scientific judgment rather than a mandated bureaucratic workflow. Use concise IEEE-style sentences and direct references.
- No training or expensive sweeps without an explicit resource budget. Preserve seeds, configs, failures and output provenance. Keep independent confirmation data separate from development.
