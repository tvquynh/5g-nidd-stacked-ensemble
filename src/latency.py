"""Inference latency + throughput micro-benchmarks for base learners and the
stacked ensemble. Measurements use repeated wall-clock timing on a held-out
test subset; results are reported as median over 10 repetitions to mitigate
jitter from a shared host.
"""
from __future__ import annotations

import gc
import time
from typing import Callable, Dict, List

import numpy as np


def measure_latency(
    predict_fn: Callable[[np.ndarray], np.ndarray],
    X: np.ndarray,
    batch_size: int,
    n_warmup: int = 2,
    n_repeats: int = 10,
) -> Dict[str, float]:
    """Return dict with median/mean/std latency (ms/batch), throughput (samples/sec),
    and per-sample latency (us/sample).
    """
    n = len(X)
    if batch_size <= 0 or batch_size > n:
        batch_size = n
    indices = np.arange(min(batch_size, n))
    Xb = X[indices]

    for _ in range(n_warmup):
        predict_fn(Xb)

    times_ms: List[float] = []
    for _ in range(n_repeats):
        gc.collect()
        t0 = time.perf_counter()
        predict_fn(Xb)
        dt = (time.perf_counter() - t0) * 1000.0
        times_ms.append(dt)

    arr = np.array(times_ms)
    median_ms = float(np.median(arr))
    return {
        "batch_size": int(batch_size),
        "n_repeats": int(n_repeats),
        "median_ms_per_batch": median_ms,
        "mean_ms_per_batch": float(arr.mean()),
        "std_ms_per_batch": float(arr.std(ddof=1) if len(arr) > 1 else 0.0),
        "per_sample_us": float(median_ms * 1000.0 / batch_size),
        "throughput_samples_per_sec": float(batch_size * 1000.0 / median_ms) if median_ms > 0 else float("inf"),
    }


def profile_throughput(predict_fn: Callable[[np.ndarray], np.ndarray],
                       X: np.ndarray,
                       batch_sizes: List[int],
                       n_repeats: int = 10) -> List[Dict]:
    """Run measure_latency across a list of batch sizes."""
    return [measure_latency(predict_fn, X, b, n_repeats=n_repeats) for b in batch_sizes]
