# IEEE working TDOA–MPR manuscript

Main file: `IEEEtran_TDOA_MPR.tex`. Companion files:
- `bibtex/references.bib`: the cited primary TDOA, NLOS and model-based learning papers.
- `Logic_Master.md`: closest-prior boundaries and claim-to-evidence status.
- `EXPERIMENT_CONTRACT.md`: prospective figures, baselines and paper risks.
- `fig/`: reserved for actual generated, independently audited results only.

## Build

Install TeX Live with `IEEEtran`, `cite`, `amsmath`, `booktabs`, BibTeX. From `paper/`:

```sh
pdflatex IEEEtran_TDOA_MPR.tex
bibtex IEEEtran_TDOA_MPR
pdflatex IEEEtran_TDOA_MPR.tex
pdflatex IEEEtran_TDOA_MPR.tex
```

The manuscript follows the five-section and concise IEEE-style argument of the AOA-MPR companion manuscript but uses TDOA-specific observations, geometry, classical citations, physical derivatives and prospective experiments. Its organization also follows `NonAttachmentCoder/research-lifecycle`: **question → closest prior → mechanism → evidence required → bounded conclusion**.

**This is not a results-ready submission.** The network architecture is a testable initial candidate, not a validated new state of the art. MPR near/far unification is established prior work. All results and runtime table cells remain `Pending`. No figures, numeric claims, authors, affiliations or journal decision are fabricated.
