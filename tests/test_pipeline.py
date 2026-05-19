"""Minimal smoke tests for the ATC 2026 stacking pipeline.

Tests use small synthetic data so they run in seconds and do not depend on
the 5G-NIDD master parquet being present on the runner.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _toy_df(n_per_class: int = 200, n_features: int = 12, n_classes: int = 4, seed: int = 0):
    rng = np.random.default_rng(seed)
    Xs, ys, bss = [], [], []
    for c in range(n_classes):
        centre = rng.normal(loc=c * 1.5, scale=0.2, size=n_features)
        X = rng.normal(loc=centre, scale=1.0, size=(n_per_class, n_features))
        y = np.full(n_per_class, c, dtype=np.int64)
        bs = rng.integers(low=1, high=3, size=n_per_class)  # 1 or 2
        Xs.append(X); ys.append(y); bss.append(bs)
    X = np.concatenate(Xs); y = np.concatenate(ys); bs = np.concatenate(bss)
    cols = [f"f{i}" for i in range(n_features)]
    df = pd.DataFrame(X.astype(np.float32), columns=cols)
    df["y_multi"] = y
    df["y_binary"] = (y != 0).astype(np.int8)
    df["BS"] = bs.astype(np.int8)
    df["capture_day"] = np.where(y < n_classes // 2, 1, 2).astype(np.int8)
    return df


def test_split_random_idempotent():
    from src.splits import split_random
    df = _toy_df(seed=0)
    tr1, te1 = split_random(df, seed=42)
    tr2, te2 = split_random(df, seed=42)
    assert np.array_equal(tr1, tr2)
    assert np.array_equal(te1, te2)
    assert set(tr1).isdisjoint(set(te1))
    assert len(tr1) + len(te1) == len(df)


def test_cross_station_balanced():
    from src.splits import split_cross_station
    df = _toy_df(seed=1)
    tr, te = split_cross_station(df, train_bs=1, seed=42)
    assert len(tr) > 0 and len(te) > 0
    assert (df.iloc[tr]["BS"] == 1).all()
    assert (df.iloc[te]["BS"] == 2).all()
    # per-class balance
    cnt_tr = df.iloc[tr]["y_multi"].value_counts().sort_index()
    cnt_te = df.iloc[te]["y_multi"].value_counts().sort_index()
    assert (cnt_tr == cnt_te).all()


def test_base_learner_fits_and_predicts():
    from src.base_models import build_base
    df = _toy_df(seed=2, n_per_class=150)
    X = df[[c for c in df.columns if c.startswith("f")]].values.astype(np.float32)
    y = df["y_multi"].values.astype(np.int64)
    for name in ("lightgbm", "xgboost", "mlp"):
        b = build_base(name=name, num_classes=4, seed=42)
        b.fit(X[:500], y[:500])
        proba = b.predict_proba(X[500:600])
        assert proba.shape == (100, 4)
        # proba rows sum to ~1
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-4)


def test_stacked_ensemble_oof_no_leakage():
    """OOF features must be filled across all folds (no zero rows) and
    the stacked predict path must produce valid distributions on a held-out set.
    """
    from src.stacking import StackedEnsemble
    df = _toy_df(seed=3, n_per_class=120)
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(df))
    df = df.iloc[perm].reset_index(drop=True)
    X = df[[c for c in df.columns if c.startswith("f")]].values.astype(np.float32)
    y = df["y_multi"].values.astype(np.int64)
    cut = int(0.7 * len(y))
    Xt, yt = X[:cut], y[:cut]
    Xs, ys = X[cut:], y[cut:]

    ens = StackedEnsemble(num_classes=4, seed=42, k_folds=3).fit(Xt, yt)
    assert ens.oof_proba.shape == (len(yt), 4 * 3)
    # no row left at zero (every train sample was a holdout in exactly one fold)
    row_sums = ens.oof_proba.reshape(len(yt), 3, 4).sum(axis=2)
    assert np.all(row_sums > 0.1)

    proba = ens.predict_proba(Xs)
    assert proba.shape == (len(ys), 4)
    assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-4)


def test_latency_profile_shape():
    from src.latency import profile_throughput
    rng = np.random.default_rng(0)
    X = rng.normal(size=(2048, 12)).astype(np.float32)

    def fake_predict(x):
        return rng.random(size=(len(x), 4))

    prof = profile_throughput(fake_predict, X, batch_sizes=[1, 16, 64, 256], n_repeats=3)
    assert len(prof) == 4
    for entry in prof:
        assert entry["per_sample_us"] >= 0
        assert entry["throughput_samples_per_sec"] > 0
        assert entry["median_ms_per_batch"] >= 0


def test_metrics_aggregate_smoke():
    from src.metrics_utils import aggregate
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 4, size=200)
    proba = rng.random(size=(200, 4))
    proba = proba / proba.sum(axis=1, keepdims=True)
    y_pred = np.argmax(proba, axis=1)
    out = aggregate(y_true, y_pred, proba=proba,
                    class_names=["Benign", "A", "B", "C"], benign_class=0)
    for k in ("macro_f1", "weighted_f1", "binary_f1", "binary_fpr",
              "macro_roc_auc", "macro_pr_auc"):
        assert k in out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
