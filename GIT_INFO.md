# GIT_INFO

This artefact is mirrored to a public GitHub repository and Zenodo at
submit-ready time. The local repository root contains all reviewer-visible
content; build artefacts and metrics JSONs are excluded by `.gitignore`
and produced on the reviewer's machine by following `RUNBOOK.md`.

## Public mirror

- Repository: https://github.com/tvquynh/5g-nidd-stacked-ensemble
- Zenodo DOI: 10.5281/zenodo.XXXXXXX (minted at submit-ready, replaced
  with the final DOI before camera-ready)
- Submit-ready tag: `submit-ready-atc-2026`

## What is in the public repo

| Top-level path | Purpose |
|---|---|
| `configs/` | paths, model hyperparameters, seeds |
| `src/` | data I/O, splits, base learners, stacking, latency, metrics, viz, tables |
| `scripts/` | smoke.sh, run_bases.sh, run_stacked.sh, run_all.sh, build_submission.sh, git_setup.sh |
| `tests/` | pytest unit tests on synthetic data |
| `paper/` | LaTeX source, figures, tables, compiled PDF |
| `submission/` | cover letter, SUBMIT_INSTRUCTIONS, highlights |
| `.restore-on-accept/` | canonical author metadata restored after acceptance |
| `README.md`, `RUNBOOK.md`, `LICENSE`, `CITATION.cff`, `.zenodo.json`, `requirements.txt` | top-level reproducibility metadata |

## Anonymisation status (during peer review)

Per the project rule `feedback_redact_reviewer_artifact_during_review.md`,
the public repo is anonymised during peer review:
- `CITATION.cff`: authors set to "Anonymised, Pending peer review".
- `.zenodo.json`: creators set to "Anonymised, Pending peer review".
- `README.md` Citation section: placeholder text.
- Manuscript title appears in the public repo with star-redaction word-by-word.

Original metadata is preserved in `.restore-on-accept/` and restored
post-acceptance per `.restore-on-accept/RESTORE_NOTES.md`.

## What is NOT redacted

- Repository name and URL (cited from the manuscript).
- Zenodo DOI (cited from the manuscript).
- Source code, module names, schema names, variable names, hyperparameters.
- Git history.

## How to reproduce

See `RUNBOOK.md`.

## Acknowledgement of upstream code reuse

This artefact reads the 5G-NIDD master parquet built by an upstream
preprocessing pipeline. The upstream preprocessing logic is described in
sufficient detail in `src/io_utils.py::load_master` and `RUNBOOK.md`
Section 7 so a reviewer can rebuild it from the public `Encoded.csv`
release.
