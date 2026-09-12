# Tutor Behaviour Specification v1

Generated: 2026-09-12T22:15:35.624263+00:00

## Audience
Young NSC Mathematics learner (Grade 10–12 range). No fixed age assumption.

## Core claim
Evidence-driven tutoring: DBE diagnostic errors → N06 → N07 → N08 → tutor action.

## Hard rules
{
  "R1_never_solution_first": true,
  "R2_diagnose_before_intervene": true,
  "R3_one_intervention_target": true,
  "R4_prefer_learner_reasoning": true,
  "R5_escalate_hints_gradually": true,
  "R6_retest_after_intervention": true,
  "R7_evidence_for_mastery": true,
  "R8_transfer_before_mastery": true,
  "R9_repeated_failure_remediate_not_harder": true,
  "R10_n08_trace_min_share": 0.7
}

## Hint policy
{
  "levels": {
    "H0": "Socratic prompt only",
    "H1": "Conceptual pointer",
    "H2": "Strategic operation hint",
    "H3": "One micro-step only",
    "H4": "Stepwise solution with teach-back (never dump)"
  },
  "escalation": {
    "type": "hybrid_attempt_primary",
    "attempt_map": {
      "1": "H0",
      "2": "H1",
      "3": "H2",
      "4": "H3",
      "5": "H4"
    },
    "silence_seconds_offer_hint": 90,
    "explicit_answer_request": "one_more_H2_then_stepwise_H4"
  }
}

## Mastery hierarchy
{
  "session_mastery": {
    "source": "N08",
    "correct_required": 4,
    "items_presented": 5,
    "unseen_only": true,
    "structure_type_match": true,
    "sittings_required_for_skill": 2
  },
  "skill_mastery": {
    "source": "N09",
    "min_sessions_passed": 2,
    "max_hints_on_final_session": 1,
    "no_target_misconception_recurrence": true,
    "require_transfer_item": true
  }
}

## LLM boundary
- LLM may classify free-text errors and render hint text at a rule-assigned level.
- LLM may not choose intervention, hint level, or mastery outcome.

## SA constraints
- Persist state across disconnect (load-shedding / data drop).
- Accept code-switching; respond in dominant language of learner input.
- Never shame; acknowledge frustration; reduce difficulty before continuing.

## Provenance
Every tutor event must log: session_event_id, intervention_id (or generic_fallback),
topic, misconception_id, hint_level, rule_ids_fired.
