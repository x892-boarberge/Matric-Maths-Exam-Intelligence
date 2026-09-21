"""Every tutor line must pass the salt check."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import meta_library as m
from src.tutor.salt_check import is_seasoned, check_all


def _all_meta_lines():
    """Collect every variant string from the meta library."""
    return (
        m._NOT_UNDERSTANDING
        + m._NOT_UNDERSTANDING_AFTER_STRUGGLE
        + m._ANSWER_DEMAND
        + m._ANSWER_DEMAND_REPEAT
        + m._FRUSTRATED
        + m._FRUSTRATED_REPEAT
        + m._SILENCE
        + m._CLOSE_BUT_NOT_QUITE
        + m._CORRECT_AFTER_STRUGGLE_LONG
        + m._CORRECT_AFTER_STRUGGLE_SHORT
        + m._OFF_TOPIC
        + m._PRAISE_SPECIFIC
    )


def test_salt_check_simple_pass():
    ok, reason = is_seasoned("Okay. Let's make this smaller. What do you see?")
    assert ok, reason


def test_salt_check_catches_law():
    ok, reason = is_seasoned("You must factorise first.")
    assert not ok
    assert "forbidden" in reason


def test_salt_check_catches_shame():
    ok, reason = is_seasoned("That is obvious.")
    assert not ok


def test_salt_check_catches_leak():
    ok, reason = is_seasoned("No matching pattern after normalisation.")
    assert not ok
    assert "forbidden" in reason


def test_salt_check_catches_no_warmth():
    ok, reason = is_seasoned("Solve the equation.")
    assert not ok
    assert "warmth" in reason


def test_every_meta_library_line_passes_salt():
    lines = _all_meta_lines()
    failures = check_all(lines)
    assert not failures, "Lines failing salt check:\n" + "\n".join(
        "- " + line + " (" + reason + ")" for line, reason in failures
    )


def test_praise_templates_pass_with_placeholder():
    # The praise template uses {what}. Substitute a sample to check.
    line = m._PRAISE_SPECIFIC[0].format(what="first step")
    ok, reason = is_seasoned(line)
    assert ok, reason
