"""Known limitations of the graceful matcher."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.answer_matcher import compare, Match


def test_suffix_value_limitation_with_inequality():
    # KNOWN LIMITATION: bare value "8" is a suffix of "y <= 8" so
    # Layer 6 currently matches. Mathematically the learner has not
    # written the range. Should be NO_MATCH in a future revision.
    result = compare("8", "y <= 8")
    assert result == Match.MATCH
