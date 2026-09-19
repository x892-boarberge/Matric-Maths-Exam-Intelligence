"""
Structural rules for Mapping v2.

Structural rules fire on regex patterns that are strong topic signals
regardless of surrounding context. They run AFTER signature matching and
BEFORE lexicon matching.

Two exclusions prevent false positives:

  SEQ_EXCLUSION  — blocks CALC rules when the text clearly refers to a
                   sequence (e.g. "maximum depth of the pattern").

  CALC_EXCLUSION — blocks ALG rules when the text has calculus markers
                   (e.g. "x?" inside a derivative). This is the fix that
                   produced F1=0.972.

Public functions:
    load_struct_rules()          -> list of (pattern, topic_id, confidence)
    match_struct(text, rules)    -> list of matching dicts
"""
from pathlib import Path
import json
import re

FROZEN_DIR = Path(__file__).parent / "frozen"


SEQ_EXCLUSION = re.compile(
    r"depth|second time|number pattern|first \d+ seconds|between T",
    re.IGNORECASE,
)


CALC_EXCLUSION = re.compile(
    r"dy/dx|d/dx|derivative|differentiat|first principles"
    r"|maximum height|minimum value|tangent|concave|inflection"
    r"|f\s*'|g\s*'|h\s*'|y\s*'"
    r"|\bf\(x\)|\bg\(x\)|\bh\(x\)",
    re.IGNORECASE,
)


def load_struct_rules(path: Path | None = None):
    """
    Load STRUCT rules from JSON.

    Returns a list of tuples: (pattern, topic_id, confidence).
    """
    path = path or (FROZEN_DIR / "struct_rules.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [tuple(r) for r in raw]


def match_struct(text, rules):
    """
    Return every structural rule that fires on `text`.

    Applies the CALC/SEQ and ALG/CALC exclusions before returning.
    """
    if not isinstance(text, str):
        return []

    text_lower = text.lower()
    is_seq  = bool(SEQ_EXCLUSION.search(text))
    is_calc = bool(CALC_EXCLUSION.search(text))

    hits = []
    for pattern, topic_id, conf in rules:
        if not re.search(pattern, text_lower):
            continue

        # A CALC rule must not fire on a sequence question.
        if topic_id == "CALC" and is_seq:
            continue

        # An ALG OCR rule must not fire on a calculus question.
        if topic_id == "ALG" and is_calc:
            continue

        hits.append({
            "topic_id":     topic_id,
            "signature_id": f"STRUCT_{topic_id}",
            "confidence":   conf,
            "usage_rule":   "PRIMARY",
            "pattern":      pattern,
        })

    return hits