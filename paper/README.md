# IEEE working manuscript

[Read the compiled paper](IEEEtran_TDOA_MPR.pdf) · [LaTeX source](IEEEtran_TDOA_MPR.tex) · [Paper logic](Logic_Master.md) · [Experiment contract](EXPERIMENT_CONTRACT.md)

The manuscript studies recurrent physical queries for single-snapshot TDOA direction and inverse-range estimation. Its measured results are the four classical estimators on the fixed seven-station Gaussian sweeps, with 32 frames per point. Neural comparisons and tests with timing biases remain prospective. [Saved observations, scores and all six figures](../experiments/seven_station_pilot/)

## Build

From this directory, use TeX Live with IEEEtran and BibTeX.

```sh
latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error IEEEtran_TDOA_MPR.tex
```

The two vector panels embedded in the manuscript use relative paths in `fig/`. The bibliography is in `bibtex/references.bib`.
