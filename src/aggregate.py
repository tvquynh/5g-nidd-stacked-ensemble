"""Aggregate per-(model, split, seed) JSON metrics into a single summary table.

Output:
    results/summary.csv
    results/summary_means.csv     (mean + std per (model, split))
    results/latency_summary.csv   (median per (model, batch_size, split))
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.io_utils import load_paths


SCALAR_COLS = (
    "macro_f1", "weighted_f1",
    "binary_precision", "binary_recall", "binary_f1", "binary_fpr",
    "binary_tpr",
    "macro_roc_auc", "macro_pr_auc",
    "fit_time_sec", "inference_time_sec", "inference_throughput_per_sec",
    "n_train", "n_test", "n_features", "num_classes",
)


def load_one(p: Path) -> Dict:
    data = json.loads(p.read_text())
    row = {
        "file": p.name,
        "model": data.get("model"),
        "split": data.get("split"),
        "seed": data.get("seed"),
        "train_bs": data.get("train_bs"),
        "smoke": bool(data.get("smoke", False)),
    }
    for c in SCALAR_COLS:
        row[c] = data.get(c)
    return row, data


def build_summary(metrics_dir: Path) -> pd.DataFrame:
    rows = []
    for f in sorted(metrics_dir.glob("*.json")):
        row, _ = load_one(f)
        rows.append(row)
    return pd.DataFrame(rows)


def build_latency_table(metrics_dir: Path) -> pd.DataFrame:
    rows = []
    for f in sorted(metrics_dir.glob("*.json")):
        data = json.loads(f.read_text())
        if data.get("smoke"):
            continue
        model = data.get("model")
        split = data.get("split")
        seed = data.get("seed")
        train_bs = data.get("train_bs")
        prof = data.get("latency_profile", []) or []
        for entry in prof:
            rows.append({
                "model": model,
                "split": split,
                "seed": seed,
                "train_bs": train_bs,
                "batch_size": entry["batch_size"],
                "median_ms_per_batch": entry["median_ms_per_batch"],
                "per_sample_us": entry["per_sample_us"],
                "throughput_samples_per_sec": entry["throughput_samples_per_sec"],
            })
        for base_name, base_prof in (data.get("base_latency_profile") or {}).items():
            for entry in base_prof:
                rows.append({
                    "model": base_name + "_in_stack",
                    "split": split,
                    "seed": seed,
                    "train_bs": train_bs,
                    "batch_size": entry["batch_size"],
                    "median_ms_per_batch": entry["median_ms_per_batch"],
                    "per_sample_us": entry["per_sample_us"],
                    "throughput_samples_per_sec": entry["throughput_samples_per_sec"],
                })
    return pd.DataFrame(rows)


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df["smoke"].astype(bool)]
    key = ["model", "split", "train_bs"]
    metrics_cols = [c for c in df.columns
                    if c not in {"file", "model", "split", "seed", "train_bs", "smoke"}
                    and pd.api.types.is_numeric_dtype(df[c])]
    grouped = df.groupby(key, dropna=False)[metrics_cols].agg(["mean", "std", "count"])
    grouped.columns = ["__".join(c) for c in grouped.columns]
    return grouped.reset_index()


def main():
    paths = load_paths()
    out_root = Path(paths["results"])
    metrics_dir = out_root / "metrics"
    if not metrics_dir.exists():
        raise FileNotFoundError(metrics_dir)

    summary = build_summary(metrics_dir)
    summary.to_csv(out_root / "summary.csv", index=False)
    print(f"[summary] wrote {out_root / 'summary.csv'} ({len(summary)} rows)")

    means = summarise(summary)
    means.to_csv(out_root / "summary_means.csv", index=False)
    print(f"[summary] wrote {out_root / 'summary_means.csv'} ({len(means)} rows)")

    latency = build_latency_table(metrics_dir)
    latency.to_csv(out_root / "latency_summary.csv", index=False)
    print(f"[summary] wrote {out_root / 'latency_summary.csv'} ({len(latency)} rows)")


if __name__ == "__main__":
    main()
