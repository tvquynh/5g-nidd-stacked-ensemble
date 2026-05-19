# ATC 2026 Submission Instructions

Step-by-step actions for the corresponding author to submit the manuscript.

## Conference

- 2026 International Conference on Advanced Technologies for Communications (ATC 2026)
- Dates: October 15--17, 2026, Quy Nhon (Gia Lai), Vietnam
- Submission site: https://edas.info/N35288
- Initial submission deadline: **May 30, 2026** (artefact built 2026-05-20, ten days buffer)
- Notification of acceptance: July 30, 2026
- Camera-ready deadline: August 15, 2026
- Preferred placement: Special Session "AI-Enabled 5G/6G Communication Systems"
- Backup placement: Main track "Network Operations and Management"

## Files in this submission package

| File | Purpose |
|---|---|
| `manuscript/main.pdf` | Compiled 6-page IEEE-conference paper |
| `manuscript/main.tex`, `refs.bib` | LaTeX source |
| `manuscript/figures/*.pdf` | Office-Blue palette figures (4 figures) |
| `manuscript/tables/*.tex` | LaTeX tables (auto-generated from results) |
| `cover_letter.pdf` | Cover letter addressed to ATC 2026 editors |
| `cover_letter.tex` | LaTeX source for the cover letter |
| `highlights.txt` | Short bullet highlights |
| `README_artefact.md` | Pointer to the public GitHub + Zenodo artefact |

## Pre-submit checklist (corresponding author)

- [ ] Re-read the manuscript end-to-end once for typos and reference-numbering errors.
- [ ] Confirm the author list, affiliations, ORCID identifiers, and corresponding e-mail.
  (Author list is currently set to the PhD-team placeholder per the supporting author's note;
  the colleague taking ownership should overwrite it before submission.)
- [ ] Confirm the funding statement (PTIT) and the AI-use disclosure in the Acknowledgments.
- [ ] Verify the four figures embed correctly in the compiled PDF and that the IEEE conference template was used.
- [ ] Verify the page count is at most 6 pages including references.
- [ ] **Mint the Zenodo DOI:** create a GitHub release on the public repo, then trigger a Zenodo deposit through the connected Zenodo--GitHub integration (or upload the source zip manually). Replace the placeholder DOI string `10.5281/zenodo.XXXXXXX` in `paper/main.tex`, `README.md`, `CITATION.cff`, `.zenodo.json`, and `submission/README_artefact.md`, then recompile the manuscript.
- [ ] **Push the public GitHub repo:** see `scripts/git_setup.sh`. Recommended repo URL: `https://github.com/tvquynh/5g-nidd-stacked-ensemble`. Repo is anonymised for review until acceptance.
- [ ] Confirm the artefact link in the manuscript is reachable and the Zenodo DOI is live.
- [ ] If the special session requires a specific keyword, add it to the EDAS submission form.

## EDAS submission steps

1. Sign in to https://edas.info/ with the corresponding author account; if not yet registered, create an account first.
2. Navigate to the ATC 2026 conference page: https://edas.info/N35288.
3. Choose "Submit a new paper" and select the appropriate track:
   - Primary: Special Session "AI-Enabled 5G/6G Communication Systems"
   - Backup: Main track "Network Operations and Management"
4. Enter the title, abstract, and keywords from the manuscript verbatim.
5. Add all four authors in the project author order, listing PTIT (or SIU for D.-T.~Huynh) as affiliation.
6. Mark Trong-Thua Huynh as the corresponding author.
7. Upload `manuscript/main.pdf` as the primary file.
8. Upload `cover_letter.pdf` as a supplementary file.
9. Confirm the submission and save the EDAS paper ID for reference.

## After acceptance

- Restore the public author list in the GitHub repository (`.restore-on-accept/` contains the canonical metadata).
- Tag the repository `accepted-camera-ready`.
- Push the camera-ready PDF and update the Zenodo record with the final version.

## Withdrawal procedure (if necessary)

In case of withdrawal (for example, a duplicate-submission issue is
raised by the editors), notify the conference chairs via EDAS and remove
the EDAS entry within 48 hours. The withdrawal note should reference
this artefact's commit hash and Zenodo DOI for traceability.
