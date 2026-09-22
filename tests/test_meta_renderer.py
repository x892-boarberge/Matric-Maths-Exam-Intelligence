"""Tests for the meta renderer with a mocked LLM."""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor import meta_renderer
from src.tutor import llm_config


def test_fallback_when_llm_disabled():
    with patch.object(llm_config, "is_enabled", return_value=False):
        result = meta_renderer.render_meta_response(
            "frustrated", "this is too hard", learner_id="L001"
        )
    assert isinstance(result, str)
    assert len(result) > 20


def test_llm_response_used_when_salted():
    good = "I hear you. Let us slow down. What is one thing you do understand?"
    with patch.object(llm_config, "is_enabled", return_value=True), \
         patch.object(meta_renderer, "_ask_llm", return_value=good):
        result = meta_renderer.render_meta_response(
            "frustrated", "this is too hard", learner_id="L002"
        )
    assert result == good


def test_llm_response_rejected_when_unsalted():
    bad = "You must try harder. This is easy."
    with patch.object(llm_config, "is_enabled", return_value=True), \
         patch.object(meta_renderer, "_ask_llm", return_value=bad):
        result = meta_renderer.render_meta_response(
            "frustrated", "this is too hard", learner_id="L003"
        )
    assert result != bad


def test_llm_response_rejected_when_leaks():
    leak = "No matching pattern after normalisation."
    with patch.object(llm_config, "is_enabled", return_value=True), \
         patch.object(meta_renderer, "_ask_llm", return_value=leak):
        result = meta_renderer.render_meta_response(
            "hostile", "fuck off", learner_id="L004"
        )
    assert result != leak


def test_same_learner_text_uses_cache():
    good = "Okay. Let us shrink it. What is the first thing the question asks?"
    meta_renderer._CACHE.clear()
    with patch.object(llm_config, "is_enabled", return_value=True), \
         patch.object(meta_renderer, "_ask_llm", return_value=good):
        first = meta_renderer.render_meta_response(
            "help_seeking", "i dont understand unique text", learner_id="L005"
        )
        with patch.object(meta_renderer, "_ask_llm") as mock_llm:
            second = meta_renderer.render_meta_response(
                "help_seeking", "i dont understand unique text", learner_id="L005"
            )
            assert second == first
            mock_llm.assert_not_called()
