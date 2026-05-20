#!/usr/bin/env bash
# Pull figures, tables, and aggregated CSVs from the server back to the
# Windows workspace so the LaTeX manuscript can be recompiled locally.
#
# Usage (from Windows / Git Bash, in the workspace root):
#   bash scripts/sync_artifacts_back.sh
set -euo pipefail

cd "$(dirname "$0")/.."

WORKSPACE=$(pwd)
SERVER="mllab63:/home/apps/papers/atc_2026_conf"

echo "[sync] figures -> $WORKSPACE/paper/figures"
scp -q "$SERVER/results/figures/*.pdf" "$WORKSPACE/paper/figures/"

echo "[sync] tables -> $WORKSPACE/paper/tables"
scp -q "$SERVER/results/tables/*.tex" "$WORKSPACE/paper/tables/"

echo "[sync] aggregated CSV -> $WORKSPACE/results"
mkdir -p "$WORKSPACE/results"
scp -q "$SERVER/results/summary.csv" \
       "$SERVER/results/summary_means.csv" \
       "$SERVER/results/latency_summary.csv" \
       "$WORKSPACE/results/"

echo "[sync] done"
ls -la "$WORKSPACE/paper/figures" "$WORKSPACE/paper/tables"
