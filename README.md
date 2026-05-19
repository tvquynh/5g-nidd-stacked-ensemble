# ATC 2026 — Lightweight Stacked Ensemble for 5G NIDS

Reviewer-runnable artefact for the manuscript *"Lightweight Stacked Ensemble for
AI-Enabled 5G Network Intrusion Detection: A Latency-Accuracy Pareto Analysis"*
submitted to the 2026 International Conference on Advanced Technologies for
Communications (ATC 2026), Special Session "AI-Enabled 5G/6G Communication
Systems".

## Contribution summary

We evaluate a **heterogeneous shallow stacked ensemble** for multi-class attack
detection on the public 5G-NIDD dataset. The ensemble combines LightGBM,
XGBoost, and a two-layer MLP through out-of-fold (OOF) cross-validated
probability stacking with a logistic-regression meta-learner. We report:

1. **Classification quality** — macro-F1, weighted-F1, binary-F1, FPR — under
   a stratified random split and a cross-station split (BS1$\to$BS2) that
   stresses generalisation across base stations.
2. **A latency–accuracy Pareto analysis** quantifying the per-sample
   inference cost of each component and the full stack, across batch sizes
   spanning $\{1, 16, 64, 256, 1024, 4096\}$.
3. **A deployment recommendation table** mapping operating points (latency
   budget, accuracy floor) to the configuration that meets them.

## Data foundation

The 5G-NIDD dataset (Samarakoon et al., *IEEE Data Descriptions* 2025;
arXiv:2212.01298) ships an author-curated `Encoded.csv` with 1,215,890 flows,
89 features after the upstream cleaning pipeline, and 9 labels (Benign +
8 attack families) collected from two base stations over two capture days.
This artefact reads the master parquet built once by the upstream
preprocessing step; no rescan/recheck labels are used.

## Layout

```
configs/        paths, model hyperparameters, seeds
src/            data I/O, splits, base learners, stacking, latency, metrics, viz, tables
scripts/        smoke.sh, run_all.sh
paper/          IEEE 6-page LaTeX source + figures + tables
results/        metrics JSON, aggregated CSV, figures, tables (re-generated)
submission/     submit-ready zip + cover letter + SUBMIT_INSTRUCTIONS.md
```

## Reproduce

See `RUNBOOK.md` for end-to-end commands. Quick start (on the server):

```bash
source /home/apps/venv/bin/activate
bash scripts/smoke.sh           # ~5 minutes
bash scripts/run_all.sh         # ~7 hours on a 60-core, 256 GB RAM CPU host
```

## Hardware

All experiments run on a single Linux host with 60 cores and 256 GB RAM, no
GPU. Reported latency numbers are CPU-only.

## Citation

See `CITATION.cff`. Reviewer-anonymised metadata is stored in `.zenodo.json`
and restored to the public author list after acceptance via the
`.restore-on-accept/` directory.

## Licence

MIT, see `LICENSE`.
