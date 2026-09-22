"""Tests that every engine tool is defined and callable."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import tools


def test_all_tools_listed():
    names = tools.list_tools()
    assert len(names) == 7
    for n in names:
        assert hasattr(tools, n), "missing function: " + n


def test_diagnose_callable():
    r = tools.tool_diagnose("algebra.quadratic.solve", "x = 2", "x = 2 or x = 3")
    assert isinstance(r, dict)
    assert "error_type" in r


def test_diagnose_returns_real_error():
    r = tools.tool_diagnose("algebra.quadratic.solve",
                            "x = 5 or x = 2", "x = -5 or x = 2")
    assert r["misconception_id"] == "M_SIGN_ERROR_FACTORISATION"


def test_hint_level_callable():
    r = tools.tool_hint_level(2, "procedural")
    assert isinstance(r, dict)
    assert "hint_level" in r


def test_intervention_callable():
    r = tools.tool_intervention("M_SIGN_ERROR_FACTORISATION")
    assert isinstance(r, dict)
    assert r["intervention_pattern"] == "IP_MISCONCEPTION_CONTRAST"


def test_misconception_context_callable():
    r = tools.tool_misconception_context("M_SIGN_ERROR_FACTORISATION")
    assert isinstance(r, dict)
    assert "hints" in r


def test_presentation_rules_stub():
    r = tools.tool_presentation_rules("M_SIGN_ERROR_FACTORISATION")
    assert isinstance(r, dict)


def test_record_attempt_stub():
    r = tools.tool_record_attempt("L001", "algebra.quadratic.solve", "x = 2", {})
    assert isinstance(r, dict)


def test_learner_state_stub():
    r = tools.tool_learner_state("L001")
    assert isinstance(r, dict)


def test_call_tool_dispatch():
    r = tools.call_tool("tool_diagnose", {
        "skill_id": "algebra.quadratic.solve",
        "response": "x = 5 or x = 2",
        "expected": "x = -5 or x = 2",
    })
    assert r["misconception_id"] == "M_SIGN_ERROR_FACTORISATION"


def test_call_tool_unknown():
    r = tools.call_tool("tool_does_not_exist", {})
    assert "error" in r


def test_call_tool_bad_args():
    r = tools.call_tool("tool_diagnose", {"wrong_arg": "x"})
    assert "error" in r
