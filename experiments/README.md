# Research experiments

The simulation library generates independent per-frame inputs with two provenance categories: (a) Gaussian errors generated using a common reference receiver, and (b) deliberately mismatched arrival-error distributions (rare high-variance outliers or positive biases). The public `evaluate` CLI is **development/smoke only**.

Publication-grade experiments must freeze scenarios, geometry, sampling intervals, noise units, model selection, number of independent scenes/frames, comparison versions, failure handling, and confidence-interval method before inspecting confirmatory results. All methods must consume identical saved observations and reported positions. The local information bound is a valid *conditional Gaussian* CRLB when Qs=0 and otherwise labelled a first-order approximation.

Prospective paper panels and complete figure/table contracts appear in `paper/EXPERIMENT_CONTRACT.md`. Do not present expected shapes, guessed gains, dummy graphics, or short pilot results as obtained paper evidence.
