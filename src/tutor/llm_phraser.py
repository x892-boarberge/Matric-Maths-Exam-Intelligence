"""
LLM phraser (Path C hybrid).

The engine decides. The LLM phrases. It never calls tools. It speaks TO
the learner, never about them.

Gated by llm_gate.should_call_llm(): only called on real maths attempts.
"""
import json
from typing import Optional, Dict, Any
from urllib import request as _urllib_request
from urllib.error import URLError

from . import llm_config
from .salt_check import is_seasoned, is_seasoned_hint


PHRASER_SYSTEM = """You are a Matric Maths tutor. Reply directly to a
Grade 12 learner. Two sentences maximum. Speak TO the learner.

NEVER: describe the learner, echo input, give the answer, use
"you must" / "you should" / "just" / "obvious" / "as an AI",
sound like a therapist, output labels like "learner:".

EXAMPLE GOOD:
One of your roots has the wrong sign. Look at each factor — what
value of x makes it zero?

EXAMPLE BAD:
The learner is in the "answer demand" state. Let's end on a note of
curiosity.

Write plain text only. No labels. No JSON. No markdown.
"""


FORBIDDEN_PHRASES = [
    "the learner", "the student", "they seem", "i can see that",
    "it seems", "challenging situation", "fueling", "hostility",
    "learner:", "you:", "tutor:",
]


def _post(url, key, payload, timeout):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    req = _urllib_request.Request(url, data=body, headers=headers, method="POST")
    with _urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _build_user_message(ctx: Dict[str, Any]) -> str:
    problem = ctx.get("problem")
    diag = ctx.get("diagnosis")
    hint = ctx.get("specific_hint") or ""
    action = ctx.get("action_type")
    learner = ctx.get("learner_response", "")

    lines = []
    lines.append("Learner typed: " + repr(str(learner)[:160]))
    lines.append("Problem: " + str(getattr(problem, "prompt", ""))[:160])
    lines.append("Error type: " + str(diag.error_type.value))
    if diag.misconception_id:
        lines.append("Misconception: " + str(diag.misconception_id))
    lines.append("Action: " + str(action.value if action else "NONE"))
    if hint:
        lines.append("Use this hint: " + hint)
    lines.append("")
    lines.append("Write the reply now. Two sentences. Speak to the learner.")
    return "\n".join(lines)


def phrase_response(ctx: Dict[str, Any]) -> Optional[str]:
    if not llm_config.is_enabled():
        return None

    url = llm_config.get_url()
    key = llm_config.get_key()
    model = llm_config.get_model()
    timeout = llm_config.get_timeout()

    user_msg = _build_user_message(ctx)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": PHRASER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.5,
        "max_tokens": 80,
    }

    try:
        data = _post(url, key, payload, timeout)
    except (URLError, KeyError, ValueError, TimeoutError, OSError):
        return None

    try:
        text = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError):
        return None

    if not text:
        return None

    if text.startswith("```"):
        text = text.strip("`").strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    low = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in low:
            return None

    ok, _reason = is_seasoned(text)
    if not ok:
        ok2, _reason2 = is_seasoned_hint(text)
        if not ok2:
            return None

    return text
