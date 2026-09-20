"""Tests for graceful answer matching."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.answer_matcher import compare, Match


def test_exact_match():
    assert compare("x = 2 or x = 3", "x = 2 or x = 3") == Match.MATCH


def test_case_insensitive():
    assert compare("X = 2", "x = 2") == Match.MATCH


def test_whitespace_tolerant():
    assert compare("x   =   2", "x = 2") == Match.MATCH
    assert compare("x=2", "x = 2") == Match.MATCH


def test_unicode_operators():
    assert compare("y \u2265 8", "y >= 8") == Match.MATCH
    assert compare("y \u2264 8", "y <= 8") == Match.MATCH


def test_function_name_spacing():
    assert compare("sintheta", "sin theta") == Match.MATCH
    assert compare("sin(theta)", "sin theta") == Match.MATCH
    assert compare("cosx", "cos x") == Match.MATCH


def test_or_equivalence():
    assert compare("x = 2 or3", "x = 2 or x = 3") == Match.MATCH
    assert compare("x=2or3", "x = 2 or x = 3") == Match.MATCH
    assert compare("x = 2 or x = 3", "x = 2 or x = 3") == Match.MATCH


def test_wrong_answer_still_wrong():
    assert compare("y >= 8", "y <= 8") == Match.NO_MATCH
    assert compare("x = 2", "x = 3") == Match.NO_MATCH
    assert compare("sin theta", "cos theta") == Match.NO_MATCH


def test_empty_responses():
    assert compare("", "x = 2") == Match.NO_MATCH
    assert compare("x = 2", "") == Match.NO_MATCH
    assert compare(None, "x = 2") == Match.NO_MATCH


def test_does_not_accept_partial():
    # A prefix is not a match
    assert compare("x = 2 or", "x = 2 or x = 3") == Match.NO_MATCH
    # Extra content is not a match
    assert compare("x = 2 or x = 3 or x = 4", "x = 2 or x = 3") == Match.NO_MATCH
