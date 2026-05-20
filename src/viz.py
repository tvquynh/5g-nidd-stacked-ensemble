"""Figures for ATC 2026 paper. All plots use the project Office Blue palette
(feedback_figure_palette_ieee_template.md): no red, no grey, no hatches.

Produced figures:
    1. macro_f1 bar chart with std error bars per model and split
    2. latency-accuracy Pareto frontier (per model, median over seeds)
    3. throughput vs batch size line plot (per model)
    4. per-class F1 heatmap for the stacked ensemble vs best single base
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
import sys

import matplotlib as mpl
mpl.use("Agg")  # headless on server
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.io_utils import load_paths, load_class_names


PALETTE = {
    "headline":  "#1F4E79",  # navy
    "baseline":  "#2E75B6",
    "variant_a": "#9DC3E6",
    "variant_b": "#BDD7EE",
    "band":      "#EAF1F7",
}
MODEL_COLOR = {
    "stacked":   PALETTE["headline"],
    "lightgbm":  PALETTE["baseline"],
    "xgboost":   PALETTE["variant_a"],
    "mlp":       PALETTE["variant_b"],
}
MODEL_MARKER = {
    "stacked":  ("D", "-"),
    "lightgbm": ("o", "--"),
    "xgboost":  ("s", "-."),
    "mlp":      ("^", ":"),
}
MODEL_LABEL = {
    "stacked":  "Stacked ensemble (proposed)",
    "lightgbm": "LightGBM",
    "xgboost":  "XGBoost",
    "mlp":      "MLP",
}


def style():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.linewidth": 0.6,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.grid": True,
        "grid.linestyle": ":",
        "grid.alpha": 0.45,
        "grid.color": "#BFBFBF",
        "legend.frameon": False,
        "legend.fontsize": 8,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    })


def fig_f1_bars(summary_means: pd.DataFrame, out: Path):
    rows = summary_means.copy()
    if "macro_f1__count" in rows.columns:
        rows = rows[rows["macro_f1__count"].notna()]
    splits = ["random", "cross_station"]
    models = ["lightgbm", "xgboost", "mlp", "stacked"]
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    width = 0.18
    x = np.arange(len(splits))
    for i, m in enumerate(models):
        means, stds = [], []
        for sp in splits:
            row = rows[(rows["model"] == m) & (rows["split"] == sp)]
            if sp == "cross_station":
                row = row[row["train_bs"] == 1]
            if row.empty:
                means.append(np.nan); stds.append(0.0); continue
            means.append(float(row["macro_f1__mean"].iloc[0]))
            stds.append(float(row["macro_f1__std"].iloc[0]) if pd.notna(row["macro_f1__std"].iloc[0]) else 0.0)
        ax.bar(x + (i - 1.5) * width, means, width=width,
               yerr=stds, capsize=2,
               color=MODEL_COLOR[m], edgecolor="white", linewidth=0.4,
               label=MODEL_LABEL[m])
    ax.set_xticks(x)
    ax.set_xticklabels(["Random split", "Cross-station (BS1$\\rightarrow$BS2)"])
    ax.set_ylabel("Macro-F1 (mean $\\pm$ 1 std, 10 seeds)")
    ax.set_ylim(0.85, 1.02)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.22), fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=400, bbox_inches="tight")
    plt.close(fig)


def fig_pareto(summary: pd.DataFrame, latency: pd.DataFrame, out: Path,
               split: str = "random", batch_size: int = 256):
    sub_acc = summary[(summary["split"] == split) & (~summary["smoke"].astype(bool))]
    sub_lat = latency[(latency["split"] == split) & (latency["batch_size"] == batch_size)]

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    for m in ["lightgbm", "xgboost", "mlp", "stacked"]:
        f1_vals = sub_acc[sub_acc["model"] == m]["macro_f1"].dropna().values
        lat_vals = sub_lat[sub_lat["model"] == m]["per_sample_us"].dropna().values
        if len(f1_vals) == 0 or len(lat_vals) == 0:
            continue
        f1 = float(np.median(f1_vals))
        lat = float(np.median(lat_vals))
        marker, ls = MODEL_MARKER[m]
        ax.scatter([lat], [f1], s=70, marker=marker, color=MODEL_COLOR[m],
                   edgecolor=PALETTE["headline"], linewidth=0.6,
                   label=MODEL_LABEL[m], zorder=3)
    ax.set_xscale("log")
    ax.set_xlabel(f"Per-sample latency at batch={batch_size} (µs, log scale)")
    ax.set_ylabel("Macro-F1 (median, 10 seeds)")
    ax.set_ylim(0.95, 1.005)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=2, fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=400, bbox_inches="tight")
    plt.close(fig)


def fig_throughput_curves(latency: pd.DataFrame, out: Path, split: str = "random"):
    sub = latency[latency["split"] == split].copy()
    fig, ax = plt.subplots(figsize=(3.5, 2.3))
    for m in ["lightgbm", "xgboost", "mlp", "stacked"]:
        g = sub[sub["model"] == m].groupby("batch_size")["throughput_samples_per_sec"].median()
        if g.empty:
            continue
        marker, ls = MODEL_MARKER[m]
        ax.plot(g.index, g.values, marker=marker, linestyle=ls,
                color=MODEL_COLOR[m], label=MODEL_LABEL[m],
                linewidth=1.3, markersize=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Batch size")
    ax.set_ylabel("Throughput (flows/sec)")
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=400, bbox_inches="tight")
    plt.close(fig)


def fig_per_class_f1(metrics_dir: Path, classes: List[str], out: Path,
                     split: str = "cross_station", train_bs: int = 1):
    """Horizontal grouped bar chart of per-class F1 (median over seeds) — legend
    placed above the plot so it never overlaps the class names on the y-axis.
    """
    models = ["lightgbm", "xgboost", "mlp", "stacked"]
    suffix = f"_bs{train_bs}" if split == "cross_station" else ""
    rows = []
    for m in models:
        per_class_f1 = {c: [] for c in classes}
        for f in metrics_dir.glob(f"{m}_{split}{suffix}_seed*.json"):
            data = json.loads(f.read_text())
            if data.get("smoke"):
                continue
            pc = data.get("per_class", {})
            for c in classes:
                if c in pc:
                    per_class_f1[c].append(pc[c]["f1"])
        for c in classes:
            vals = per_class_f1[c]
            if vals:
                rows.append({"model": m, "class": c, "f1": float(np.median(vals))})
    df = pd.DataFrame(rows)
    if df.empty:
        return
    pivot = df.pivot(index="class", columns="model", values="f1").reindex(classes)
    fig, ax = plt.subplots(figsize=(7.1, 2.6))
    y = np.arange(len(classes))
    height = 0.20
    for i, m in enumerate(models):
        if m not in pivot.columns:
            continue
        vals = pivot[m].values
        ax.barh(y + (i - 1.5) * height, vals, height=height,
                color=MODEL_COLOR[m], edgecolor="white", linewidth=0.4,
                label=MODEL_LABEL[m])
    ax.set_yticks(y)
    ax.set_yticklabels(classes, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Per-class F1 (median)")
    ax.set_xlim(0.0, 1.05)
    ax.legend(ncol=4, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    fig.savefig(out, dpi=400, bbox_inches="tight")
    plt.close(fig)


def main():
    style()
    paths = load_paths()
    classes = load_class_names()
    out_root = Path(paths["results"])
    fig_dir = out_root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    summary = pd.read_csv(out_root / "summary.csv")
    means = pd.read_csv(out_root / "summary_means.csv")
    latency = pd.read_csv(out_root / "latency_summary.csv")

    fig_f1_bars(means, fig_dir / "fig1_f1_by_model_split.pdf")
    fig_pareto(summary, latency, fig_dir / "fig2_pareto_latency_accuracy.pdf",
               split="random", batch_size=256)
    fig_throughput_curves(latency, fig_dir / "fig3_throughput_vs_batch.pdf", split="random")
    fig_per_class_f1(out_root / "metrics", classes,
                     fig_dir / "fig4_per_class_f1_cross_station.pdf",
                     split="cross_station", train_bs=1)
    print(f"[viz] wrote 4 figures into {fig_dir}")


if __name__ == "__main__":
    main()
