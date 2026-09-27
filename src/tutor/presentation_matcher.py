"""
Presentation matcher.

Reads presentation_rules_v1.csv and matches the learner's working
against presentation triggers. Returns gentle coaching notes for
the highest-priority matches only — never blocks the main verdict.

Public:
    check_presentation(working_lines, topic=None) -> list[PresentationNote]
    format_note(note) -> str
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "processed" / "tutor" / "presentation_rules_v1.csv"

PRIORITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}


@dataclass
class PresentationNote:
    rule_id: str
    category: str
    topic: str
    priority: str
    advice: str
    dbe_note: str
    evidence: str = ""


# ------------------------------------------------------------------
# Load rules
# ------------------------------------------------------------------
def _load_rules() -> List[dict]:
    if not CSV_PATH.exists():
        return []
    out = []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out.append(row)
    return out


_RULES: Optional[List[dict]] = None


def _rules() -> List[dict]:
    global _RULES
    if _RULES is None:
        _RULES = _load_rules()
    return _RULES


# ------------------------------------------------------------------
# Rule predicates — detect presentation problems in text
# ------------------------------------------------------------------
# Each predicate takes the full working string and returns (fires, evidence)

def _has_multiple_equals_one_line(text: str) -> bool:
    for line in text.splitlines():
        if line.count("=") >= 3:
            return True
    return False


def _has_no_blank_between_parts(text: str) -> bool:
    # Very heuristic — no blank lines but multiple sub-parts
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 4:
        return False
    # No blank lines at all
    raw = text.splitlines()
    blanks = sum(1 for l in raw if not l.strip())
    return blanks == 0 and len(lines) >= 5


def _has_slash_fraction(text: str) -> bool:
    # Look for a/b but not date-like
    for m in re.finditer(r"(?<!\d)(\d+)\s*/\s*(\d+)", text):
        n, d = int(m.group(1)), int(m.group(2))
        if d in (2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 100):
            if len(n) <= 3 and len(str(d)) <= 3:
                return True
    return False


def _has_answer_only(text: str) -> bool:
    # Single line, contains =, no other working lines
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) != 1:
        return False
    return "=" in lines[0] and len(lines[0]) < 60


def _has_single_root(text: str) -> bool:
    # For quadratic — only one root mentioned
    matches = re.findall(r"[a-z]\s*=\s*-?\d+", text, re.IGNORECASE)
    return len(matches) == 1


def _has_no_units(text: str, topic: Optional[str]) -> bool:
    if topic not in ("FIN", "CALC", "AGEO", "TRIG"):
        return False
    if re.search(r"\bcm\b|\bm\b|\bkm\b|\bR\s*\d|\bdegrees\b|°|\bm²|\bcm²|\bcm³", text):
        return False
    return True


def _has_no_two_decimal(text: str) -> bool:
    # If the question asked for TWO decimal places but answer is exact
    # (handled at call site — not detected here)
    return False


def _has_negative_without_brackets(text: str) -> bool:
    # "-3x" without brackets is fine; "-3(2)" without brackets around the -3 is a problem
    # Look for patterns like = -3( or + -3 or - -2 that suggest bracketless negatives
    return bool(re.search(r"[+\-]\s*-\s*\d", text))


def _has_no_reason_column(text: str, topic: Optional[str]) -> bool:
    if topic != "EUCL":
        return False
    # If the learner's working has no reason-language and lines are short
    reason_words = ["reason", "angle", "sides", "cyclic", "semicircle",
                    "tangent", "chord", "radius", "diameter", "opposite"]
    low = text.lower()
    return not any(w in low for w in reason_words)


# ------------------------------------------------------------------
# Rule registry — predicate per rule_id
# ------------------------------------------------------------------
_RULE_PREDICATES = {
    "PR_GEN_001": lambda t, top: _has_answer_only(t),
    "PR_GEN_004": lambda t, top: _has_multiple_equals_one_line(t),
    "PR_GEN_005": lambda t, top: "!!!" in t or "~~" in t,
    "PR_GEN_009": lambda t, top: _has_answer_only(t),
    "PR_GEN_011": lambda t, top: _has_no_units(t, top),
    "PR_GEN_014": lambda t, top: _has_single_root(t),
    "PR_ALG_012": lambda t, top: "sqrt" in t and "reject" not in t.lower() and "extraneous" not in t.lower(),
    "PR_ALG_016": lambda t, top: _has_negative_without_brackets(t),
    "PR_ALG_020": lambda t, top: False,
    "PR_AGEO_007": lambda t, top: False,
    "PR_DIAG_008": lambda t, top: "assum" in t.lower() and "because" in t.lower(),
    "PR_EUCL_001": lambda t, top: _has_no_reason_column(t, top),
    "PR_FIN_009": lambda t, top: top == "FIN" and "R" not in t and re.search(r"\d+\.\d+", t) is not None,
    "PR_STAT_012": lambda t, top: "median" in t.lower() and "position" not in t.lower(),
    "PR_PROB_014": lambda t, top: bool(re.search(r"\b[2-9]\.\d+\b", t)) and top == "PROB",
    "PR_DBE_002": lambda t, top: False,
    "PR_DBE_004": lambda t, top: _has_negative_without_brackets(t),
    "PR_DBE_005": lambda t, top: _has_single_root(t),
    "PR_DBE_010": lambda t, top: _has_multiple_equals_one_line(t),
}


# ------------------------------------------------------------------
# Main check
# ------------------------------------------------------------------
def check_presentation(working_lines, topic: Optional[str] = None,
                       max_notes: int = 2) -> List[PresentationNote]:
    """
    Match the learner's working against presentation rules.
    Returns up to max_notes notes, highest priority first.
    """
    if isinstance(working_lines, list):
        text = "\n".join(str(l) for l in working_lines)
    else:
        text = str(working_lines or "")

    if not text.strip():
        return []

    matched: List[PresentationNote] = []

    for rule in _rules():
        rid = rule.get("rule_id", "")
        pred = _RULE_PREDICATES.get(rid)
        if pred is None:
            continue
        try:
            if pred(text, topic):
                matched.append(PresentationNote(
                    rule_id=rid,
                    category=rule.get("category", ""),
                    topic=rule.get("topic", ""),
                    priority=rule.get("priority", "medium"),
                    advice=rule.get("advice", ""),
                    dbe_note=rule.get("dbe_note", ""),
                    evidence="",
                ))
        except Exception:
            continue

    # Also try topic-specific rules with generic predicates
    for rule in _rules():
        if rule.get("topic") not in (topic, "all"):
            continue
        rid = rule.get("rule_id", "")
        if rid in _RULE_PREDICATES:
            continue  # already handled
        # For unhandled topic rules, check trigger-keyword overlap with working text
        trig = (rule.get("trigger") or "").lower()
        # Simple keyword overlap: 2+ words from trigger appear in working
        words = [w for w in re.findall(r"[a-z]{4,}", trig) if len(w) > 3]
        low = text.lower()
        hits = sum(1 for w in words if w in low)
        if hits >= 3:
            matched.append(PresentationNote(
                rule_id=rid,
                category=rule.get("category", ""),
                topic=rule.get("topic", ""),
                priority=rule.get("priority", "medium"),
                advice=rule.get("advice", ""),
                dbe_note=rule.get("dbe_note", ""),
            ))

    # Sort by priority, deduplicate
    matched.sort(key=lambda n: -PRIORITY_RANK.get(n.priority, 0))
    seen = set()
    out = []
    for n in matched:
        if n.rule_id in seen:
            continue
        seen.add(n.rule_id)
        out.append(n)
        if len(out) >= max_notes:
            break
    return out


def format_note(note: PresentationNote) -> str:
    """Render a single presentation note warmly."""
    lines = []
    lines.append("")
    lines.append("  ~ Presentation note ~")
    if note.dbe_note:
        lines.append(f"  {note.dbe_note}")
    if note.advice:
        lines.append(f"  Rule: {note.advice}")
    lines.append(f"  ({note.rule_id} | priority: {note.priority})")
    return "\n".join(lines)