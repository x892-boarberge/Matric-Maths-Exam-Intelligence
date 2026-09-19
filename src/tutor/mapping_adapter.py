"""
Adapter: v1 topic labels <-> v2 topic_ids.

The tutor engine (built earlier) uses v1 topic labels:
    "Algebra & Equations", "Functions & Graphs", "Calculus", ...

The v2 mapped corpus and priority engine use v2 topic_ids:
    "ALG", "FUNC", "CALC", ...

This module translates between the two, so the tutor can consume
the v2 corpus without rewriting its internals.

Public:
    v1_to_v2(label)  -> str or None
    v2_to_v1(topic_id) -> str or None
    load_translation() -> dict
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TAX_PATH = ROOT / "data" / "processed" / "taxonomy" / "v1_to_v2_topic_map.csv"

_v1_to_v2 = None
_v2_to_v1 = None


def load_translation() -> dict:
    global _v1_to_v2, _v2_to_v1
    if _v1_to_v2 is not None:
        return _v1_to_v2
    df = pd.read_csv(TAX_PATH)
    _v1_to_v2 = dict(zip(df["v1_label"], df["v2_topic_id"]))
    _v2_to_v1 = {v: k for k, v in _v1_to_v2.items()}
    return _v1_to_v2


def v1_to_v2(label):
    if label is None:
        return None
    return load_translation().get(str(label).strip())


def v2_to_v1(topic_id):
    if topic_id is None:
        return None
    load_translation()
    return _v2_to_v1.get(str(topic_id).strip())


def all_v2_ids():
    return sorted(set(load_translation().values()))


def all_v1_labels():
    return sorted(set(load_translation().keys()))
