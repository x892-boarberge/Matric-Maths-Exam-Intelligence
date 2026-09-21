"""Tests for OTHER_LANGUAGE detection and response."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.disengagement import detect_disengagement, DisengagementKind
from src.tutor import meta_library as m
from src.tutor.salt_check import is_seasoned


def test_afrikaans_detected():
    r = detect_disengagement("die gradient is te klein")
    assert r.kind == DisengagementKind.OTHER_LANGUAGE


def test_zulu_detected():
    r = detect_disengagement("ngiyazi kodwa angazi ukuthi ngenzeni")
    assert r.kind == DisengagementKind.OTHER_LANGUAGE


def test_sesotho_detected():
    r = detect_disengagement("a ke utlwisisa")
    assert r.kind == DisengagementKind.OTHER_LANGUAGE


def test_afrikaans_short_detected():
    r = detect_disengagement("ek het n vraag")
    assert r.kind == DisengagementKind.OTHER_LANGUAGE


def test_english_not_misclassified():
    r = detect_disengagement("I do not understand this problem")
    assert r.kind != DisengagementKind.OTHER_LANGUAGE


def test_english_die_not_flagged():
    r = detect_disengagement("the die is cast")
    assert r.kind != DisengagementKind.OTHER_LANGUAGE


def test_solve_for_x_not_flagged():
    r = detect_disengagement("solve for x please")
    assert r.kind != DisengagementKind.OTHER_LANGUAGE


def test_language_response_exists():
    s = m.say_other_language(learner_id="L001")
    assert isinstance(s, str)
    assert len(s) > 20


def test_language_response_is_salted():
    for lid in ["L001", "L002", "L003", "L004"]:
        s = m.say_other_language(learner_id=lid)
        ok, reason = is_seasoned(s)
        assert ok, reason


def test_language_response_does_not_correct():
    for lid in ["L001", "L002", "L003"]:
        s = m.say_other_language(learner_id=lid).lower()
        assert "speak english" not in s
        assert "in english only" not in s
        assert "must use english" not in s


def test_language_dispatch():
    s = m.respond_to_disengagement("other_language", learner_id="L001")
    assert isinstance(s, str)
    assert len(s) > 20
