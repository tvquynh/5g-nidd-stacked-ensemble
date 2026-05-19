"""Multi-class classification metrics + binary detection metrics shared by
all experiments. Centralised here so the same numbers feed the paper tables.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
    average_precision_score,
)


def per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                      class_names: Optional[List[str]] = None) -> Dict:
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
    out = {}
    for i in range(len(p)):
        key = class_names[i] if class_names else str(i)
        out[key] = {
            "precision": float(p[i]),
            "recall": float(r[i]),
            "f1": float(f[i]),
            "support": int(s[i]),
        }
    return out


def detection_metrics(y_true: np.ndarray, y_pred: np.ndarray, benign_class: int = 0) -> Dict:
    y_true_bin = (y_true != benign_class).astype(np.int8)
    y_pred_bin = (y_pred != benign_class).astype(np.int8)
    tp = int(((y_true_bin == 1) & (y_pred_bin == 1)).sum())
    fp = int(((y_true_bin == 0) & (y_pred_bin == 1)).sum())
    tn = int(((y_true_bin == 0) & (y_pred_bin == 0)).sum())
    fn = int(((y_true_bin == 1) & (y_pred_bin == 0)).sum())
    fpr = fp / max(fp + tn, 1)
    recall = tp / max(tp + fn, 1)
    precision = tp / max(tp + fp, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "binary_precision": float(precision),
        "binary_recall": float(recall),
        "binary_f1": float(f1),
        "binary_fpr": float(fpr),
        "binary_tn": tn,
        "binary_fp": fp,
        "binary_fn": fn,
        "binary_tp": tp,
    }


def auc_metrics(y_true: np.ndarray, proba: np.ndarray) -> Dict:
    n_classes = proba.shape[1]
    eye = np.eye(n_classes)
    Y = eye[y_true]
    try:
        roc = float(roc_auc_score(Y, proba, average="macro", multi_class="ovr"))
    except Exception:
        roc = float("nan")
    try:
        pr = float(average_precision_score(Y, proba, average="macro"))
    except Exception:
        pr = float("nan")
    return {"macro_roc_auc": roc, "macro_pr_auc": pr}


def aggregate(y_true: np.ndarray, y_pred: np.ndarray,
              proba: Optional[np.ndarray] = None,
              class_names: Optional[List[str]] = None,
              benign_class: int = 0) -> Dict:
    out = {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "per_class": per_class_metrics(y_true, y_pred, class_names),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    out.update(detection_metrics(y_true, y_pred, benign_class=benign_class))
    if proba is not None:
        out.update(auc_metrics(y_true, proba))
    return out
