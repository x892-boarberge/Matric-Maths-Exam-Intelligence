import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from .schemas import EventType, TutorEvent, EVENT_SCHEMA_VERSION


class SessionLogger:
    """Append-only JSONL session logger.

    Guarantees:
    - monotonic sequence numbers within a session
    - append-only writes
    - schema_version on every event
    - SESSION_ENDED carries integrity + R10 fallback summary
    """

    def __init__(self, session_id: str, log_path: Path):
        self.session_id = session_id
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._seq = 0
        self._current_attempt_id: Optional[str] = None
        self._counts = {
            "total_decisions": 0,
            "n08_backed": 0,
            "fallback": 0,
            "diagnoses": 0,
            "interventions": 0,
            "actions": 0,
        }
        self._integrity_errors: List[str] = []

    def begin_attempt(self) -> str:
        self._current_attempt_id = f"att_{uuid.uuid4().hex[:12]}"
        return self._current_attempt_id

    def end_attempt(self) -> None:
        self._current_attempt_id = None

    def emit(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        attempt_id: Optional[str] = None,
    ) -> str:
        self._seq += 1
        evt = TutorEvent(
            schema_version=EVENT_SCHEMA_VERSION,
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=self.session_id,
            sequence=self._seq,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            attempt_id=attempt_id if attempt_id is not None else self._current_attempt_id,
            payload=payload,
        )
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(evt.to_jsonl() + "\n")
        self._update_counts(event_type, payload)
        return evt.event_id

    def _update_counts(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        if event_type == EventType.DIAGNOSIS_MADE:
            self._counts["diagnoses"] += 1
        elif event_type == EventType.INTERVENTION_SELECTED:
            self._counts["interventions"] += 1
            self._counts["total_decisions"] += 1
            prov = payload.get("provenance")
            if prov == "n08_backed":
                self._counts["n08_backed"] += 1
            elif prov == "generic_fallback":
                self._counts["fallback"] += 1
        elif event_type in (EventType.HINT_ISSUED, EventType.TUTOR_MESSAGE):
            self._counts["actions"] += 1

    def close(self) -> Dict[str, Any]:
        """Emit SESSION_ENDED with integrity and fallback summary. Call once."""
        if self._counts["diagnoses"] != self._counts["interventions"]:
            self._integrity_errors.append(
                f"diagnosis/intervention mismatch: "
                f"{self._counts['diagnoses']} vs {self._counts['interventions']}"
            )

        total = self._counts["total_decisions"]
        fallback_ratio = (self._counts["fallback"] / total) if total else 0.0
        warning_raised = fallback_ratio > 0.30

        summary = {
            "total_decisions": total,
            "n08_backed": self._counts["n08_backed"],
            "fallback": self._counts["fallback"],
            "fallback_ratio": round(fallback_ratio, 4),
            "warning_raised": warning_raised,
            "integrity_errors": list(self._integrity_errors),
        }
        self.emit(EventType.SESSION_ENDED, summary)
        return summary


def read_events(log_path: Path) -> List[Dict[str, Any]]:
    events = []
    with Path(log_path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events