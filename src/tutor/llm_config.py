"""
LLM configuration for the meta renderer.

Reads environment variables. If MATRICMATH_LLM_URL is not set, the LLM
is disabled and the meta library pool is used as the only source.

Supported:
    MATRICMATH_LLM_URL     - OpenAI-compatible endpoint
                             (e.g. https://api.openai.com/v1/chat/completions
                              or http://localhost:11434/v1/chat/completions)
    MATRICMATH_LLM_KEY     - API key (optional for local models)
    MATRICMATH_LLM_MODEL   - model name (default: gpt-4o-mini)
    MATRICMATH_LLM_TIMEOUT - seconds (default: 8)
    MATRICMATH_LLM_OFF     - set to "1" to force disable
"""
import os


def is_enabled() -> bool:
    if os.environ.get("MATRICMATH_LLM_OFF") == "1":
        return False
    return bool(os.environ.get("MATRICMATH_LLM_URL"))


def get_url() -> str:
    return os.environ.get("MATRICMATH_LLM_URL", "")


def get_key() -> str:
    return os.environ.get("MATRICMATH_LLM_KEY", "")


def get_model() -> str:
    return os.environ.get("MATRICMATH_LLM_MODEL", "gpt-4o-mini")


def get_timeout() -> float:
    try:
        return float(os.environ.get("MATRICMATH_LLM_TIMEOUT", "8"))
    except ValueError:
        return 8.0
