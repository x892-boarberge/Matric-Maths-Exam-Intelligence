from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any
import json


class HintLevel(str, Enum):
    H0 = "H0"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"


class ErrorType(str, Enum):
    NONE = "none"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    ARITHMETIC = "arithmetic"
    REPRESENTATION = "representation"
    STRATEGY = "strategy"
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    ACKNOWLEDGE_CORRECT = "ACKNOWLEDGE_CORRECT"
    ASK_GUIDING_QUESTION = "ASK_GUIDING_QUESTION"
    GIVE_HINT = "GIVE_HINT"
    OFFER_WORKED_STEP = "OFFER_WORKED_STEP"
    FLAG_FOR_HUMAN = "FLAG_FOR_HUMAN"
    HANDLE_DISENGAGEMENT = "HANDLE_DISENGAGEMENT"


class MasteryState(str, Enum):
    NOT_STARTED = "not_started"
    PRACTISING = "practising"
    NEAR_MASTERY = "near_mastery"
    MASTERED = "mastered"


class ProvenanceKind(str, Enum):
    N08_BACKED = "n08_backed"
    GENERIC_FALLBACK = "generic_fallback"


@dataclass
class Problem:
    problem_id: str
    skill_id: str
    topic: str
    subtopic: str
    structure_type: str
    prompt: str
    expected_answer: str


@dataclass
class LearnerState:
    learner_id: str
    skill_id: str
    mastery_state: MasteryState = MasteryState.NOT_STARTED
    attempts_total: int = 0
    attempts_correct: int = 0
    hint_history: List[HintLevel] = field(default_factory=list)
    error_history: List[str] = field(default_factory=list)
    current_session_id: str = ""
    session_events: List[Dict[str, Any]] = field(default_factory=list)
    last_response_at: Optional[str] = None


@dataclass
class DiagnosisResult:
    error_type: ErrorType
    misconception_id: Optional[str]
    confidence: float
    rule_id: str
    explanation: str


@dataclass
class InterventionSelection:
    intervention_pattern: str
    provenance: ProvenanceKind
    n08_intervention_id: Optional[str]
    rule_id: str
    notes: str = ""


@dataclass
class TutorAction:
    action: ActionType
    hint_level: Optional[HintLevel]
    diagnosis: DiagnosisResult
    intervention: InterventionSelection
    tutor_message: str
    next_state: LearnerState
    rule_id: str
    session_event_id: str


class EventType(str, Enum):
    SESSION_STARTED = "SESSION_STARTED"
    PROBLEM_PRESENTED = "PROBLEM_PRESENTED"
    LEARNER_ATTEMPTED = "LEARNER_ATTEMPTED"
    DIAGNOSIS_MADE = "DIAGNOSIS_MADE"
    INTERVENTION_SELECTED = "INTERVENTION_SELECTED"
    HINT_ISSUED = "HINT_ISSUED"
    TUTOR_MESSAGE = "TUTOR_MESSAGE"
    MASTERY_UPDATED = "MASTERY_UPDATED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    FALLBACK_USED = "FALLBACK_USED"
    SESSION_ENDED = "SESSION_ENDED"


EVENT_SCHEMA_VERSION = "1.0"


@dataclass
class TutorEvent:
    schema_version: str
    event_id: str
    session_id: str
    sequence: int
    timestamp: str
    event_type: EventType
    attempt_id: Optional[str]
    payload: Dict[str, Any]

    def to_jsonl(self) -> str:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        return json.dumps(d, ensure_ascii=False, default=str)
