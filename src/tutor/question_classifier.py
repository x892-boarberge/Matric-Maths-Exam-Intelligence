# src/tutor/question_classifier.py
"""
Question classifier — the frame that lets the tutor work with any question.

Three response modes:
  * in-library       — matched a known signature → skill_id resolves to templates
  * in-taxonomy      — matched topic_v2 only → topic known, no variants yet
  * out-of-taxonomy  — no match → log, work with what we have

Backlog S spec: docs/backlog.md
"""
from __future__ import annotations
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]

BRIDGE_PATH = ROOT / "data" / "processed" / "tutor" / "taxonomy_v2_bridge.csv"
SIG_PATH = ROOT / "data" / "processed" / "tutor" / "signature_index.json"
TEMPLATE_DIR = ROOT / "data" / "processed" / "tutor" / "question_templates"


# ------------------------------------------------------------
# Load resources once
# ------------------------------------------------------------

def _load_bridge():
    if not BRIDGE_PATH.exists():
        return {}
    with BRIDGE_PATH.open(encoding="utf-8-sig") as f:
        return {r["topic_v2"]: r["canonical_prefix"]
                for r in csv.DictReader(f)}


def _load_signatures():
    if not SIG_PATH.exists():
        return {}
    return json.loads(SIG_PATH.read_text(encoding="utf-8"))


BRIDGE = _load_bridge()
SIGNATURES = _load_signatures()


# ------------------------------------------------------------
# Result type
# ------------------------------------------------------------

@dataclass
class Classification:
    mode: str                     # 'in-library' | 'in-taxonomy' | 'out-of-taxonomy'
    topic_v2: Optional[str]       # ALG, SEQ, ..., or None
    canonical_prefix: Optional[str]
    signature_id_v2: Optional[str]
    skill_id: Optional[str]       # resolved if in-library
    confidence: float             # 0.0-1.0
    reason: str


# ------------------------------------------------------------
# Rule-based topic_v2 detection (fast, no LLM)
# ------------------------------------------------------------

_TOPIC_HINTS = {
    # topic_v2 : list of regex patterns
    "ALG": [
        r"\bsolve\s+for\s+x\b",
        r"\bx\s*\^\s*2\b", r"\bx\s*\*", r"\bquadratic\b",
        r"\bsimultaneous\b",
    ],
    "SEQ": [
        r"\barithmetic\b", r"\bgeometric\b",
        r"\bsequence\b", r"\bseries\b", r"\bsigma\b",
        r"\bT_n\b", r"\bS_n\b",
    ],
    "FUNC": [
        r"\bfunction\b", r"\basymptote\b", r"\bsketch\b",
        r"\bparabola\b", r"\bhyperbola\b",
        r"\bexponential\b", r"\blogarithm", r"\binverse\b",
        r"\bturning point\b",
    ],
    "CALC": [
        r"\bderivative\b", r"\bf'\(", r"\bcalculus\b",
        r"\bfirst principles\b", r"\bmaximum\b", r"\bminimum\b",
        r"\bconcave\b", r"\btangent\b", r"\boptimi",
    ],
    "TRIG": [
        r"\bsin\b", r"\bcos\b", r"\btan\b",
        r"\btrig\b", r"\bidentity\b", r"\bcompound angle\b",
        r"\breduction\b", r"\bgeneral solution\b",
    ],
    "STAT": [
        r"\bmean\b", r"\bmedian\b", r"\bmode\b",
        r"\bstandard deviation\b", r"\bregression\b",
        r"\bscatter\b", r"\bogive\b", r"\bquartile\b",
        r"\bcorrelation\b",
    ],
    "PROB": [
        r"\bprobability\b", r"\bvenn\b", r"\bindependent\b",
        r"\bmutually exclusive\b", r"\bcounting\b",
        r"\bpermutation\b", r"\bcombination\b",
    ],
    "AGEO": [
        r"\bgradient\b", r"\bmidpoint\b", r"\bcircle\b",
        r"\bequation of.*line\b", r"\bcoordinates\b",
        r"\bangle of inclination\b", r"\bperpendicular\b",
        r"\bparallel\b",
    ],
    "EUCL": [
        r"\bprove\b", r"\bcircle\b", r"\bchord\b",
        r"\btangent\b", r"\bcyclic\b", r"\bsimilar\b",
        r"\bmidpoint\b", r"\bproportional\b",
        r"\breasons?\b",
    ],
    "FIN": [
        r"\binterest\b", r"\bcompound\b", r"\bdepreciat",
        r"\bloan\b", r"\bannuity\b", r"\binvest",
        r"\bR\s*\d",
    ],
}


def _guess_topic_v2(text: str):
    t = text.lower()
    best = (None, 0.0, "")
    for topic, patterns in _TOPIC_HINTS.items():
        hits = sum(1 for pat in patterns if re.search(pat, t))
        if hits == 0:
            continue
        conf = min(1.0, hits * 0.25)
        if conf > best[1]:
            best = (topic, conf, f"{hits} pattern matches")
    return best


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def classify_question(text: str,
                      default_skill_hint: Optional[str] = None
                      ) -> Classification:
    """
    Classify a question from its text. Returns a Classification object.

    Uses rules by default. If a default_skill_hint is provided (the tutor
    knows the topic already), it overrides the guess.
    """
    text = (text or "").strip()
    if not text:
        return Classification(
            mode="out-of-taxonomy", topic_v2=None,
            canonical_prefix=None, signature_id_v2=None,
            skill_id=None, confidence=0.0,
            reason="empty text",
        )

    # 1. Try the hint first
    if default_skill_hint:
        prefix = default_skill_hint.split(".")[0]
        topic = next((k for k, v in BRIDGE.items() if v == prefix), None)
        if topic:
            return Classification(
                mode="in-taxonomy", topic_v2=topic,
                canonical_prefix=prefix,
                signature_id_v2=None,
                skill_id=default_skill_hint,
                confidence=0.7,
                reason="skill_hint from tutor",
            )

    # 2. Rule-based topic guess
    topic, conf, reason = _guess_topic_v2(text)
    if topic is None:
        return Classification(
            mode="out-of-taxonomy", topic_v2=None,
            canonical_prefix=None, signature_id_v2=None,
            skill_id=None, confidence=0.0,
            reason="no rule matched",
        )

    prefix = BRIDGE.get(topic)

    # 3. Do we have a template with this prefix?
    #    (in-library means signature matched, not just topic)
    #    For now, we only resolve to skill_id if the caller passed a hint.
    return Classification(
        mode="in-taxonomy",
        topic_v2=topic,
        canonical_prefix=prefix,
        signature_id_v2=None,
        skill_id=None,
        confidence=conf,
        reason=reason,
    )


def log_unknown(text: str, learner_id: str = "", session_id: str = ""):
    """Log an out-of-taxonomy question to a JSONL file for later review."""
    import time
    log_dir = ROOT / "data" / "processed" / "tutor"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "question_log.jsonl"
    entry = {
        "ts": time.time(),
        "text": text[:500],
        "learner_id": learner_id,
        "session_id": session_id,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return str(log_path)
