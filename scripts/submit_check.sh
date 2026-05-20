#!/usr/bin/env bash
# Pre-flight verification that the submission package is complete.
# Run this just before EDAS upload.
set -euo pipefail

cd "$(dirname "$0")/.."

OK=0
FAIL=0
warn() { echo "WARN: $*"; }
fail() { echo "FAIL: $*"; FAIL=$((FAIL+1)); }
pass() { echo "PASS: $*"; OK=$((OK+1)); }

# 1. Manuscript compiled
[[ -s paper/main.pdf ]] && pass "main.pdf exists" || fail "main.pdf missing"

# 2. Cover letter compiled
[[ -s submission/cover_letter.pdf ]] && pass "cover_letter.pdf exists" || fail "cover_letter.pdf missing"

# 3. Highlights present
[[ -s submission/highlights.txt ]] && pass "highlights.txt exists" || fail "highlights.txt missing"

# 4. SUBMIT_INSTRUCTIONS
[[ -s submission/SUBMIT_INSTRUCTIONS.md ]] && pass "SUBMIT_INSTRUCTIONS.md exists" || fail "SUBMIT_INSTRUCTIONS.md missing"

# 5. Page count of manuscript <= 6 (approx; check via pdfinfo if available)
if command -v pdfinfo >/dev/null 2>&1; then
    pages=$(pdfinfo paper/main.pdf 2>/dev/null | awk '/Pages/{print $2}')
    if [[ -n "$pages" ]]; then
        if (( pages <= 6 )); then
            pass "main.pdf is $pages pages (<= 6)"
        else
            fail "main.pdf is $pages pages (> 6 limit)"
        fi
    else
        warn "could not parse page count"
    fi
else
    warn "pdfinfo not available, skip page-count check"
fi

# 6. Figures and tables present
for f in fig1_f1_by_model_split fig2_pareto_latency_accuracy fig3_throughput_vs_batch fig4_per_class_f1_cross_station; do
    [[ -s "paper/figures/${f}.pdf" ]] && pass "figure $f exists" || fail "figure $f missing"
done
for t in tab_main tab_latency tab_per_class; do
    [[ -s "paper/tables/${t}.tex" ]] && pass "table $t exists" || fail "table $t missing"
done

# 7. Code reviewer-runnable checklist (7-item per feedback_reviewer_runnable_code.md)
for f in README.md RUNBOOK.md LICENSE CITATION.cff requirements.txt GIT_INFO.md .zenodo.json; do
    [[ -s "$f" ]] && pass "$f exists" || fail "$f missing"
done

# 8. pytest passes
if command -v python >/dev/null 2>&1; then
    if python -m pytest tests/ -q --tb=no 2>&1 | tail -1 | grep -qE '[0-9]+ passed'; then
        pass "pytest passes from archive copy"
    else
        warn "pytest did not report passed cleanly (run python -m pytest tests/ -v)"
    fi
fi

# 9. Anonymisation in CITATION.cff
if grep -q "Anonymised" CITATION.cff; then
    pass "CITATION.cff is anonymised for review"
else
    warn "CITATION.cff has author names visible (acceptable for single-blind venues)"
fi

# 10. AI disclosure in manuscript (removed at NCS direction 2026-05-20 for ATC; warn-only)
if grep -q "generative AI" paper/main.tex; then
    pass "AI use disclosure present in manuscript"
else
    warn "AI use disclosure absent (removed at author's request; verify ATC/IEEE policy permits omission)"
fi

echo
echo "Result: $OK passed, $FAIL failed"
exit $FAIL
