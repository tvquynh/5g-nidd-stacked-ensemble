# Final report template (fill at end-of-task)

Per `feedback_paper_work_final_report_format.md`. Em fill after stacked sweep
finishes and final zip is built.

---

## Rev 0 deliverables (synced)

| Asset | Path |
|---|---|
| Manuscript PDF | `paper/main.pdf` (?? pages) |
| Submission zip | `submission/atc_2026_YYYYMMDD.zip` (?? MB) |
| Git tag | `submit-ready-atc-2026` on `tvquynh/5g-nidd-stacked-ensemble` |
| GitHub repo | https://github.com/tvquynh/5g-nidd-stacked-ensemble |
| Zenodo DOI | 10.5281/zenodo.XXXXXXX |
| OneDrive archive | `E:/OneDrive - rtwv/project/p_atc_2026_5g_stacked/` |
| Tracker update | n/a (đồng nghiệp paper, không thuộc PhD portfolio v4.5.2) |

## NCS paths

```text
📄 Manuscript:   E:\phase3\scripts\side_projects\atc_2026_conf\paper\main.pdf
📦 Submit zip:   E:\phase3\scripts\side_projects\atc_2026_conf\submission\atc_2026_YYYYMMDD.zip
📦 OneDrive:     E:\OneDrive - rtwv\project\p_atc_2026_5g_stacked\
🐙 GitHub:       https://github.com/tvquynh/5g-nidd-stacked-ensemble (tag submit-ready-atc-2026)
```

## Summary (Vietnamese)

Em đã hoàn tất paper ATC 2026 "Lightweight Stacked Ensemble for AI-Enabled 5G
Network Intrusion Detection" (6 trang IEEE conference, EDAS https://edas.info/N35288,
deadline 30/05/2026); package gồm manuscript PDF, source LaTeX, code reviewer-runnable
trên GitHub public, DOI Zenodo, cover letter và SUBMIT_INSTRUCTIONS để đồng nghiệp tự
upload EDAS.

## Risks flagged

1. **Override memory rules (one-off):** `feedback_venue_blacklist_2026_05_16.md`
   (conf-only-FDSE) và `feedback_papers_accept_after_april_2027.md` (HOLD until
   April 2027) tạm thời không apply cho paper hộ đồng nghiệp này. Memory KHÔNG
   được update để giữ blacklist cho future PhD work.

2. **Dual-submission watch:** Paper ATC re-uses 5G-NIDD dataset + base
   preprocessing từ `jisa_5g_bonus` (đang plan submit JISA Elsevier). Em đã design
   ATC paper có contribution **KHÁC** (heterogeneous shallow stacking + latency
   Pareto vs JISA's 5-contribution comprehensive eval). Nhưng đồng nghiệp khi
   nhận zip nên xem xét: (a) coordinate với NCS để tránh self-overlap, (b) hoặc
   thay dataset thực sự nếu cần safety.

3. **Author info tạm:** Em dùng team PhD NCS (Trinh / Huynh T.T. corresponding /
   Huynh D.T. / Le N.H.). Đồng nghiệp PHẢI sửa author list trước khi submit
   EDAS, theo NCS chốt "đồng nghiệp sẽ sửa lại sau".

4. **Compute footprint:** Bases ?? metrics × seeds, stacked ?? metrics × seeds
   trên mllab63 (60c/256GB). KHÔNG sửa code `jisa_5g_bonus` (đang in pipeline).

5. **Memory rule respected:** Em vẫn áp dụng code audit 2-pass, reviewer-runnable
   code, Office Blue figure palette, sequential 1-by-1 audit, 5G-NIDD
   class-coverage disclosure, anonymise GitHub during review.
