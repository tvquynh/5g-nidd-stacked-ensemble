"""Heterogeneous shallow stacking with leakage-free out-of-fold (OOF) features.

Pipeline:
  1. For each base learner B in {LightGBM, XGBoost, MLP}:
       - 5-fold stratified CV on the training set.
       - For each fold, fit B on K-1 folds, predict_proba on the held-out fold.
       - Concatenate to form OOF probability matrix P_B in [N, C].
       - Refit B on the full training set; obtain test probabilities Q_B.
  2. Stack: train meta = LogisticRegression on horizontally concatenated
     [P_{LGB} | P_{XGB} | P_{MLP}] -> y_train. Apply to [Q_{LGB} | Q_{XGB} | Q_{MLP}]
     to obtain test predictions.

This avoids the "stacker overfit to base train predictions" leak by holding base
predictions to OOF on train. Meta-learner is light and CPU-cheap.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from .base_models import build_base, BaseLearner
from .io_utils import load_model_config


BASE_NAMES: Tuple[str, ...] = ("lightgbm", "xgboost", "mlp")


@dataclass
class StackedEnsemble:
    num_classes: int
    seed: int
    k_folds: int = 5
    base_names: Tuple[str, ...] = BASE_NAMES

    bases: List[BaseLearner] = field(default_factory=list)
    meta: LogisticRegression = None
    fit_times: Dict[str, float] = field(default_factory=dict)
    oof_proba: np.ndarray = None  # for diagnostics

    def fit(self, X: np.ndarray, y: np.ndarray) -> "StackedEnsemble":
        skf = StratifiedKFold(n_splits=self.k_folds, shuffle=True, random_state=self.seed)
        n, c = len(y), self.num_classes

        oof_blocks = []
        for name in self.base_names:
            oof = np.zeros((n, c), dtype=np.float32)
            t0 = time.time()
            for fold_id, (tr_idx, vl_idx) in enumerate(skf.split(X, y)):
                base = build_base(name=name, num_classes=c, seed=self.seed + fold_id)
                base.fit(X[tr_idx], y[tr_idx])
                oof[vl_idx] = base.predict_proba(X[vl_idx]).astype(np.float32)
            self.fit_times[f"{name}_oof"] = time.time() - t0

            # refit on full train
            t0 = time.time()
            full = build_base(name=name, num_classes=c, seed=self.seed)
            full.fit(X, y)
            self.bases.append(full)
            self.fit_times[f"{name}_full"] = time.time() - t0
            oof_blocks.append(oof)

        oof_features = np.hstack(oof_blocks)  # [N, 3*C]
        self.oof_proba = oof_features

        meta_cfg = dict(load_model_config()["meta_lr"])
        meta_cfg.pop("multi_class", None)
        meta_cfg["random_state"] = self.seed
        t0 = time.time()
        self.meta = LogisticRegression(**meta_cfg)
        self.meta.fit(oof_features, y)
        self.fit_times["meta"] = time.time() - t0
        return self

    def base_proba(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        return {b.name: b.predict_proba(X) for b in self.bases}

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        blocks = [self.bases[i].predict_proba(X).astype(np.float32)
                  for i in range(len(self.base_names))]
        feats = np.hstack(blocks)
        return self.meta.predict_proba(feats)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_proba(X), axis=1)
