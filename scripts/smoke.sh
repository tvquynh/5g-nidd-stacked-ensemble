#!/usr/bin/env bash
# Smoke test on a 30k-flow stratified subset. Should complete in ~5 minutes
# on mllab63 and produce one JSON per (model, split). All artifacts are
# written under results/metrics/ with smoke=true so they are excluded from the
# main summary.
set -euo pipefail

cd "$(dirname "$0")/.."
source /home/apps/venv/bin/activate

echo "[smoke] starting at $(date)"
python -m src.run_experiment --model lightgbm --split random --seed 42 --smoke
python -m src.run_experiment --model xgboost  --split random --seed 42 --smoke
python -m src.run_experiment --model mlp      --split random --seed 42 --smoke
python -m src.run_experiment --model stacked  --split random --seed 42 --smoke
python -m src.run_experiment --model stacked  --split cross_station --train-bs 1 --seed 42 --smoke
echo "[smoke] done at $(date)"
