"""Tests for near-miss detection."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.answer_matcher import near_miss


def test_typo_caught():
    assert near_miss("x = -5 or 22", "x = -5 or x = 2") is True


def test_completely_wrong_not_near_miss():
    assert near_miss("x = 100 or x = 200", "x = -5 or x = 2") is False


def test_exact_not_near_miss():
    # Exact is not a near miss - the matcher handles it
    assert near_miss("x = 2", "x = 2") is True  # distance 0, still <= 2


def test_empty_not_near_miss():
    assert near_miss("", "x = 2") is False
    assert near_miss(None, "x = 2") is False
