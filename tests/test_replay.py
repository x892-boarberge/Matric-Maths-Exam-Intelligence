import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.event_log import SessionLogger, read_events
from src.tutor.schemas import EventType
from src.tutor.replay import replay_session


def test_replay_reconstructs_learner_state(tmp_path):
    log = tmp_path / "s.jsonl"
    lg = SessionLogger("s1", log)

    lg.emit(EventType.SESSION_STARTED, {})
    lg.emit(EventType.PROBLEM_PRESENTED, {"skill_id": "trig.reduction.simplify"})

    lg.begin_attempt()
    lg.emit(EventType.LEARNER_ATTEMPTED, {"response": "-sin theta"})
    lg.emit(
        EventType.DIAGNOSIS_MADE,
        {"error_type": "conceptual", "misconception_id": "M_REDUCTION_SIGN"},
    )
    lg.emit(EventType.INTERVENTION_SELECTED, {"provenance": "n08_backed"})
    lg.emit(EventType.HINT_ISSUED, {"hint_level": "H0"})
    lg.end_attempt()

    lg.begin_attempt()
    lg.emit(EventType.LEARNER_ATTEMPTED, {"response": "sin theta"})
    lg.emit(
        EventType.DIAGNOSIS_MADE,
        {"error_type": "none", "misconception_id": None},
    )
    lg.emit(EventType.INTERVENTION_SELECTED, {"provenance": "n08_backed"})
    lg.end_attempt()

    lg.close()

    state = replay_session(read_events(log))
    assert state.attempts_total == 2
    assert state.attempts_correct == 1
    assert state.error_history == ["M_REDUCTION_SIGN"]
