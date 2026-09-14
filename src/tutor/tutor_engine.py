from datetime import datetime, timezone
from typing import Optional, Callable, Dict, Any
import uuid

from .schemas import (
    LearnerState,
    Problem,
    TutorAction,
    ActionType,
    HintLevel,
    ErrorType,
    MasteryState,
    ProvenanceKind,
    InterventionSelection,
    EventType,
)
from .diagnosis import diagnose
from .intervention_selector import select_intervention
from .hint_policy import select_hint_level
from .event_log import SessionLogger


MASTERY_MIN_CORRECT = 3
MAX_ATTEMPTS_BEFORE_HUMAN = 6


class TutorEngine:
    """Rule-governed tutor engine. Engine decides; renderer phrases."""

    def __init__(
        self,
        phrase_renderer: Optional[Callable[[Dict[str, Any]], str]] = None,
        session_logger: Optional[SessionLogger] = None,
    ):
        self.phrase_renderer = phrase_renderer or self._default_renderer
        self.logger = session_logger

    def step(
        self,
        learner_state: LearnerState,
        problem: Problem,
        learner_response: str,
        explicit_solution_request: bool = False,
    ) -> TutorAction:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # --- logging: learner attempt ---
        if self.logger:
            self.logger.begin_attempt()
            self.logger.emit(
                EventType.LEARNER_ATTEMPTED,
                {
                    "response": learner_response,
                    "attempt_number": learner_state.attempts_total + 1,
                    "skill_id": problem.skill_id,
                    "problem_id": problem.problem_id,
                },
            )

        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)
        learner_state.attempts_total += 1

        # --- logging: diagnosis ---
        if self.logger:
            self.logger.emit(
                EventType.DIAGNOSIS_MADE,
                {
                    "error_type": diag.error_type.value,
                    "misconception_id": diag.misconception_id,
                    "confidence": diag.confidence,
                    "rule_id": diag.rule_id,
                },
            )

        if diag.error_type == ErrorType.NONE:
            learner_state.attempts_correct += 1
            action_type = ActionType.ACKNOWLEDGE_CORRECT
            hint_level = None
            intervention = InterventionSelection(
                intervention_pattern="NONE",
                provenance=ProvenanceKind.N08_BACKED,
                n08_intervention_id=None,
                rule_id="ISEL_CORRECT_NOOP",
                notes="Correct response; no intervention required.",
            )
            engine_rule = "ENG_CORRECT"
        else:
            intervention = select_intervention(diag)
            hint_level = select_hint_level(
                attempts_total=learner_state.attempts_total,
                error_type=diag.error_type,
                explicit_request=explicit_solution_request,
            )
            if hint_level == HintLevel.H4:
                action_type = ActionType.OFFER_WORKED_STEP
            elif hint_level in (HintLevel.H0, HintLevel.H1):
                action_type = ActionType.ASK_GUIDING_QUESTION
            else:
                action_type = ActionType.GIVE_HINT
            engine_rule = f"ENG_HINT_{hint_level.value}"

        if (
            learner_state.attempts_total >= MAX_ATTEMPTS_BEFORE_HUMAN
            and learner_state.attempts_correct == 0
        ):
            action_type = ActionType.FLAG_FOR_HUMAN
            engine_rule = "ENG_ESCALATE_HUMAN"

        if hint_level:
            learner_state.hint_history.append(hint_level)
        if diag.misconception_id:
            learner_state.error_history.append(diag.misconception_id)
        learner_state.last_response_at = now
        learner_state.mastery_state = self._evaluate_mastery(learner_state)

        ctx = {
            "problem": problem,
            "diagnosis": diag,
            "intervention": intervention,
            "hint_level": hint_level,
            "action_type": action_type,
            "learner_state": learner_state,
        }
        message = self.phrase_renderer(ctx)

        event = {
            "event_id": event_id,
            "timestamp": now,
            "skill_id": problem.skill_id,
            "attempts_total": learner_state.attempts_total,
            "diagnosis_rule": diag.rule_id,
            "misconception_id": diag.misconception_id,
            "intervention_rule": intervention.rule_id,
            "intervention_provenance": intervention.provenance.value,
            "hint_level": hint_level.value if hint_level else None,
            "action": action_type.value,
            "engine_rule": engine_rule,
        }
        learner_state.session_events.append(event)

        # --- logging: intervention / hint / message / mastery ---
        if self.logger:
            self.logger.emit(
                EventType.INTERVENTION_SELECTED,
                {
                    "intervention_pattern": intervention.intervention_pattern,
                    "provenance": intervention.provenance.value,
                    "n08_intervention_id": intervention.n08_intervention_id,
                    "rule_id": intervention.rule_id,
                },
            )
            if intervention.provenance.value == "generic_fallback":
                self.logger.emit(
                    EventType.FALLBACK_USED,
                    {"reason": intervention.notes},
                )
            if engine_rule == "ENG_ESCALATE_HUMAN":
                self.logger.emit(
                    EventType.ESCALATION_TRIGGERED,
                    {"reason": "max_attempts_without_success"},
                )
            self.logger.emit(
                EventType.HINT_ISSUED,
                {
                    "hint_level": hint_level.value if hint_level else None,
                    "action": action_type.value,
                    "engine_rule": engine_rule,
                },
            )
            self.logger.emit(
                EventType.TUTOR_MESSAGE,
                {"message": message},
            )
            self.logger.emit(
                EventType.MASTERY_UPDATED,
                {"mastery_state": learner_state.mastery_state.value},
            )
            self.logger.end_attempt()

        return TutorAction(
            action=action_type,
            hint_level=hint_level,
            diagnosis=diag,
            intervention=intervention,
            tutor_message=message,
            next_state=learner_state,
            rule_id=engine_rule,
            session_event_id=event_id,
        )

    def _evaluate_mastery(self, state: LearnerState) -> MasteryState:
        if state.attempts_correct >= MASTERY_MIN_CORRECT:
            return MasteryState.MASTERED
        if state.attempts_correct >= 1:
            return MasteryState.PRACTISING
        return MasteryState.NOT_STARTED

    def _default_renderer(self, ctx) -> str:
        a = ctx["action_type"]
        h = ctx["hint_level"]
        d = ctx["diagnosis"]

        if a == ActionType.ACKNOWLEDGE_CORRECT:
            return "Good — that step is correct. Let's keep going."
        if a == ActionType.FLAG_FOR_HUMAN:
            return (
                "I'm seeing a persistent difficulty here. Let's step back "
                "and rebuild this concept from the basics. I'll flag this "
                "for your teacher."
            )
        if h == HintLevel.H0:
            return "What are you being asked to find in this step?"
        if h == HintLevel.H1:
            return f"Think about the concept here. {d.explanation}"
        if h == HintLevel.H2:
            return "Try identifying the operation you need before computing."
        if h == HintLevel.H3:
            return "Here is one step to try. Complete the rest yourself."
        if h == HintLevel.H4:
            return "Let's walk through this together, one step at a time."
        return "Let's continue."
