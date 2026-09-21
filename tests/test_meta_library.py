"""Tests for the meta-communication library."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import meta_library as m


def test_not_understanding_returns_string():
    s = m.say_not_understanding()
    assert isinstance(s, str)
    assert len(s) > 40


def test_answer_demand_does_not_give_answer():
    s = m.say_answer_demand()
    assert "the answer is" not in s.lower()
    assert "I will not" in s or "won" in s


def test_frustrated_is_graceful():
    s = m.say_frustrated()
    for bad in ["stupid", "easy", "obvious", "just", "again"]:
        assert bad not in s.lower()


def test_close_but_not_quite_offers_path():
    s = m.say_close_but_not_quite()
    assert "almost" in s.lower() or "close" in s.lower()


def test_correct_after_struggle_acknowledges_effort():
    s = m.say_correct_after_struggle(attempts=4)
    assert "yourself" in s.lower() or "tries" in s.lower()


def test_off_topic_returns_to_problem():
    s = m.say_off_topic()
    assert "problem" in s.lower() or "question" in s.lower()


def test_praise_specific_uses_context():
    s = m.say_praise_specific("first step")
    assert "first step" in s
