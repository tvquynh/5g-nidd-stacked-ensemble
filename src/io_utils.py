"""Path resolution + data loading helpers.

Reads master 5G-NIDD parquet from a read-only location (built once by the
upstream preprocessing pipeline). No write operations on the source data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml


def detect_profile() -> str:
    return "server" if Path("/home/apps").exists() else "local"


def load_paths() -> Dict:
    cfg_path = Path(__file__).resolve().parent.parent / "configs" / "paths.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    profile = detect_profile()
    paths = dict(cfg[profile])
    paths["artifacts"] = cfg["artifacts"]
    return paths


def load_seeds() -> Dict:
    cfg_path = Path(__file__).resolve().parent.parent / "configs" / "seeds.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def load_model_config() -> Dict:
    cfg_path = Path(__file__).resolve().parent.parent / "configs" / "models.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def load_master() -> pd.DataFrame:
    paths = load_paths()
    p = Path(paths["master_parquet"])
    if not p.exists():
        raise FileNotFoundError(f"Master parquet not found at {p}")
    df = pd.read_parquet(p)
    return df


def load_class_names() -> List[str]:
    paths = load_paths()
    p = Path(paths["classes_json"])
    if not p.exists():
        raise FileNotFoundError(f"Classes JSON not found at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def results_dir(name: str = "metrics") -> Path:
    paths = load_paths()
    base = Path(paths["results"]) / paths["artifacts"][f"{name}_dir"].split("/")[-1]
    base.mkdir(parents=True, exist_ok=True)
    return base
