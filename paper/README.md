# IEEE working manuscript

[Read the compiled paper](IEEEtran_TDOA_MPR.pdf) · [LaTeX source](IEEEtran_TDOA_MPR.tex) · [Paper logic](Logic_Master.md) · [Experiment contract](EXPERIMENT_CONTRACT.md)

The manuscript relates the distance to a best-fitting plane wave to the local information for inverse range, then specifies a recurrent estimator that updates the predicted TDOAs and receiver bearings. Table I evaluates the wavefront distance on the published seven-receiver array. Figure 1 reports four classical estimators on matched Gaussian sweeps with 32 frames per point. Comparative neural accuracy and sensitivity to timing biases remain open. [Saved observations, scores and reproduction of the table and figure](../experiments/seven_station_pilot/)

## Build

From this directory, use TeX Live with IEEEtran and BibTeX.

```sh
latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error IEEEtran_TDOA_MPR.tex
```

The two vector panels embedded in the manuscript use relative paths in `fig/`. The bibliography is in `bibtex/references.bib`.
