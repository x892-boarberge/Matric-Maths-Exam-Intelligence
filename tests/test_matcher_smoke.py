"""Smoke tests for Mapping v2."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mapping.signatures import load_signatures, match_signatures
from src.mapping.structural import load_struct_rules, match_struct
from src.mapping.lexicon import load_lexicon
from src.mapping.matcher import map_v2_final

sig_df = load_signatures()
struct_rules = load_struct_rules()
token_map = load_lexicon()


def test_signatures_load():
    assert len(sig_df) > 100
    assert "topic_id" in sig_df.columns


def test_struct_loads():
    assert len(struct_rules) == 14


def test_lexicon_loads():
    assert len(token_map) > 100


def test_match_signatures_basic():
    hits = match_signatures("Solve for x: x2 + 5x - 6 = 0", sig_df)
    assert len(hits) >= 1


def test_match_struct_calculus():
    hits = match_struct("Determine f'(x) from first principles", struct_rules)
    topics = [h["topic_id"] for h in hits]
    assert "CALC" in topics


def test_match_struct_blocks_alg_on_calc():
    hits = match_struct("g'(x) if g(x) = -3x* + 2x", struct_rules)
    topics = [h["topic_id"] for h in hits]
    assert "ALG" not in topics


def test_map_v2_final_returns_dict():
    pred = map_v2_final("Solve for x", "P1", sig_df, token_map, struct_rules)
    assert "topic_id" in pred
    assert "method" in pred
    assert "confidence" in pred
    assert "signature_id" in pred


def test_map_v2_final_empty_text():
    pred = map_v2_final("", "P1", sig_df, token_map, struct_rules)
    assert pred["topic_id"] is None
    assert pred["method"] == "no_text"
