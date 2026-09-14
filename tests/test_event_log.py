import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.tutor.event_log import SessionLogger, read_events
from src.tutor.schemas import EventType


def test_append_only_and_sequence(tmp_path):
    log = tmp_path / "session.jsonl"
    lg = SessionLogger("s1", log)
    lg.emit(EventType.SESSION_STARTED, {"learner": "L1"})
    lg.emit(EventType.LEARNER_ATTEMPTED, {"response": "x=1"})
    lg.close()

    events = read_events(log)
    seqs = [e["sequence"] for e in events]
    assert seqs == sorted(seqs)
    assert len(seqs) == len(set(seqs))


def test_schema_version_on_every_event(tmp_path):
    log = tmp_path / "session.jsonl"
    lg = SessionLogger("s1", log)
    lg.emit(EventType.SESSION_STARTED, {})
    lg.close()
    for e in read_events(log):
        assert e["schema_version"] == "1.0"


def test_session_ended_carries_fallback_summary(tmp_path):
    log = tmp_path / "session.jsonl"
    lg = SessionLogger("s1", log)
    for _ in range(5):
        lg.emit(EventType.INTERVENTION_SELECTED, {"provenance": "n08_backed"})
    for _ in range(5):
        lg.emit(EventType.INTERVENTION_SELECTED, {"provenance": "generic_fallback"})
    summary = lg.close()

    assert summary["total_decisions"] == 10
    assert summary["fallback"] == 5
    assert summary["fallback_ratio"] == 0.5
    assert summary["warning_raised"] is True
