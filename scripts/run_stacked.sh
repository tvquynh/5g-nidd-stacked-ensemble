#!/usr/bin/env bash
# Phase 2: stacked ensemble across all 10 seeds x 2 splits.
# Wall-clock estimate ~8 h on a 60-core, 256 GB RAM host.
set -euo pipefail

cd "$(dirname "$0")/.."
source /home/apps/venv/bin/activate

SEEDS=(42 123 456 789 1011 2026 3141 4242 5555 6789)
SPLITS=("random" "cross_station")

echo "[stacked] starting at $(date)"
for split in "${SPLITS[@]}"; do
    extra=""
    [[ "$split" == "cross_station" ]] && extra="--train-bs 1"
    for seed in "${SEEDS[@]}"; do
        tag="stacked_${split}_seed${seed}"
        t0=$(date +%s)
        python -m src.run_experiment --model stacked --split "$split" --seed "$seed" $extra \
            >> logs/stacked.log 2>&1
        dt=$(( $(date +%s) - t0 ))
        echo "[stacked] ${tag} done in ${dt}s"
    done
done
echo "[stacked] finished at $(date)"
