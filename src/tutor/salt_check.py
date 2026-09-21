"""
Salt check.

"Let your conversation be always full of grace, seasoned with salt."
    - Colossians 4:6

Every tutor line must pass this check before it ships. The check is
deliberately narrow: it catches the specific failures the persona
forbids, not stylistic preference.

A line is seasoned if it:
  - is not a law ("you must", "you should", "always", "never")
  - does not shame ("stupid", "lazy", "obvious", "just do")
  - does not leak internals ("normalisation", "rule_id", "unknown pattern",
    "error_type", "fallback")
  - does not pretend the learner is at fault ("you forgot", "you failed")
  - contains at least one warmth signal:
      * a question mark
      * a soft opener ("okay", "that is", "let's", "i hear", "i know", "not a problem")
      * an acknowledgement ("good", "right", "close", "nearly", "well")
"""
import re
from typing import Tuple


FORBIDDEN = [
    # Laws
    r"\byou must\b",
    r"\byou should\b",
    r"\byou need to\b",
    r"\byou have to\b",
    r"\balways do\b",
    r"\bnever do\b",
    # Shaming
    r"\bstupid\b",
    r"\blazy\b",
    r"\bobvious\b",
    r"\bjust do\b",
    r"\bso easy\b",
    r"\bcome on\b",
    r"\bhonestly\b",
    # Blame
    r"\byou forgot\b",
    r"\byou failed\b",
    r"\byou got it wrong\b",
    r"\bwhy did you\b",
    # Leaked internals
    r"\bnormalisation\b",
    r"\bnormalization\b",
    r"\brule_id\b",
    r"\bunknown pattern\b",
    r"\berror_type\b",
    r"\bfallback\b",
    r"\bprovenance\b",
    r"\bmisconception_id\b",
]


WARMTH_OPENERS = [
    "okay", "alright", "that is", "that's", "let's", "let us",
    "i hear", "i know", "i understand", "i am not",
    "not a problem", "no rush", "no problem",
    "fine", "right", "good", "nice",
    "very close", "nearly", "close", "almost",
    "so near", "take", "yes",
]


def is_seasoned(line: str) -> Tuple[bool, str]:
    """
    Return (True, "") if the line passes the salt check.
    Return (False, reason) if it fails.
    """
    if not isinstance(line, str) or not line.strip():
        return False, "empty line"

    low = line.lower()

    for pattern in FORBIDDEN:
        if re.search(pattern, low):
            return False, "forbidden phrase: " + pattern

    # Warmth signal
    if "?" in line:
        return True, ""
    for opener in WARMTH_OPENERS:
        if low.startswith(opener + " ") or low.startswith(opener + ",") or low.startswith(opener + "."):
            return True, ""
    # Also allow warmth mid-line for very short lines
    for opener in WARMTH_OPENERS:
        if " " + opener + " " in low[:40]:
            return True, ""

    return False, "no warmth signal (no question, no soft opener, no acknowledgement)"


def check_all(lines):
    """Return list of (line, reason) for every line that fails."""
    failures = []
    for line in lines:
        ok, reason = is_seasoned(line)
        if not ok:
            failures.append((line, reason))
    return failures
