"""Tests for the analogue library."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import analogue_library as al
from src.tutor.salt_check import is_seasoned


def test_all_skills_have_analogues():
    expected = {
        "algebra.quadratic.solve",
        "functions.parabola.range",
        "trig.reduction.simplify",
        "analytical_geom.parallelogram.prove",
        "euclidean.semicircle.prove",
    }
    for s in expected:
        assert al.has_analogue(s), "missing analogue for " + s


def test_each_analogue_has_required_fields():
    for skill in al.all_skills():
        a = al.get_analogue(skill)
        assert "problem" in a
        assert "steps" in a
        assert "note" in a
        assert len(a["steps"]) >= 2


def test_unknown_skill_returns_none():
    assert al.get_analogue("unknown.skill") is None
    assert not al.has_analogue("unknown.skill")


def test_analogue_notes_are_salted():
    for skill in al.all_skills():
        note = al.get_analogue(skill)["note"]
        ok, reason = is_seasoned(note)
        assert ok, skill + " - " + reason
