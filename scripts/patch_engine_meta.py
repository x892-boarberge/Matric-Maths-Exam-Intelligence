"""Wire the meta library into tutor_engine.py disengagement handling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# Add import
if "meta_library" not in src:
    src = src.replace(
        "from .disengagement import detect_disengagement, DisengagementKind\n",
        "from .disengagement import detect_disengagement, DisengagementKind\nfrom . import meta_library\n",
        1,
    )
    print("Added meta_library import")
else:
    print("meta_library already imported")

# Replace the three hardcoded disengagement branches
old_block = '''        # Override phrasing for disengagement (still no full solution)
        if diseng.kind == DisengagementKind.ANSWER_DEMAND and diag.error_type != ErrorType.NONE:
            message = (
                "I won't give the full solution yet. "
                "Let's take one useful step: what are you being asked to find?"
            )
            action_type = ActionType.HANDLE_DISENGAGEMENT
            engine_rule = "ENG_DISENGAGE_ANSWER_DEMAND"
        elif diseng.kind == DisengagementKind.FRUSTRATED and diag.error_type != ErrorType.NONE:
            message = (
                "Let's simplify. Ignore the whole problem for a moment — "
                "what is the single quantity this question asks for?"
            )
            action_type = ActionType.HANDLE_DISENGAGEMENT
            engine_rule = "ENG_DISENGAGE_FRUSTRATED"
        elif diseng.kind == DisengagementKind.HELP_SEEKING and diag.error_type != ErrorType.NONE:
            message = (
                "No problem — let's slow down. "
                "What is the single thing this question is asking you to find?"
            )
            action_type = ActionType.HANDLE_DISENGAGEMENT
            engine_rule = "ENG_DISENGAGE_HELP_SEEKING"'''

new_block = '''        # Override phrasing for disengagement (still no full solution)
        if diseng.kind != DisengagementKind.NONE and diag.error_type != ErrorType.NONE:
            # Count prior same-kind events in this session
            prior_same = sum(
                1 for e in learner_state.session_events
                if e.get("disengagement") == diseng.kind.value
            )
            meta_message = meta_library.respond_to_disengagement(
                diseng.kind.value,
                learner_id=learner_state.learner_id,
                attempts=prior_same,
            )
            if meta_message:
                message = meta_message
                action_type = ActionType.HANDLE_DISENGAGEMENT
                engine_rule = "ENG_DISENGAGE_" + diseng.kind.value.upper()'''

if old_block in src:
    src = src.replace(old_block, new_block, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("Engine disengagement block rewritten")
else:
    print("WARNING - old disengagement block not found. Inspect tutor_engine.py manually.")
