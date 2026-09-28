"""LLM as cognitive instrument for MethodMarker.

When the tutor's layers 1 and 2 cannot explain a learner's error, the LLM
reasons about it. This is NOT a validator and NOT a gate. It is one
cognitive instrument inside the Tutor Learning Engine.

Design principles (from docs/spirit.md and docs/architecture.md):
  - The LLM is optional. If it is off or fails, the discovery is still
    recorded with all other signals. No exception propagates to the drill.
  - Its output is a hypothesis with a certainty score, not a verdict.
  - Its explanation is shown to the learner now and stored in the
    discovery for later analysis.
  - It reuses the project HTTP layer (llm_phraser._post) and config
    (llm_config) -- same infrastructure as the phraser, different prompt.
  - Its learner-facing text MUST pass salt_check -- the tutor's voice
    guardrail. Same discipline as phrase_response.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from . import llm_config
from .llm_phraser import _post
from .salt_check import is_seasoned, is_seasoned_hint
from urllib.error import URLError


DIAGNOSER_SYSTEM = """You are a Matric Maths tutor observing a Grade 12
learner. The tutor's rule library cannot explain this specific error, so
you are reasoning about it.

Speak TO the learner. Warm. Two or three sentences in the explanation
field. No laws ("you must", "you should"). No shaming. No blame. No
therapist tone. No labels. Teach; do not lecture.

You MUST respond with valid JSON only -- no prose, no markdown fences,
no commentary. Exactly this shape:
{"hypothesis": "...", "explanation": "...", "certainty": 0.0,
 "suggested_foundation": null}
"""


def is_enabled() -> bool:
    """Delegates to llm_config -- enabled when URL is set and OFF is not."""
    return llm_config.is_enabled()


def _extract_json(text: str) -> Optional[dict]:
    """Parse JSON from LLM response. Handles markdown fences and prose noise."""
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    i = t.find("{")
    j = t.rfind("}")
    if i < 0 or j < 0 or j <= i:
        return None
    try:
        return json.loads(t[i:j + 1])
    except Exception:
        return None


PROMPT_TEMPLATE = """Context:
- Skill: {skill_id}
- Expected answer: {expected_answer}
- Learner's working (verbatim, one line per entry):
{lines}

Return the JSON object now."""


def _safe_explanation(text: str) -> Optional[str]:
    """Pass the explanation through salt_check. Returns None if it fails.

    Mirrors the discipline of phrase_response: try warmth first
    (is_seasoned), fall back to hint-level (is_seasoned_hint). If neither
    passes, drop the explanation entirely -- never speak unseasoned text
    to the learner.
    """
    if not text or not text.strip():
        return None
    ok, _reason = is_seasoned(text)
    if ok:
        return text.strip()
    ok2, _reason2 = is_seasoned_hint(text)
    if ok2:
        return text.strip()
    return None


def diagnose_unknown(
    skill_id: str,
    learner_lines: list[str],
    expected_answer: str,
) -> Optional[dict]:
    """Ask the LLM to reason about an unexplained error.

    Returns dict with keys: hypothesis, explanation, certainty,
    suggested_foundation. Returns None if disabled / failed / unparseable.
    If the explanation fails salt_check, the field is set to None but
    the discovery data is still returned.
    """
    if not llm_config.is_enabled():
        return None

    if not learner_lines or not expected_answer:
        return None

    url = llm_config.get_url()
    key = llm_config.get_key()
    model = llm_config.get_model()
    timeout = llm_config.get_timeout()

    user_msg = PROMPT_TEMPLATE.format(
        skill_id=skill_id,
        expected_answer=expected_answer,
        lines="\n".join("  " + ln for ln in learner_lines),
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DIAGNOSER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    try:
        data = _post(url, key, payload, timeout)
    except (URLError, KeyError, ValueError, TimeoutError, OSError):
        return None

    try:
        raw = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, AttributeError, TypeError):
        return None

    parsed = _extract_json(raw)
    if not parsed:
        return None

    certainty = parsed.get("certainty", 0.0)
    try:
        certainty = max(0.0, min(1.0, float(certainty)))
    except (TypeError, ValueError):
        certainty = 0.0

    raw_explanation = str(parsed.get("explanation", "")).strip()
    safe_explanation = _safe_explanation(raw_explanation)

    return {
        "hypothesis": str(parsed.get("hypothesis", "")).strip(),
        "explanation": safe_explanation,
        "explanation_flagged": raw_explanation if not safe_explanation else None,
        "certainty": certainty,
        "suggested_foundation": parsed.get("suggested_foundation"),
    }


# ============================================================
# Learner-facing rendering
# ============================================================

def render_for_learner(reasoning: dict) -> str:
    """Format the LLM reasoning for the learner, warmly.

    Explanations are pre-filtered by salt_check in diagnose_unknown.
    If explanation is None (rejected), returns an empty string.
    """
    if not reasoning:
        return ""
    explanation = reasoning.get("explanation")
    if not explanation:
        return ""
    cert = reasoning.get("certainty", 0.0)
    if cert < 0.4:
        prefix = "  I'm not completely sure, but here's a guess:\n"
    elif cert < 0.7:
        prefix = "  I think I see what happened here:\n"
    else:
        prefix = "  I see what happened here:\n"
    return prefix + "  " + explanation
