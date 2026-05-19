# PAPER_INFO.md (OneDrive archive template)

Em fill numbers/dates after stacked sweep finishes. Saved into
`E:/OneDrive - rtwv/project/p_atc_2026_5g_stacked/PAPER_INFO.md`.

---

# Paper Info — ATC 2026 5G-NIDD Stacked Ensemble

## Quick reference

| Field | Value |
|---|---|
| Working title | Lightweight Stacked Ensemble for AI-Enabled 5G Network Intrusion Detection: A Latency-Accuracy Pareto Analysis |
| Target venue | 2026 International Conference on Advanced Technologies for Communications (ATC 2026) |
| Special session | AI-Enabled 5G/6G Communication Systems (primary), Network Operations and Management (backup) |
| Submission system | EDAS — https://edas.info/N35288 |
| Initial deadline | 30 May 2026 |
| Notification | 30 July 2026 |
| Camera-ready | 15 August 2026 |
| Conference dates | 15--17 October 2026, Gia Lai, Vietnam |
| Page limit | 6 pages |
| Format | IEEE conference (IEEEtran) |
| Status | Submit-ready (ng??y MM/DD/YYYY) — pending colleague hand-off |
| Tracker entry | n/a (?đ?ng nghi?p paper, kh?ng thu?c PhD portfolio v4.5.2) |

## Authors (placeholder, to be revised by colleague)

| Order | Name | Affiliation | Email | ORCID |
|---|---|---|---|---|
| 1 | Van-Quynh Trinh | PTIT | tvquynh@ptit.edu.vn | 0009-0006-0514-6123 |
| 2 (corr) | Trong-Thua Huynh | PTIT | huynhtrongthua@ptit.edu.vn | 0000-0003-3934-1067 |
| 3 | De-Thu Huynh | SIU | -- | 0000-0002-1227-0281 |
| 4 | Ngoc-Hieu Le | PTIT | -- | -- |

## Contributions

1. Heterogeneous shallow stacked ensemble (LightGBM + XGBoost + MLP -> logistic-regression meta-learner) with leakage-free OOF probability stacking.
2. Two evaluation regimes: stratified random split (in-distribution) and cross-base-station BS1->BS2 with per-class prior rebalance.
3. Latency-accuracy Pareto analysis across six batch sizes {1, 16, 64, 256, 1024, 4096} on a commodity 60-core CPU host; three-tier deployment recommendation table.

## Dataset

- 5G-NIDD (Samarakoon et al., arXiv:2212.01298; IEEE Data Descriptions 2025)
- 1,215,890 flows; 89 numeric features; 9 labels (1 benign + 8 attacks); 2 base stations; 2 capture days
- CC BY 4.0

## Headline numbers (fill after sweep)

| Metric | Random | Cross-station BS1->BS2 |
|---|---|---|
| Stacked macro-F1 | ?? | ?? |
| Stacked binary FPR | ?? | ?? |
| Best single base macro-F1 | ?? (??) | ?? (??) |
| Stacked vs best base gap | ?? | ?? |
| Stacked per-sample latency @\,b=256 | ?? µs | -- |
| Stacked throughput @\,b=1024 | ?? flows/sec | -- |

## Hardware / software

- mllab63 (10.10.26.63): Xeon Gold 6130, 60 cores, 256 GB RAM, no GPU
- Python 3.10, scikit-learn 1.7.2, LightGBM 4.6.0, XGBoost 3.2.0, NumPy 2.2.6, pandas 2.3.3
- 10 seeds: {42, 123, 456, 789, 1011, 2026, 3141, 4242, 5555, 6789}

## Risks flagged in final report

1. Override `feedback_venue_blacklist_2026_05_16.md` and `feedback_papers_accept_after_april_2027.md` one-off; memory NOT updated.
2. Dual-submission watch with `jisa_5g_bonus` (JISA Elsevier plan). Differentiation: ATC focuses on stacking + Pareto; JISA covers 5 broad contributions including SHAP + holdout-attack. No shared figures/tables; no shared captions.
3. Author list is placeholder; colleague must revise pre-submit.
4. Repository anonymised during review; canonical metadata in `.restore-on-accept/`.

## Pointers

- Working repo: E:/phase3/scripts/side_projects/atc_2026_conf/
- GitHub: https://github.com/tvquynh/5g-nidd-stacked-ensemble (tag `submit-ready-atc-2026`)
- Zenodo: 10.5281/zenodo.XXXXXXX (minted at submit-ready)
- Server workspace: /home/apps/papers/atc_2026_conf/ (mllab63)
- Data source: /home/apps/papers/jisa_5g_bonus/data/master_5g_nidd.parquet (read-only)
