"""
Meta renderer.

For human-moment responses (hostile input, frustration, help-seeking,
answer demand, silence), try an LLM first. If unavailable, or the
response fails the salt check, fall back to the meta library pool.

The engine still decides everything. This module only phrases.

Public:
    render_meta_response(kind, learner_text, learner_id, attempts=None)
"""
import json
import hashlib
from typing import Optional
from urllib import request as _urllib_request
from urllib.error import URLError

from . import llm_config
from .meta_prompt import SYSTEM_PROMPT, build_user_prompt
from .salt_check import is_seasoned
from . import meta_library as _pool


# Simple in-process cache: (kind, hash(learner_text)) -> rendered string
_CACHE = {}
_MAX_CACHE = 500


def _cache_key(kind, learner_text):
    h = hashlib.sha256(str(learner_text).encode("utf-8")).hexdigest()[:16]
    return str(kind) + "|" + h


def _cache_get(key):
    return _CACHE.get(key)


def _cache_put(key, value):
    if len(_CACHE) > _MAX_CACHE:
        _CACHE.clear()
    _CACHE[key] = value


def _ask_llm(kind, learner_text, learner_id, attempts=None) -> Optional[str]:
    """Call the LLM. Return the text, or None on any error."""
    if not llm_config.is_enabled():
        return None

    url = llm_config.get_url()
    key = llm_config.get_key()
    model = llm_config.get_model()
    timeout = llm_config.get_timeout()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(
                kind, learner_text, learner_id, attempts)},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key

    req = _urllib_request.Request(url, data=body, headers=headers, method="POST")

    try:
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"].strip()
        return text
    except (URLError, KeyError, ValueError, TimeoutError, OSError):
        return None


def _sanitise(text: str) -> str:
    """Trim whitespace and strip surrounding quotes if present."""
    if not text:
        return ""
    t = text.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1].strip()
    return t


def render_meta_response(kind, learner_text, learner_id=None,
                         attempts=None, context=None) -> str:
    """
    Return a phrase for the learner's human moment.

    Order of preference:
      1. Cached LLM response (same learner text -> same phrase)
      2. Fresh LLM response, if it passes the salt check
      3. Meta library pool (always available)
    """
    key = _cache_key(kind, learner_text)

    cached = _cache_get(key)
    if cached:
        return cached

    # Try the LLM
    raw = _ask_llm(kind, learner_text, learner_id, attempts)
    if raw:
        candidate = _sanitise(raw)
        if candidate and len(candidate) < 500:
            ok, _reason = is_seasoned(candidate)
            if ok:
                _cache_put(key, candidate)
                return candidate

    # Fallback to the pool
    pool_line = _pool.respond_to_disengagement(
        kind,
        learner_id=learner_id,
        attempts=attempts,
    )
    if pool_line:
        return pool_line

    # Last resort
    return "Let us come back to the question. What is your first step?"
