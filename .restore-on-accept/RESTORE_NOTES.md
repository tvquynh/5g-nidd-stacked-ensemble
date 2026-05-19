# Restore-on-accept instructions

During the ATC 2026 peer-review cycle the GitHub repository is
anonymised per the project's reviewer-artefact redaction rule. After
acceptance and immediately before the camera-ready submission deadline,
restore the public author metadata using the steps below.

## Files to restore (currently anonymised in the public repo)

| File | Anonymised content | Canonical content (this folder) |
|---|---|---|
| `CITATION.cff` | "Anonymised, Pending peer review" | `CITATION.cff.canonical` |
| `.zenodo.json` | "Anonymised, Pending peer review" | `.zenodo.json.canonical` |
| `README.md` (Citation section) | placeholder | `README.snippet.canonical.md` |

## Commands

```bash
# from repository root
cp .restore-on-accept/CITATION.cff.canonical  CITATION.cff
cp .restore-on-accept/.zenodo.json.canonical  .zenodo.json
# Manually merge README.snippet.canonical.md into the Citation section of README.md.

git add CITATION.cff .zenodo.json README.md
git commit -m "Restore canonical author metadata after ATC 2026 acceptance"
git tag accepted-camera-ready
git push origin main --tags
```

## What is NOT redacted

- Repository name and URL (the manuscript cites them).
- Zenodo DOI (the manuscript cites it).
- Source code, module names, schema names, variable names, git history.
- Hyperparameters and seeds.

This list matches the project rule in `feedback_redact_reviewer_artifact_during_review.md`.
