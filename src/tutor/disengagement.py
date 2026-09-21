"""Rule-based disengagement / help-seeking detection (no LLM)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


# Words that are clearly not English. A single hit is not enough;
# we require 2+ markers before firing, to avoid false positives.
SA_LANGUAGE_MARKERS = [
    # Afrikaans - definite/indefinite articles and common words
    "die", "n", "te", "het", "vraag", "som", "hoe", "wat",
    "nie", "ek", "jy", "julle", "hulle", "hierdie", "daardie",
    "baie", "klein", "groot", "maar", "ook", "nog", "want",
    "waar", "wanneer", "hoekom", "asseblief", "dankie",
    "verstaan", "verduidelik", "geleer", "gese", "reg",
    "verkeerd", "maklik", "moeilik", "sommer", "net", "al",
    # isiZulu and isiXhosa
    "yebo", "cha", "haibo", "eish", "yoh",
    "ngiyazi", "angazi", "ngiyabonga", "ngicela",
    "yini", "kanjani", "kuhle", "kubi", "kodwa", "futhi",
    "manje", "ngoba", "noma", "ndiyazi", "andazi",
    "ndiyabulela", "ndicela", "ntoni", "njani",
    "kwaye", "ngoku", "yinhle", "utlwisisa", "utlwa",
    "sawubona", "sanibonani", "molo",
    # Sesotho, Sepedi, Setswana
    "dumela", "kea", "leboha", "kopa", "gore", "gona",
    "fela", "nnete", "jwang", "empa", "hape", "jwale",
    "hantle", "tseba", "utlwisisa",
    # SA English slang
    "eish", "haibo", "howzit", "bra", "bru", "lekker", "kiff",
]


def _looks_like_other_language(text: str) -> bool:
    if not isinstance(text, str):
        return False
    low = text.lower()
    hits = 0
    for word in SA_LANGUAGE_MARKERS:
        if " " + word + " " in " " + low + " ":
            hits += 1
            if hits >= 2:
                return True
    return False


class DisengagementKind(str, Enum):
    OTHER_LANGUAGE = "other_language"
    HOSTILE = "hostile"
    NONE = "none"
    ANSWER_DEMAND = "answer_demand"
    FRUSTRATED = "frustrated"
    HELP_SEEKING = "help_seeking"


@dataclass
class DisengagementResult:
    kind: DisengagementKind
    matched_phrase: Optional[str] = None


# Order matters: answer-demand → frustrated → help-seeking → none
_ANSWER_PATTERNS = [
    r"\bjust give me the answer\b",
    r"\bgive me the answer\b",
    r"\bgive me the solution\b",
    r"\btell me the answer\b",
    r"\bwhat is the answer\b",
    r"\bshow me the solution\b",
    r"\bsolve it for me\b",
    r"\bi need this fixed now\b",
    r"^answer$",
    r"^solution$",
]

_FRUSTRATED_PATTERNS = [
    r"\bi'?m so frustrated\b",
    r"\bthis is so frustrating\b",
    r"\bi'?m losing my patience\b",
    r"\bi'?m fed up\b",
    r"\bi'?m done with this\b",
    r"\bi give up\b",
    r"\bi quit\b",
    r"\bforget it\b",
    r"\bnever mind\b",
    r"\bthis is ridiculous\b",
    r"\bthis is absurd\b",
    r"\bthis is unbelievable\b",
    r"\bare you kidding me\b",
    r"\byou'?ve got to be kidding me\b",
    r"\bseriously\?\b",
    r"\bcome on\b",
    r"\bugh\b",
    r"\bwhat the hell\b",
    r"\bwhat is wrong with this\b",
    r"\bwhy is this so hard\b",
    r"\bwhy does this keep happening\b",
    r"\bnothing works\b",
    r"\bnothing is working\b",
    r"\bit still doesn'?t work\b",
    r"\bi'?ve tried everything\b",
    r"\bi already tried that\b",
    r"\bthat'?s not what i asked\b",
    r"\byou'?re not listening\b",
    r"\byou don'?t understand\b",
    r"\bdo you even understand\b",
    r"\bthis makes no sense\b",
    r"\bthis is a waste of time\b",
    r"\bi can'?t take this anymore\b",
    r"\bi'?m about to lose it\b",
    r"\bi'?m at my wit'?s end\b",
    r"\bthis is driving me crazy\b",
    r"\bthis is so annoying\b",
    r"\bi hate this\b",
    r"\bi'?m sick of this\b",
    r"\bnot again\b",
    r"\bwhy do you keep doing that\b",
    r"\bstop repeating yourself\b",
    r"\bthat'?s useless\b",
    r"\bthis is useless\b",
    r"\bthis is garbage\b",
    r"\bthis is terrible\b",
    r"\bworst experience ever\b",
    r"\bi can'?t believe this\b",
    r"\bi'?m so done\b",
    r"\bi'?m done\b",
    r"\bi need this fixed now\b",
]

_HELP_PATTERNS = [
    r"\bi need help\b",
    r"\bcan you help me\b",
    r"\bplease help\b",
    r"\bi need assistance\b",
    r"\bcan you assist me\b",
    r"\bi'?m stuck\b",
    r"\bi don'?t know what to do\b",
    r"\bi don'?t understand\b",
    r"\bi'?m confused\b",
    r"\bcan you explain this\b",
    r"\bi need guidance\b",
    r"\bi'?m lost\b",
    r"\bi need support\b",
    r"\bcan someone help\b",
    r"\bhow do i fix this\b",
    r"\bwhere do i start\b",
    r"\bi can'?t figure this out\b",
    r"\bcould you walk me through this\b",
    r"\bwhat should i do\b",
    r"\bi'?m having trouble\b",
    r"\bi need a hand\b",
    r"\bi'?m not sure how to proceed\b",
    r"\bi need more information\b",
    r"\bi'?m unable to continue\b",
    r"\bi need a human\b",
    r"\bcan i talk to support\b",
    r"\bthis isn'?t working for me\b",
    r"\bi need to resolve this\b",
    r"\bhow can i solve this\b",
    r"\bi need step-by-step help\b",
    r"\bi need step by step help\b",
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

    for pat in _HELP_PATTERNS:
        m = re.search(pat, s)
        if m:
            return DisengagementResult(DisengagementKind.HELP_SEEKING, m.group(0))

    # Hostile or abusive input
    HOSTILE_WORDS = [
        "fuck", "fuk", "shit", "bullshit", "damn", "hell",
        "stupid", "idiot", "fool", "dick", "asshole", "bastard",
        "shut up", "screw you", "piss off",
    ]
    low = (text or "").lower()
    if any(w in low for w in HOSTILE_WORDS):
        return DisengagementResult(
            kind=DisengagementKind.HOSTILE,
            matched_phrase=next(w for w in HOSTILE_WORDS if w in low),
        )

    # Other South African language or code-switching
    if _looks_like_other_language(text):
        return DisengagementResult(
            kind=DisengagementKind.OTHER_LANGUAGE,
            matched_phrase="language_marker",
        )

    return DisengagementResult(DisengagementKind.NONE)