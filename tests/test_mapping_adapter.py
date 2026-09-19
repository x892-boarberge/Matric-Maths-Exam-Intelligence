import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.mapping_adapter import v1_to_v2, v2_to_v1, all_v2_ids


def test_basic_translation():
    assert v1_to_v2("Algebra & Equations") == "ALG"
    assert v1_to_v2("Functions & Graphs") == "FUNC"
    assert v1_to_v2("Calculus") == "CALC"
    assert v1_to_v2("Trigonometry") == "TRIG"
    assert v1_to_v2("Euclidean Geometry") == "EUCL"


def test_reverse_translation():
    assert v2_to_v1("ALG") == "Algebra & Equations"
    assert v2_to_v1("FUNC") == "Functions & Graphs"


def test_unknown_returns_none():
    assert v1_to_v2("Unknown Topic") is None
    assert v1_to_v2(None) is None
    assert v2_to_v1("XYZ") is None


def test_all_v2_ids_present():
    ids = set(all_v2_ids())
    expected = {"ALG", "SEQ", "FIN", "FUNC", "CALC", "PROB",
                "STAT", "AGEO", "TRIG", "EUCL"}
    assert expected.issubset(ids)


def test_round_trip():
    for label in ["Algebra & Equations", "Calculus", "Trigonometry"]:
        v2 = v1_to_v2(label)
        assert v2 is not None
        assert v2_to_v1(v2) == label
