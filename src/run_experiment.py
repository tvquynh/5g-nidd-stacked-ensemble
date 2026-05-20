"""Main entry point: train + evaluate one (model, split, seed) configuration.

CLI:
    python -m src.run_experiment --model stacked --split random --seed 42
    python -m src.run_experiment --model lightgbm --split cross_station --train-bs 1 --seed 42

Output: results/metrics/<model>_<split>[_bs<X>]_seed<seed>.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.io_utils import load_master, load_class_names, load_paths
from src.splits import get_split
from src.base_models import build_base
from src.stacking import StackedEnsemble, BASE_NAMES
from src.metrics_utils import aggregate
from src.latency import profile_throughput


MODEL_CHOICES = ("lightgbm", "xgboost", "mlp", "stacked")
SPLIT_CHOICES = ("random", "cross_station")
LATENCY_BATCHES = (1, 16, 64, 256, 1024, 4096)


def numpy_to_python(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: numpy_to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [numpy_to_python(x) for x in obj]
    return obj


def get_feature_matrix(df, feature_cols):
    return df[feature_cols].values.astype(np.float32)


def get_feature_columns(df) -> list:
    meta = {"y_multi", "y_binary", "BS", "capture_day"}
    return [c for c in df.columns if c not in meta]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=MODEL_CHOICES)
    ap.add_argument("--split", required=True, choices=SPLIT_CHOICES)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--train-bs", type=int, default=1, choices=(1, 2))
    ap.add_argument("--smoke", action="store_true", help="subsample to 30k flows for smoke test")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    paths = load_paths()
    classes = load_class_names()
    num_classes = len(classes)

    print(f"[load] master parquet at {paths['master_parquet']}")
    df = load_master()
    print(f"[load] {len(df):,} rows x {len(df.columns)} cols")

    if args.smoke:
        from sklearn.model_selection import StratifiedShuffleSplit
        sss = StratifiedShuffleSplit(n_splits=1, test_size=30_000, random_state=args.seed)
        _, sub = next(sss.split(np.zeros(len(df)), df["y_multi"].values))
        df = df.iloc[sub].reset_index(drop=True)
        print(f"[smoke] subsampled to {len(df):,} rows")

    feature_cols = get_feature_columns(df)
    X = get_feature_matrix(df, feature_cols)
    y = df["y_multi"].values.astype(np.int64)

    print(f"[split] {args.split} seed={args.seed} bs={args.train_bs}")
    train_idx, test_idx = get_split(args.split, df, seed=args.seed, train_bs=args.train_bs)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    print(f"[split] n_train={len(y_train):,} n_test={len(y_test):,}")

    benign_id = classes.index("Benign") if "Benign" in classes else 0

    t_fit0 = time.time()
    if args.model == "stacked":
        ens = StackedEnsemble(num_classes=num_classes, seed=args.seed,
                              k_folds=5, base_names=BASE_NAMES).fit(X_train, y_train)
        fit_time = time.time() - t_fit0
        t_inf0 = time.time()
        proba = ens.predict_proba(X_test)
        inf_time = time.time() - t_inf0
        per_base_time = ens.fit_times
        # latency on test subset
        latency_profile = profile_throughput(
            ens.predict_proba, X_test, list(LATENCY_BATCHES), n_repeats=10
        )
        base_latency = {
            name: profile_throughput(b.predict_proba, X_test, list(LATENCY_BATCHES), n_repeats=10)
            for name, b in zip(BASE_NAMES, ens.bases)
        }
    else:
        base = build_base(name=args.model, num_classes=num_classes, seed=args.seed)
        base.fit(X_train, y_train)
        fit_time = time.time() - t_fit0
        t_inf0 = time.time()
        proba = base.predict_proba(X_test)
        inf_time = time.time() - t_inf0
        per_base_time = {args.model: fit_time}
        latency_profile = profile_throughput(
            base.predict_proba, X_test, list(LATENCY_BATCHES), n_repeats=10
        )
        base_latency = {}

    y_pred = np.argmax(proba, axis=1)
    metrics = aggregate(y_test, y_pred, proba=proba, class_names=classes, benign_class=benign_id)
    metrics.update({
        "model": args.model,
        "split": args.split,
        "seed": args.seed,
        "train_bs": args.train_bs if args.split == "cross_station" else None,
        "smoke": bool(args.smoke),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "n_features": int(X.shape[1]),
        "num_classes": int(num_classes),
        "fit_time_sec": float(fit_time),
        "inference_time_sec": float(inf_time),
        "inference_throughput_per_sec": float(len(y_test) / max(inf_time, 1e-9)),
        "per_component_fit_time_sec": {k: float(v) for k, v in per_base_time.items()},
        "latency_profile": latency_profile,
        "base_latency_profile": base_latency,
        "git_commit": _git_commit_or_none(),
    })

    if args.out:
        out_path = Path(args.out)
    else:
        out_dir = Path(paths["results"]) / "metrics"
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"_bs{args.train_bs}" if args.split == "cross_station" else ""
        smoke_suffix = "_smoke" if args.smoke else ""
        fname = f"{args.model}_{args.split}{suffix}_seed{args.seed}{smoke_suffix}.json"
        out_path = out_dir / fname

    out_path.write_text(json.dumps(numpy_to_python(metrics), indent=2))
    print(f"[done] macro_f1={metrics['macro_f1']:.4f}  binary_f1={metrics['binary_f1']:.4f}  -> {out_path}")


def _git_commit_or_none():
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(Path(__file__).resolve().parent.parent),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return None


if __name__ == "__main__":
    main()
