#!/usr/bin/env bash
# Full sweep: 10 seeds (project convention) x {random, cross_station BS1}
# for each base learner; 10 seeds x {random, cross_station BS1} for stacked.
#
# Wall-clock estimate on mllab63 (60 cores, 256 GB RAM):
#   - base learners: ~2 min / run * 80 runs ~ 2.5 h
#   - stacked      : ~25 min / run * 20 runs ~ 8 h  (5-fold OOF x 3 bases + refit)
# Run sequentially to keep memory headroom; no SLURM, no nohup loop.
set -euo pipefail

cd "$(dirname "$0")/.."
source /home/apps/venv/bin/activate

SEEDS=(42 123 456 789 1011 2026 3141 4242 5555 6789)
SPLITS=("random" "cross_station")

echo "[run_all] starting at $(date)"

for split in "${SPLITS[@]}"; do
    extra=""
    if [[ "$split" == "cross_station" ]]; then
        extra="--train-bs 1"
    fi
    for seed in "${SEEDS[@]}"; do
        for model in lightgbm xgboost mlp; do
            tag="${model}_${split}_seed${seed}"
            echo "[run_all] $tag"
            python -m src.run_experiment --model "$model" --split "$split" --seed "$seed" $extra
        done
    done
done

# Stacked second (slow): all seeds for both splits
for split in "${SPLITS[@]}"; do
    extra=""
    if [[ "$split" == "cross_station" ]]; then
        extra="--train-bs 1"
    fi
    for seed in "${SEEDS[@]}"; do
        echo "[run_all] stacked_${split}_seed${seed}"
        python -m src.run_experiment --model stacked --split "$split" --seed "$seed" $extra
    done
done

echo "[run_all] aggregating..."
python -m src.aggregate
python -m src.viz
python -m src.make_tables

echo "[run_all] done at $(date)"
