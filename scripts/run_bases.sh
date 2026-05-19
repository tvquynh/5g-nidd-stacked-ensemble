#!/usr/bin/env bash
# Phase 1: base learners across all 10 seeds x 2 splits.
# Wall-clock estimate ~1.5 h on a 60-core, 256 GB RAM host.
set -euo pipefail

cd "$(dirname "$0")/.."
source /home/apps/venv/bin/activate

SEEDS=(42 123 456 789 1011 2026 3141 4242 5555 6789)
SPLITS=("random" "cross_station")
MODELS=("lightgbm" "xgboost" "mlp")

echo "[bases] starting at $(date)"
for split in "${SPLITS[@]}"; do
    extra=""
    [[ "$split" == "cross_station" ]] && extra="--train-bs 1"
    for seed in "${SEEDS[@]}"; do
        for model in "${MODELS[@]}"; do
            tag="${model}_${split}_seed${seed}"
            t0=$(date +%s)
            python -m src.run_experiment --model "$model" --split "$split" --seed "$seed" $extra \
                >> logs/bases.log 2>&1
            dt=$(( $(date +%s) - t0 ))
            echo "[bases] ${tag} done in ${dt}s"
        done
    done
done
echo "[bases] finished at $(date)"
