"""Build the 5G-NIDD master parquet from the author-curated ``Encoded.csv``.

The 5G-NIDD release at https://ieee-dataport.org/documents/5g-nidd ships
``Encoded.csv`` (CC BY 4.0; 1,215,890 rows, 96 columns). This script
applies the documented author preprocessing plus the project-specific
station and capture-day markers, and writes a parquet that the rest of
the pipeline reads as ``master_5g_nidd.parquet``.

Reviewer usage:

    python -m src.build_master \\
        --encoded-csv /path/to/5G-NIDD/Encoded.csv \\
        --out-parquet /path/to/master_5g_nidd.parquet \\
        --out-classes /path/to/master_5g_nidd.classes.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


BS1_ROW_COUNT = 728_316  # verified from BTS_1.csv
BS2_ROW_COUNT = 487_574  # verified from BTS_2.csv
TOTAL_ROWS = BS1_ROW_COUNT + BS2_ROW_COUNT  # 1,215,890

ATTACK_TO_DAY = {
    "Benign":          1,
    "ICMPFlood":       1,
    "SYNScan":         1,
    "TCPConnectScan":  1,
    "UDPFlood":        1,
    "UDPScan":         1,
    "HTTPFlood":       2,
    "SYNFlood":        2,
    "SlowrateDoS":     2,
}


def build(encoded_csv: Path, out_parquet: Path, out_classes: Path):
    print(f"[build] reading {encoded_csv}")
    df = pd.read_csv(encoded_csv, low_memory=False)
    n = len(df)
    if n != TOTAL_ROWS:
        raise ValueError(f"Encoded.csv expected {TOTAL_ROWS} rows, got {n}")

    bs = (df.index >= BS1_ROW_COUNT).astype("int8") + 1
    df["BS"] = bs
    df = df.iloc[:, 1:]  # drop Unnamed: 0
    for col in ("Attack Tool", "Label", "sVid", "dVid", "54"):
        if col in df.columns:
            df = df.drop(columns=col)

    numeric = df.select_dtypes(include="number").columns
    df[numeric] = df[numeric].fillna(df[numeric].median())
    df["capture_day"] = df["Attack Type"].map(ATTACK_TO_DAY).fillna(1).astype("int8")

    atk = df["Attack Type"].astype(str).str.strip()
    classes = sorted(atk.unique().tolist())
    cls_to_int = {c: i for i, c in enumerate(classes)}
    df["y_multi"] = atk.map(cls_to_int).astype("int32")
    df["y_binary"] = (atk != "Benign").astype("int8")
    df = df.drop(columns=["Attack Type"], errors="ignore")

    meta_cols = {"y_multi", "y_binary", "BS", "capture_day"}
    feature_cols = [c for c in df.columns if c not in meta_cols]
    for c in feature_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[feature_cols] = df[feature_cols].fillna(0).astype("float32")

    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, compression="snappy", index=False)
    out_classes.parent.mkdir(parents=True, exist_ok=True)
    out_classes.write_text(json.dumps(classes))
    print(f"[build] wrote {out_parquet} ({out_parquet.stat().st_size/1024/1024:.1f} MB)")
    print(f"[build] wrote {out_classes}")
    print(f"[build] rows={len(df):,} features={len(feature_cols)} classes={len(classes)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--encoded-csv", required=True, type=Path)
    ap.add_argument("--out-parquet", required=True, type=Path)
    ap.add_argument("--out-classes", required=True, type=Path)
    args = ap.parse_args()
    build(args.encoded_csv, args.out_parquet, args.out_classes)


if __name__ == "__main__":
    main()
