#!/usr/bin/env bash
# Build the submit-ready zip for ATC 2026 EDAS upload.
#
# Layout:
#   submission/atc_2026_<YYYYMMDD>/
#     manuscript/main.pdf
#     manuscript/main.tex refs.bib
#     manuscript/figures/*.pdf
#     manuscript/tables/*.tex
#     cover_letter.pdf
#     cover_letter.tex
#     highlights.txt
#     SUBMIT_INSTRUCTIONS.md
#     README_artefact.md
set -euo pipefail

cd "$(dirname "$0")/.."

DATE=$(date +%Y%m%d)
STAGE="submission/atc_2026_${DATE}"
ZIP="submission/atc_2026_${DATE}.zip"

rm -rf "$STAGE" "$ZIP"
mkdir -p "$STAGE/manuscript/figures" "$STAGE/manuscript/tables"

# manuscript core
cp paper/main.pdf       "$STAGE/manuscript/main.pdf"
cp paper/main.tex       "$STAGE/manuscript/main.tex"
cp paper/refs.bib       "$STAGE/manuscript/refs.bib"
cp paper/IEEEtran.cls   "$STAGE/manuscript/IEEEtran.cls"  2>/dev/null || true
cp paper/IEEEtran.bst   "$STAGE/manuscript/IEEEtran.bst"  2>/dev/null || true
cp paper/figures/*.pdf  "$STAGE/manuscript/figures/" 2>/dev/null || true
cp paper/tables/*.tex   "$STAGE/manuscript/tables/"  2>/dev/null || true

# cover + checklists
cp submission/cover_letter.pdf       "$STAGE/cover_letter.pdf"
cp submission/cover_letter.tex       "$STAGE/cover_letter.tex"
cp submission/highlights.txt         "$STAGE/highlights.txt"
cp submission/SUBMIT_INSTRUCTIONS.md "$STAGE/SUBMIT_INSTRUCTIONS.md"
cp submission/README_artefact.md     "$STAGE/README_artefact.md"

# Zip it
( cd submission && zip -r "atc_2026_${DATE}.zip" "atc_2026_${DATE}/" > /dev/null )

echo "[build] wrote $ZIP"
du -sh "$ZIP"
unzip -l "$ZIP" | head -30
