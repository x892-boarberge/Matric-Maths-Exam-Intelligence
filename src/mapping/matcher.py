"""
Full mapping pipeline for Mapping v2.

map_v2_final() is the single entry point. It runs the cascade:

    1. Signature + structural matching (combined, ranked together)
    2. Lexicon matching
    3. Unmapped

Signatures and structural rules are COMBINED into one candidate list
before ranking. A high-confidence STRUCT rule can outrank a
medium-confidence signature.

The paper prior kills weak cross-paper hits: on P1, a low-confidence
match to a P2-only topic is discarded, and vice versa.

Public function:
    map_v2_final(text, paper, sig_df, token_map, struct_rules) -> dict
"""
from .signatures import match_signatures, pick_best_signature
from .structural import match_struct
from .lexicon import match_lexicon


P1_OK = {"ALG", "SEQ", "FIN", "FUNC", "CALC", "PROB"}
P2_OK = {"STAT", "AGEO", "TRIG", "EUCL"}


def map_v2_final(text, paper, sig_df, token_map, struct_rules):
    """
    Map a question to a v2 topic_id.

    Args:
        text:         the question text
        paper:        "P1" or "P2"
        sig_df:       load_signatures() output
        token_map:    load_lexicon() output
        struct_rules: load_struct_rules() output

    Returns:
        dict with keys:
            topic_id      (str or None)
            method        ("signature" | "struct" | "lexicon" | "unmapped")
            confidence    ("high" | "medium" | "low" | None)
            signature_id  (str or None)
    """
    if not isinstance(text, str) or not text.strip():
        return {"topic_id": None, "method": "no_text",
                "confidence": None, "signature_id": None}

    # ---- Stage 1: signatures + struct, COMBINED ----
    sig_hits = match_signatures(text, sig_df,
                                usage_filter={"PRIMARY", "SECONDARY"})
    struct_hits = match_struct(text, struct_rules)
    all_hits = sig_hits + struct_hits

    best = pick_best_signature(all_hits)
    if best:
        topic_id = best["topic_id"]
        conf = best["confidence"]

        # Paper prior: kill weak cross-paper hits
        if paper == "P1" and topic_id in P2_OK and conf == "low":
            topic_id = None
        elif paper == "P2" and topic_id in P1_OK and conf == "low":
            topic_id = None

        if topic_id:
            method = "struct" if str(best["signature_id"]).startswith("STRUCT_") else "signature"
            return {
                "topic_id":     topic_id,
                "method":       method,
                "confidence":   conf,
                "signature_id": best["signature_id"],
            }

    # ---- Stage 2: lexicon ----
    votes = match_lexicon(text, token_map)
    if votes:
        top_topic, weight = votes[0]
        if paper == "P1" and top_topic in P2_OK:
            top_topic = None
        elif paper == "P2" and top_topic in P1_OK:
            top_topic = None
        if top_topic:
            return {
                "topic_id":     top_topic,
                "method":       "lexicon",
                "confidence":   "medium" if weight >= 10 else "low",
                "signature_id": None,
            }

    # ---- Stage 3: unmapped ----
    return {"topic_id": None, "method": "unmapped",
            "confidence": None, "signature_id": None}
    