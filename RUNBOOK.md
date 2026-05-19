# RUNBOOK — ATC 2026 Stacked NIDS

End-to-end operational guide for reproducing every number and figure in the
manuscript. Times are wall-clock on a 60-core, 256 GB RAM CPU server.

## 1. Pre-flight

```bash
# venv with pinned versions (already on the server)
source /home/apps/venv/bin/activate
python -c "import lightgbm, xgboost, sklearn, pandas; \
           print(lightgbm.__version__, xgboost.__version__, sklearn.__version__, pandas.__version__)"
# expected: 4.6.0 3.2.0 1.7.2 2.3.3

# master parquet (read-only) must exist
ls -lh /home/apps/papers/jisa_5g_bonus/data/master_5g_nidd.parquet
# expected: ~150 MB, 1,215,890 rows
```

If the master parquet is missing, follow Section 7 (Data acquisition) below
to rebuild it from the 5G-NIDD `Encoded.csv` distribution.

## 2. Smoke test (≈5 min)

```bash
bash scripts/smoke.sh
ls results/metrics/ | grep _smoke -c  # expect 5 files
```

Pass criterion: every JSON shows `macro_f1 > 0.85` on the 30k subset. If a
file is missing or macro-F1 < 0.65, stop and debug `src/run_experiment.py`
before launching the full sweep.

## 3. Full sweep (≈7 h)

```bash
nohup bash scripts/run_all.sh > logs/run_all.log 2>&1 &
echo $! > logs/run_all.pid

# progress (file count grows from 0 -> 80)
while ps -p $(cat logs/run_all.pid) >/dev/null; do
    echo "$(date '+%H:%M:%S') $(ls results/metrics/ 2>/dev/null | wc -l) metrics produced"
    sleep 60
done
```

Expected output volume: 10 seeds × 2 splits × 4 models = 80 JSON files plus
the smoke files from Section 2 (the smoke files are filtered out by
`src.aggregate`).

## 4. Aggregate + figures + tables

`run_all.sh` already calls these. To run them manually after a sweep:

```bash
python -m src.aggregate            # writes results/{summary,summary_means,latency_summary}.csv
python -m src.viz                  # writes results/figures/{fig1..fig4}.pdf
python -m src.make_tables          # writes results/tables/tab_{main,latency,per_class}.tex
```

## 5. Expected outputs

| Path | Description |
|---|---|
| `results/summary.csv` | one row per JSON (80 rows + 5 smoke filtered) |
| `results/summary_means.csv` | grouped mean / std / count per (model, split, train_bs) |
| `results/latency_summary.csv` | per-batch median latency + throughput |
| `results/figures/fig1_f1_by_model_split.pdf` | bar chart |
| `results/figures/fig2_pareto_latency_accuracy.pdf` | latency–accuracy Pareto |
| `results/figures/fig3_throughput_vs_batch.pdf` | throughput vs batch size |
| `results/figures/fig4_per_class_f1_cross_station.pdf` | per-class F1 |
| `results/tables/tab_main.tex` | quality table |
| `results/tables/tab_latency.tex` | latency table |
| `results/tables/tab_per_class.tex` | per-class F1 table |
| `paper/main.pdf` | compiled manuscript |

## 6. Test (sanity)

```bash
pytest -q tests/
```

Tests cover: split idempotence, stacking leakage-free OOF, latency
profile shape, classes JSON coverage.

## 7. Data acquisition (only if master parquet is absent)

The dataset is **5G-NIDD** (Samarakoon et al., *IEEE Data Descriptions* 2025).
Obtain `Encoded.csv` (≈1.2M rows, 96 columns) from
https://ieee-dataport.org/documents/5g-nidd-comprehensive-network-intrusion-detection-dataset-generated-over-5g-wireless
under CC BY 4.0. Then build the master parquet:

```bash
source /home/apps/venv/bin/activate
python -m src.build_master \
    --encoded-csv /path/to/Encoded.csv \
    --out-parquet /home/apps/papers/jisa_5g_bonus/data/master_5g_nidd.parquet \
    --out-classes /home/apps/papers/jisa_5g_bonus/data/master_5g_nidd.classes.json
```

The resulting schema is documented in `src/io_utils.py::load_master` and
`src/build_master.py`: 89 numeric features plus `y_multi`, `y_binary`,
`BS`, `capture_day`. The output path can be redirected by editing
`configs/paths.yaml` (`server.master_parquet`).

## 8. Troubleshooting

| Symptom | Diagnosis | Fix |
|---|---|---|
| `FileNotFoundError master_5g_nidd.parquet` | Server master parquet path changed | edit `configs/paths.yaml` |
| `macro_f1` random < 0.65 on smoke | Label encoding drift | `python -c "import pandas as pd; print(pd.read_parquet('/home/apps/papers/jisa_5g_bonus/data/master_5g_nidd.parquet')['y_multi'].value_counts())"` |
| `MemoryError` during stacked fit | XGBoost+LightGBM hold full DMatrix in RAM | reduce parallel `num_threads` from 16 to 8 in `configs/models.yaml` |
| Latency profile noisy (>20 % CV) | Shared host contention | increase `n_repeats` in `src/run_experiment.py::LATENCY_BATCHES` |
| LaTeX undefined reference | tables / figures regenerated after compile | `pdflatex` twice |
