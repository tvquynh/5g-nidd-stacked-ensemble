# Reviewer-runnable artefact

The code, configuration, ten project seeds, and aggregation pipeline that
produce every number and figure in this paper are available at:

- GitHub repository: https://github.com/tvquynh/5g-nidd-stacked-ensemble
- Zenodo DOI: 10.5281/zenodo.XXXXXXX (minted at submission time; final
  DOI will replace this placeholder before camera-ready)

Reproduction requires a Linux host with Python 3.10, 60+ CPU cores, and
at least 32\,GB of RAM. The author-curated `Encoded.csv` distribution of
5G-NIDD (Samarakoon et al., arXiv:2212.01298) is needed as input;
instructions to acquire it are in `RUNBOOK.md` of the artefact.

The `README.md` of the repository describes the layout; `RUNBOOK.md`
gives the exact sequence of commands; `tests/test_pipeline.py` is a
self-contained pytest suite that does not need the 5G-NIDD parquet.

## Contents of this submission package only

| File | Purpose |
|---|---|
| `manuscript/main.pdf` | Compiled IEEE-conference paper (6 pages) |
| `manuscript/main.tex`, `refs.bib` | LaTeX source |
| `manuscript/figures/*.pdf` | Office-Blue palette figures (Fig.~1--4) |
| `manuscript/tables/*.tex` | LaTeX tables (tab.~main, latency, perclass) |
| `cover_letter.pdf`, `cover_letter.tex` | Cover letter to ATC 2026 |
| `highlights.txt` | Bullet highlights |
| `SUBMIT_INSTRUCTIONS.md` | EDAS upload checklist |
