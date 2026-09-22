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
    DiagnosisResult,
)
from .diagnosis import diagnose
from .intervention_selector import select_intervention
from .hint_policy import select_hint_level
from .event_log import SessionLogger
from .disengagement import detect_disengagement, DisengagementKind
from . import meta_library
from . import meta_renderer
from . import analogue_library
from . import misconception_hints
from . import llm_phraser
from . import llm_gate


MASTERY_MIN_CORRECT = 3
MAX_ATTEMPTS_BEFORE_ANALOGUE = 6  # after this many real attempts, show a similar worked problem


class TutorEngine:
    """Rule-governed tutor engine. Engine decides; renderer phrases."""

    def __init__(
        self,
        phrase_renderer: Optional[Callable[[Dict[str, Any]], str]] = None,
        session_logger: Optional[SessionLogger] = None,
        use_llm_phraser: bool = True,
    ):
        self.phrase_renderer = phrase_renderer or self._default_renderer
        self.logger = session_logger
        self.use_llm_phraser = use_llm_phraser

    def step(
        self,
        learner_state: LearnerState,
        problem: Problem,
        learner_response: str,
        explicit_solution_request: bool = False,
    ) -> TutorAction:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # Disengagement (rule-based, not LLM)
        diseng = detect_disengagement(learner_response)
        if diseng.kind == DisengagementKind.ANSWER_DEMAND:
            explicit_solution_request = True

        if self.logger:
            self.logger.begin_attempt()
            self.logger.emit(
                EventType.LEARNER_ATTEMPTED,
                {
                    "response": learner_response,
                    "attempt_number": learner_state.attempts_total + 1,
                    "skill_id": problem.skill_id,
                    "problem_id": problem.problem_id,
                    "topic_v2": problem.topic_v2,
                    "disengagement": diseng.kind.value,
                },
            )

        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)

        # Near-miss detection: if the response is close to expected but not
        # exact, ask for clarification instead of saying "unknown".
        if diag.error_type == ErrorType.UNKNOWN:
            from .answer_matcher import near_miss
            if near_miss(learner_response, problem.expected_answer):
                diag = DiagnosisResult(
                    error_type=ErrorType.UNKNOWN,
                    misconception_id=None,
                    confidence=0.5,
                    rule_id="D_NEAR_MISS",
                    explanation="Response looks close to expected but not exact.",
                )

        # Count the attempt only when the learner actually attempted the maths.
        # Celebration, meta-comment, hostile, language, silence, and pure
        # answer-demand do not count as attempts, so they must not advance
        # the hint ladder.
        NON_ATTEMPT_KINDS = {
            "celebration",
            "meta_comment",
            "hostile",
            "other_language",
            "silent",
        }
        is_real_attempt = diseng.kind.value not in NON_ATTEMPT_KINDS
        # Also treat "answer_demand" as a non-attempt for ladder purposes
        if diseng.kind.value == "answer_demand":
            is_real_attempt = False

        if is_real_attempt:
            learner_state.attempts_total += 1

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
            # Frustrated → keep hint burden lower
            if diseng.kind == DisengagementKind.FRUSTRATED and hint_level in (
                HintLevel.H3,
                HintLevel.H4,
            ):
                hint_level = HintLevel.H1

            if hint_level == HintLevel.H4:
                action_type = ActionType.OFFER_WORKED_STEP
            elif hint_level in (HintLevel.H0, HintLevel.H1):
                action_type = ActionType.ASK_GUIDING_QUESTION
            else:
                action_type = ActionType.GIVE_HINT
            engine_rule = f"ENG_HINT_{hint_level.value}"

        if (
            learner_state.attempts_total >= MAX_ATTEMPTS_BEFORE_ANALOGUE
            and learner_state.attempts_correct == 0
        ):
            # Never end the session. Never label the learner.
            # Show a simpler worked problem of the same type, then invite
            # the learner to try the original again.
            # Has this analogue already been shown in this session?
            analogue_seen = any(
                e.get("kind") == "analogue_shown"
                and e.get("skill_id") == problem.skill_id
                for e in learner_state.session_events
            )

            if analogue_library.has_analogue(problem.skill_id) and not analogue_seen:
                action_type = ActionType.OFFER_WORKED_ANALOGUE
                engine_rule = "ENG_OFFER_ANALOGUE"
                learner_state.session_events.append({
                    "kind": "analogue_shown",
                    "skill_id": problem.skill_id,
                })
            elif analogue_seen:
                # The learner has already seen the analogue. Change tack.
                # Offer a break or a different approach.
                action_type = ActionType.GIVE_HINT
                hint_level = HintLevel.H2
                engine_rule = "ENG_BREAK_OR_PIVOT"
            else:
                action_type = ActionType.GIVE_HINT
                hint_level = HintLevel.H2
                engine_rule = "ENG_STEP_DOWN_NO_ANALOGUE"

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
            "disengagement": diseng.kind,
            "learner_response": learner_response,
            "engine_rule": engine_rule,
            "specific_hint": (
                misconception_hints.get_hint(diag.misconception_id, hint_level.value)
                if diag.misconception_id and hint_level else None
            ),
        }
        # Try the LLM phraser only when the gate says the LLM adds value.
        # Categorical states (celebration, hostile, help-seeking, meta,
        # language, silence, answer-demand, off-topic) use the pool
        # directly. Only genuine maths attempts go to the LLM.
        message = None
        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt
        ):
            phrased = llm_phraser.phrase_response(ctx)
            if phrased:
                message = phrased
                ctx["llm_used"] = True
        if message is None:
            message = self.phrase_renderer(ctx)
            ctx["llm_used"] = False

        # Override phrasing for disengagement (still no full solution)
        if diseng.kind != DisengagementKind.NONE and diag.error_type != ErrorType.NONE:
            # Count prior same-kind events in this session
            prior_same = sum(
                1 for e in learner_state.session_events
                if e.get("disengagement") == diseng.kind.value
            )
            # The pool handles these kinds more reliably than the LLM:
            #   celebration    - short acknowledgement, no variety needed
            #   meta_comment   - honest brief answer, LLM drifts
            #   other_language - LLM does not speak SA languages well
            #   silent         - one prompt, pool is fine
            POOL_ONLY_KINDS = {
                "celebration",
                "meta_comment",
                "other_language",
                "silent",
            }

            if diseng.kind.value in POOL_ONLY_KINDS:
                meta_message = meta_library.respond_to_disengagement(
                    diseng.kind.value,
                    learner_id=learner_state.learner_id,
                    attempts=prior_same,
                )
            else:
                meta_message = meta_renderer.render_meta_response(
                    diseng.kind.value,
                    learner_text=learner_response,
                    learner_id=learner_state.learner_id,
                    attempts=prior_same,
                )
            if meta_message:
                message = meta_message
                action_type = ActionType.HANDLE_DISENGAGEMENT
                engine_rule = "ENG_DISENGAGE_" + diseng.kind.value.upper()

        # Quiet struggle signal for the teacher dashboard (does not
        # affect what the learner sees)
        if (learner_state.attempts_total >= MAX_ATTEMPTS_BEFORE_ANALOGUE
                and learner_state.attempts_correct == 0):
            event_struggle = {
                "event_id": event_id + "_struggle",
                "timestamp": now,
                "skill_id": problem.skill_id,
                "attempts_total": learner_state.attempts_total,
                "kind": "deep_struggle",
            }
            learner_state.session_events.append(event_struggle)
            if self.logger:
                self.logger.emit(
                    EventType.ESCALATION_TRIGGERED,
                    {
                        "reason": "deep_struggle_logged",
                        "skill_id": problem.skill_id,
                        "attempts": learner_state.attempts_total,
                    },
                )

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
            "disengagement": diseng.kind.value,
        }
        learner_state.session_events.append(event)

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
            if engine_rule in (
                "ENG_ESCALATE_HUMAN",
                "ENG_DISENGAGE_ANSWER_DEMAND",
                "ENG_DISENGAGE_FRUSTRATED",
                "ENG_DISENGAGE_HELP_SEEKING",
            ):
                self.logger.emit(
                    EventType.ESCALATION_TRIGGERED,
                    {
                        "reason": engine_rule,
                        "phrase": diseng.matched_phrase,
                    },
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
        if a == ActionType.OFFER_WORKED_ANALOGUE:
            analogue = analogue_library.get_analogue(ctx["problem"].skill_id)
            if not analogue:
                return "Let's try a smaller version of this problem."
            lines = ["That has not gone well yet. Let's change the approach.",
                     "Here is a similar problem, worked through:",
                     "Problem: " + analogue["problem"]]
            for step in analogue["steps"]:
                lines.append("  " + step)
            lines.append("Note: " + analogue["note"])
            lines.append("When you are ready, try your problem again with this in front of you.")
            return "\n".join(lines)
        if h == HintLevel.H0:
            return "What are you being asked to find in this step?"
        if h == HintLevel.H1:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H1")
                if specific:
                    return specific
            return "Think about the concept here. What rule or formula applies to this step?"
        if h == HintLevel.H2:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H2")
                if specific:
                    return specific
            return "Try identifying the operation you need before computing."
        if h == HintLevel.H3:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H3")
                if specific:
                    return specific
            return "Here is one step to try. Complete the rest yourself."
        if h == HintLevel.H4:
            return "Let's walk through this together, one step at a time."
        return "Let's continue."