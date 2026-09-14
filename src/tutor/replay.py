from typing import Dict, Any, List

from .schemas import LearnerState, MasteryState, HintLevel, ErrorType


def replay_session(events: List[Dict[str, Any]]) -> LearnerState:
    """Reconstruct LearnerState from an event log alone."""
    if not events:
        raise ValueError("Empty event log.")

    events_sorted = sorted(events, key=lambda e: e["sequence"])

    state = LearnerState(
        learner_id="<replayed>",
        skill_id="<replayed>",
        current_session_id=events_sorted[0]["session_id"],
    )
    state.session_events = []
    state.hint_history = []
    state.error_history = []

    for evt in events_sorted:
        t = evt["event_type"]
        p = evt.get("payload", {})

        if t == "PROBLEM_PRESENTED":
            state.skill_id = p.get("skill_id", state.skill_id)

        elif t == "LEARNER_ATTEMPTED":
            state.attempts_total += 1

        elif t == "DIAGNOSIS_MADE":
            if p.get("error_type") == ErrorType.NONE.value:
                state.attempts_correct += 1
            mid = p.get("misconception_id")
            if mid:
                state.error_history.append(mid)

        elif t == "HINT_ISSUED":
            level = p.get("hint_level")
            if level:
                state.hint_history.append(HintLevel(level))

        elif t == "MASTERY_UPDATED":
            if p.get("mastery_state"):
                state.mastery_state = MasteryState(p["mastery_state"])

        state.session_events.append(evt)

    return state
