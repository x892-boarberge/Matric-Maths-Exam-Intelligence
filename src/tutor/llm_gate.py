"""
LLM gate.

Decides whether the LLM phraser should be called for a given turn.
Categorical states and fixed documents use the pool. The LLM is only
used to rephrase short hint texts in fluent, varied language.
"""

POOL_ONLY_KINDS = {
    "celebration",
    "hostile",
    "meta_comment",
    "other_language",
    "silent",
    "answer_demand",
    "off_topic",
    "help_seeking",
}

FIXED_ACTIONS = {
    "OFFER_WORKED_ANALOGUE",
    "OFFER_WORKED_STEP",
    "FLAG_FOR_HUMAN",
    "HANDLE_DISENGAGEMENT",
}


def should_call_llm(disengagement_kind, is_real_attempt, action_type=None):
    if disengagement_kind in POOL_ONLY_KINDS:
        return False
    if action_type in FIXED_ACTIONS:
        return False
    return bool(is_real_attempt)
