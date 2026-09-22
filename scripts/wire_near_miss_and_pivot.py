"""Wire near_miss detection and pivot renderer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# ---------- Import DiagnosisResult if not already ----------
if "DiagnosisResult," not in src:
    src = src.replace(
        "    ProvenanceKind,\n    InterventionSelection,\n    EventType,\n)",
        "    ProvenanceKind,\n    InterventionSelection,\n    EventType,\n    DiagnosisResult,\n)",
        1,
    )
    print("DiagnosisResult imported")
else:
    print("DiagnosisResult already imported")

# ---------- Near-miss injection after diagnose ----------
old_diag = "        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)\n"
new_diag = '''        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)

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
'''
if "D_NEAR_MISS" not in src:
    if old_diag in src:
        src = src.replace(old_diag, new_diag, 1)
        print("Near-miss injection added")
    else:
        print("WARNING - diagnose line not found")
else:
    print("Near-miss already present")

# ---------- Add learner_response and engine_rule to ctx ----------
old_ctx = '''        ctx = {
            "problem": problem,
            "diagnosis": diag,
            "intervention": intervention,
            "hint_level": hint_level,
            "action_type": action_type,
            "learner_state": learner_state,
            "disengagement": diseng.kind,
        }'''

new_ctx = '''        ctx = {
            "problem": problem,
            "diagnosis": diag,
            "intervention": intervention,
            "hint_level": hint_level,
            "action_type": action_type,
            "learner_state": learner_state,
            "disengagement": diseng.kind,
            "learner_response": learner_response,
            "engine_rule": engine_rule,
        }'''

if "learner_response\": learner_response" not in src:
    if old_ctx in src:
        src = src.replace(old_ctx, new_ctx, 1)
        print("ctx extended with learner_response and engine_rule")
    else:
        print("WARNING - ctx dict not found")
else:
    print("ctx already extended")

# ---------- Add renderer branches ----------
old_render_head = '''        if a == ActionType.ACKNOWLEDGE_CORRECT:
            return "Good — that step is correct. Let's keep going."
        if a == ActionType.FLAG_FOR_HUMAN:'''

new_render_head = '''        # Near-miss clarification
        if d.rule_id == "D_NEAR_MISS":
            learner = ctx.get("learner_response", "")
            expected = ctx["problem"].expected_answer
            return ("I read your answer as '" + learner + "'. That looks close "
                    "to the target. Did you mean " + expected + "?")

        # Pivot after the analogue has already fired
        if ctx.get("engine_rule") == "ENG_BREAK_OR_PIVOT":
            return ("We have tried that approach together. Let us change tack. "
                    "Either take a break or try a different question from the menu. "
                    "If you want to keep going on this one, tell me which step is unclear.")

        if a == ActionType.ACKNOWLEDGE_CORRECT:
            return "Good — that step is correct. Let's keep going."
        if a == ActionType.FLAG_FOR_HUMAN:'''

if "D_NEAR_MISS" not in src.split("_default_renderer")[-1].split("return")[0]:
    if old_render_head in src:
        src = src.replace(old_render_head, new_render_head, 1)
        print("Renderer branches added")
    else:
        print("WARNING - renderer head not found")
else:
    print("Renderer already has near-miss branch")

ENGINE.write_text(src, encoding="utf-8")
print("patch complete")
