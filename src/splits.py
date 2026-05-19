"""Two splits used in this paper:
- random: stratified 80/20 on y_multi.
- cross_station: train on base station train_bs (1 or 2), test on the other.
  Per-class stratified rebalance to size = min(train_bs class size, test_bs class size)
  so the prior shift is removed and the residual gap reflects true cross-station
  generalization.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit


def split_random(df: pd.DataFrame, seed: int, test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(np.zeros(len(df)), df["y_multi"].values))
    return train_idx, test_idx


def split_cross_station(df: pd.DataFrame, train_bs: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    test_bs = 2 if train_bs == 1 else 1
    rng = np.random.default_rng(seed)
    classes = np.unique(df["y_multi"].values)
    train_chunks, test_chunks = [], []
    for c in classes:
        m_train = (df["BS"].values == train_bs) & (df["y_multi"].values == c)
        m_test = (df["BS"].values == test_bs) & (df["y_multi"].values == c)
        idx_train_all = np.where(m_train)[0]
        idx_test_all = np.where(m_test)[0]
        if len(idx_train_all) == 0 or len(idx_test_all) == 0:
            continue
        n = min(len(idx_train_all), len(idx_test_all))
        train_chunks.append(rng.choice(idx_train_all, size=n, replace=False))
        test_chunks.append(rng.choice(idx_test_all, size=n, replace=False))
    return np.concatenate(train_chunks), np.concatenate(test_chunks)


def get_split(name: str, df: pd.DataFrame, seed: int, train_bs: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    if name == "random":
        return split_random(df, seed)
    if name == "cross_station":
        return split_cross_station(df, train_bs=train_bs, seed=seed)
    raise ValueError(f"Unknown split: {name}")
