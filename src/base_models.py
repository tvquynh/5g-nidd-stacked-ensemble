"""Three heterogeneous base learners used in the stacked ensemble:

- LightGBM (gradient-boosted trees, native multi-class softmax)
- XGBoost  (gradient-boosted trees, histogram method)
- MLP      (sklearn MLPClassifier, two hidden layers)

Each returns a thin BaseLearner wrapper exposing .fit(X, y) and .predict_proba(X)
so the stacking layer can iterate uniformly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from .io_utils import load_model_config


@dataclass
class BaseLearner:
    name: str
    num_classes: int
    seed: int
    val_fraction: float = 0.1

    def __post_init__(self):
        self._model = None
        self._scaler: Optional[StandardScaler] = None
        self._cfg = load_model_config()

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseLearner":
        if self.name == "lightgbm":
            self._fit_lgb(X, y)
        elif self.name == "xgboost":
            self._fit_xgb(X, y)
        elif self.name == "mlp":
            self._fit_mlp(X, y)
        else:
            raise ValueError(f"Unknown base learner: {self.name}")
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise RuntimeError(f"Model {self.name} not fit yet")
        if self.name == "lightgbm":
            proba = self._model.predict(X)
        elif self.name == "xgboost":
            proba = self._model.predict(xgb.DMatrix(X))
        elif self.name == "mlp":
            X_scaled = self._scaler.transform(X)
            proba = self._model.predict_proba(X_scaled)
        else:
            raise ValueError(self.name)
        return self._pad_to_num_classes(proba)

    def _pad_to_num_classes(self, proba: np.ndarray) -> np.ndarray:
        """If a base learner saw fewer classes than ``self.num_classes`` (can happen
        in tiny CV folds), pad the missing columns with zeros so the OOF buffer
        has a consistent shape across base learners and folds.
        """
        if proba.ndim != 2 or proba.shape[1] == self.num_classes:
            return proba
        if proba.shape[1] > self.num_classes:
            raise RuntimeError(
                f"{self.name}: predict_proba returned {proba.shape[1]} cols, "
                f"expected at most {self.num_classes}"
            )
        full = np.zeros((proba.shape[0], self.num_classes), dtype=proba.dtype)
        if self.name == "mlp":
            seen = list(self._model.classes_)
        else:
            seen = list(range(proba.shape[1]))
        for j, c in enumerate(seen):
            full[:, int(c)] = proba[:, j]
        return full

    def _fit_lgb(self, X, y):
        cfg = dict(self._cfg["lightgbm"])
        n_iter = cfg.pop("num_iterations", 300)
        early_stop = cfg.pop("early_stopping_rounds", 25)
        cfg["seed"] = self.seed
        cfg["num_class"] = self.num_classes
        X_tr, X_vl, y_tr, y_vl = train_test_split(
            X, y, test_size=self.val_fraction, random_state=self.seed, stratify=y
        )
        train_set = lgb.Dataset(X_tr, label=y_tr)
        val_set = lgb.Dataset(X_vl, label=y_vl, reference=train_set)
        self._model = lgb.train(
            cfg, train_set,
            num_boost_round=n_iter,
            valid_sets=[val_set], valid_names=["val"],
            callbacks=[lgb.early_stopping(early_stop, verbose=False),
                       lgb.log_evaluation(0)],
        )

    def _fit_xgb(self, X, y):
        cfg = dict(self._cfg["xgboost"])
        n_est = cfg.pop("n_estimators", 300)
        early = cfg.pop("early_stopping_rounds", 25)
        cfg["seed"] = self.seed
        cfg["num_class"] = self.num_classes
        X_tr, X_vl, y_tr, y_vl = train_test_split(
            X, y, test_size=self.val_fraction, random_state=self.seed, stratify=y
        )
        dtr = xgb.DMatrix(X_tr, label=y_tr)
        dvl = xgb.DMatrix(X_vl, label=y_vl)
        self._model = xgb.train(
            cfg, dtr,
            num_boost_round=n_est,
            evals=[(dvl, "val")],
            early_stopping_rounds=early,
            verbose_eval=False,
        )

    def _fit_mlp(self, X, y):
        cfg = dict(self._cfg["mlp"])
        cfg["random_state"] = self.seed
        cfg["hidden_layer_sizes"] = tuple(cfg.get("hidden_layer_sizes", [128, 64]))
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)
        self._model = MLPClassifier(**cfg)
        self._model.fit(X_scaled, y)


def build_base(name: str, num_classes: int, seed: int) -> BaseLearner:
    return BaseLearner(name=name, num_classes=num_classes, seed=seed)
