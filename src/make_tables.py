"""LaTeX tables for ATC 2026 paper. Loads aggregated CSVs from results/ and emits
booktabs-style .tex snippets into paper/tables/.

Table 1: Macro-F1 / weighted-F1 / binary-F1 / FPR per model on random + cross-station
Table 2: Latency + throughput at batch sizes {1, 256, 4096} per model
Table 3: Per-class F1 on cross-station BS1->BS2 (best for showing stacked gain)
"""
from __future__ import annotations

from pathlib import Path
from typing import List
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.io_utils import load_paths, load_class_names


MODEL_ORDER = ["lightgbm", "xgboost", "mlp", "stacked"]
MODEL_LABEL = {
    "lightgbm": "LightGBM",
    "xgboost":  "XGBoost",
    "mlp":      "MLP",
    "stacked":  r"Stacked ensemble (\textbf{proposed})",
}


def _fmt(mean, std, k=3):
    if pd.isna(mean):
        return "--"
    if pd.isna(std):
        return f"{mean:.{k}f}"
    return f"{mean:.{k}f}$\\pm${std:.{k}f}"


def table_main(means: pd.DataFrame, out: Path):
    """Macro-F1 / weighted-F1 / binary-F1 / binary-FPR per model × split."""
    splits = [("random", None, "Random split"),
              ("cross_station", 1, r"Cross-station (BS1$\rightarrow$BS2)")]
    metric_cols = [
        ("macro_f1", "Macro-F1"),
        ("weighted_f1", "Weighted-F1"),
        ("binary_f1", "Binary-F1"),
        ("binary_fpr", "Binary FPR"),
    ]

    lines = []
    lines.append(r"\begin{table*}[!t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Classification quality on the 5G-NIDD multi-class task. "
                 r"Mean$\pm$std over the 10 project seeds "
                 r"\{42, 123, 456, 789, 1011, 2026, 3141, 4242, 5555, 6789\}. "
                 r"\emph{Binary-F1} treats the Benign class as the negative class and the eight attack families as the positive class; "
                 r"\emph{Binary FPR} = FP / (FP + TN) under the same binary collapse.}")
    lines.append(r"\label{tab:main}")
    lines.append(r"\begin{tabular}{ll" + "c" * len(metric_cols) + r"}")
    lines.append(r"\toprule")
    header = ["Split", "Model"] + [m[1] for m in metric_cols]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")

    for split_name, train_bs, split_label in splits:
        first_row = True
        for m in MODEL_ORDER:
            row = means[(means["model"] == m) & (means["split"] == split_name)]
            if split_name == "cross_station":
                row = row[row["train_bs"] == train_bs]
            cells = []
            for key, _ in metric_cols:
                mean_col = f"{key}__mean"
                std_col = f"{key}__std"
                if row.empty or mean_col not in row.columns:
                    cells.append("--"); continue
                cells.append(_fmt(row[mean_col].iloc[0],
                                  row[std_col].iloc[0] if std_col in row.columns else np.nan))
            split_cell = split_label if first_row else ""
            lines.append(f"{split_cell} & {MODEL_LABEL[m]} & " + " & ".join(cells) + r" \\")
            first_row = False
        lines.append(r"\midrule")
    # remove last midrule
    if lines[-1] == r"\midrule":
        lines.pop()
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[tab] {out}")


def table_latency(latency: pd.DataFrame, out: Path, split: str = "random"):
    """Median per-sample latency (µs) at batch sizes 1 / 256 / 4096 per model."""
    bs_list = [1, 256, 4096]
    sub = latency[latency["split"] == split]
    lines = []
    lines.append(r"\begin{table}[!t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Inference latency on a 60-core, 256\,GB-RAM CPU server. "
                 r"Median over 10 seeds and 10 timing repetitions; lower is faster.}")
    lines.append(r"\label{tab:latency}")
    lines.append(r"\begin{tabular}{l" + "c" * (len(bs_list) * 2) + r"}")
    lines.append(r"\toprule")
    parts = ["Model"]
    for bs in bs_list:
        parts.append(rf"$\mu$s/flow @\,b={bs}")
        parts.append(rf"thr./sec @\,b={bs}")
    lines.append(" & ".join(parts) + r" \\")
    lines.append(r"\midrule")

    for m in MODEL_ORDER:
        cells = [MODEL_LABEL[m]]
        for bs in bs_list:
            row = sub[(sub["model"] == m) & (sub["batch_size"] == bs)]
            if row.empty:
                cells.append("--"); cells.append("--"); continue
            us = float(np.median(row["per_sample_us"].dropna().values))
            thr = float(np.median(row["throughput_samples_per_sec"].dropna().values))
            cells.append(f"{us:.1f}")
            cells.append(f"{thr/1e3:.1f}k")
        lines.append(" & ".join(cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[tab] {out}")


def table_per_class(metrics_dir: Path, classes: List[str], out: Path,
                    split: str = "cross_station", train_bs: int = 1):
    """Per-class F1 medians for cross-station split (most informative for stacked gain)."""
    import json
    suffix = f"_bs{train_bs}" if split == "cross_station" else ""
    rows = []
    for m in MODEL_ORDER:
        per_cls = {c: [] for c in classes}
        for f in metrics_dir.glob(f"{m}_{split}{suffix}_seed*.json"):
            data = json.loads(f.read_text())
            if data.get("smoke"):
                continue
            pc = data.get("per_class", {})
            for c in classes:
                if c in pc:
                    per_cls[c].append(pc[c]["f1"])
        row = {"model": m}
        for c in classes:
            vals = per_cls[c]
            row[c] = float(np.median(vals)) if vals else np.nan
        rows.append(row)
    if not rows:
        return
    df = pd.DataFrame(rows).set_index("model").reindex(MODEL_ORDER)

    lines = []
    lines.append(r"\begin{table*}[!t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Per-class F1 on cross-station BS1$\rightarrow$BS2 (median over 10 seeds). "
                 r"The MLP excels on the volumetric classes (Benign, UDPFlood) while the gradient-boosted "
                 r"trees and the stacked ensemble dominate the application-layer DoS classes.}")
    lines.append(r"\label{tab:perclass}")
    cols = "l" + "c" * len(classes)
    lines.append(rf"\begin{{tabular}}{{{cols}}}")
    lines.append(r"\toprule")
    header = ["Model"] + classes
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")
    for m in MODEL_ORDER:
        cells = [MODEL_LABEL[m]]
        for c in classes:
            v = df.loc[m, c] if m in df.index else np.nan
            cells.append("--" if pd.isna(v) else f"{v:.3f}")
        lines.append(" & ".join(cells) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[tab] {out}")


def main():
    paths = load_paths()
    out_root = Path(paths["results"])
    tab_dir = out_root / "tables"
    tab_dir.mkdir(parents=True, exist_ok=True)

    means = pd.read_csv(out_root / "summary_means.csv")
    latency = pd.read_csv(out_root / "latency_summary.csv")
    classes = load_class_names()

    table_main(means, tab_dir / "tab_main.tex")
    table_latency(latency, tab_dir / "tab_latency.tex", split="random")
    table_per_class(out_root / "metrics", classes, tab_dir / "tab_per_class.tex",
                    split="cross_station", train_bs=1)


if __name__ == "__main__":
    main()
