"""Rule-based disengagement detection (no LLM)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


class DisengagementKind(str, Enum):
    NONE = "none"
    ANSWER_DEMAND = "answer_demand"
    FRUSTRATED = "frustrated"


@dataclass
class DisengagementResult:
    kind: DisengagementKind
    matched_phrase: Optional[str] = None


_ANSWER_PATTERNS = [
    r"\bjust give me the answer\b",
    r"\bgive me the answer\b",
    r"\bgive me the solution\b",
    r"\btell me the answer\b",
    r"\bwhat is the answer\b",
    r"\bshow me the solution\b",
    r"\bsolve it for me\b",
    r"^answer$",
    r"^solution$",
]

_FRUSTRATED_PATTERNS = [
    r"\bi don't understand\b",
    r"\bi dont understand\b",
    r"\bthis is too hard\b",
    r"\bi'm stuck\b",
    r"\bim stuck\b",
    r"\bthis is confusing\b",
    r"\bi give up\b",
    r"\btoo difficult\b",
]


def detect_disengagement(text: str) -> DisengagementResult:
    s = (text or "").strip().lower()
    if not s:
        return DisengagementResult(DisengagementKind.NONE)

    for pat in _ANSWER_PATTERNS:
        m = re.search(pat, s)
        if m:
            return DisengagementResult(DisengagementKind.ANSWER_DEMAND, m.group(0))

    for pat in _FRUSTRATED_PATTERNS:
        m = re.search(pat, s)
        if m:
            return DisengagementResult(DisengagementKind.FRUSTRATED, m.group(0))

    return DisengagementResult(DisengagementKind.NONE)
