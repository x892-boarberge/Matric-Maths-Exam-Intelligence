import sys
import pathlib
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.n08_loader import load_n08_library, select_intervention_from_library, get_library
from src.tutor.schemas import DiagnosisResult, ErrorType


def test_fallback_when_csv_missing(tmp_path):
    lib = load_n08_library(tmp_path / "does_not_exist.csv")
    assert lib.load_status == "fallback"
    assert "M_REDUCTION_SIGN" in lib.by_misconception


def test_csv_load_when_valid(tmp_path):
    path = tmp_path / "intervention_specification_v1.csv"
    pd.DataFrame(
        [
            {
                "intervention_id": "N08_TRIG_RED_01",
                "topic": "Trigonometry",
                "misconception_id": "M_REDUCTION_SIGN",
                "intervention_pattern": "IP_MISCONCEPTION_CONTRAST",
                "status": "active",
            }
        ]
    ).to_csv(path, index=False)

    lib = load_n08_library(path)
    assert lib.load_status == "csv"
    assert lib.source_hash is not None
    assert lib.by_misconception["M_REDUCTION_SIGN"]["intervention_id"] == "N08_TRIG_RED_01"


def test_select_uses_library():
    get_library(force_reload=True)
    diag = DiagnosisResult(
        error_type=ErrorType.CONCEPTUAL,
        misconception_id="M_REDUCTION_SIGN",
        confidence=0.8,
        rule_id="D_TRIG_RED_SIGN",
        explanation="test",
    )
    sel, source = select_intervention_from_library(diag)
    assert sel.n08_intervention_id is not None
    assert sel.provenance.value == "n08_backed"
    assert source in ("csv", "fallback", "fallback_map")
