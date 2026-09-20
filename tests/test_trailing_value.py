"""Test that verbose expected answers accept bare and contextual learner values."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.answer_matcher import compare, Match


def test_boxplot_bare_value():
    assert compare("7", "{5, 7, 9, 12, 25} IQR = 7") == Match.MATCH


def test_boxplot_wrong_value_still_wrong():
    assert compare("18", "{5, 7, 9, 12, 25} IQR = 7") == Match.NO_MATCH


def test_generic_eq():
    assert compare("16/3", "S_infinity = 16/3") == Match.MATCH


def test_contextual_response_matches_verbose_expected():
    assert compare("IQR = 7", "{5, 7, 9, 12, 25} IQR = 7") == Match.MATCH


def test_partial_number_is_not_a_match():
    assert compare("7", "17") == Match.NO_MATCH
    assert compare("2", "42") == Match.NO_MATCH
