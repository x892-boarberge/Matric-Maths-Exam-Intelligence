"""MatricMath Tutor — behaviour test suite (skeleton)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TutorState:
    topic: str
    hint_level: str
    attempt_count: int
    intervention_id: str
    n08_trace: bool
    misconception_id: Optional[str] = None
    engagement_state: str = "active"
    solution_policy: str = "never_full_solution_first"


@dataclass
class TutorResponse:
    tutor_message: str
    ask: str
    hint_level_used: str
    n08_linked: bool
    intervention_id: str
    rules_respected: List[str] = field(default_factory=list)
    contains_full_solution: bool = False
    declares_mastery: bool = False
    shaming_language: bool = False


def assert_r1_never_solution_first(state: TutorState, resp: TutorResponse) -> None:
    if state.hint_level != "H4":
        assert not resp.contains_full_solution, "R1 violated: full solution before H4"


def assert_r2_diagnose_before_intervene(state: TutorState, resp: TutorResponse) -> None:
    assert (
        state.misconception_id is not None
        or state.intervention_id == "generic_fallback"
    ), "R2 violated: intervene without diagnosis/fallback"


def assert_r3_one_target(state: TutorState, resp: TutorResponse) -> None:
    assert state.misconception_id is None or "," not in str(state.misconception_id), (
        "R3 violated: multiple misconception targets"
    )


def assert_r5_hint_level_match(state: TutorState, resp: TutorResponse) -> None:
    assert resp.hint_level_used == state.hint_level, (
        f"R5 violated: used {resp.hint_level_used}, policy said {state.hint_level}"
    )


def assert_r7_no_self_mastery(resp: TutorResponse) -> None:
    assert not resp.declares_mastery, "R7 violated: LLM declared mastery"


def assert_r10_trace_flag(state: TutorState, resp: TutorResponse) -> None:
    assert resp.n08_linked == state.n08_trace, "R10 violated: N08 link mismatch"


def assert_no_shame(resp: TutorResponse) -> None:
    assert not resp.shaming_language, "Tone rule violated: shaming language"


def run_basic_suite(cases):
    failures = []
    for i, (state, resp) in enumerate(cases):
        try:
            assert_r1_never_solution_first(state, resp)
            assert_r2_diagnose_before_intervene(state, resp)
            assert_r3_one_target(state, resp)
            assert_r5_hint_level_match(state, resp)
            assert_r7_no_self_mastery(resp)
            assert_r10_trace_flag(state, resp)
            assert_no_shame(resp)
        except AssertionError as e:
            failures.append({"case": i, "error": str(e)})
    return {
        "passed": len(cases) - len(failures),
        "failed": len(failures),
        "failures": failures,
    }


EXAMPLE_CASES = [
    (
        TutorState(
            topic="Trigonometry",
            hint_level="H1",
            attempt_count=2,
            intervention_id="trigonometry__formula_identity_error",
            n08_trace=True,
            misconception_id="formula_identity_error",
        ),
        TutorResponse(
            tutor_message="Think about which identity applies to this angle.",
            ask="Which reduction formula are you considering?",
            hint_level_used="H1",
            n08_linked=True,
            intervention_id="trigonometry__formula_identity_error",
            rules_respected=["R1", "R2", "R5"],
            contains_full_solution=False,
        ),
    ),
    (
        TutorState(
            topic="Calculus",
            hint_level="H0",
            attempt_count=1,
            intervention_id="generic_fallback",
            n08_trace=False,
            misconception_id=None,
        ),
        TutorResponse(
            tutor_message="What is the question asking you to find?",
            ask="What is the unknown?",
            hint_level_used="H0",
            n08_linked=False,
            intervention_id="generic_fallback",
            contains_full_solution=False,
        ),
    ),
]


if __name__ == "__main__":
    result = run_basic_suite(EXAMPLE_CASES)
    print(result)
    if result["failed"]:
        raise SystemExit(1)
    print("tutor_test_suite: basic fixtures passed")
