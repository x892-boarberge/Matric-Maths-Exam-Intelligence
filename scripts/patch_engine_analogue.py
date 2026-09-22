"""Replace FLAG_FOR_HUMAN with OFFER_WORKED_ANALOGUE."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# 1. Add import
if "analogue_library" not in src:
    src = src.replace(
        "from . import meta_renderer\n",
        "from . import meta_renderer\nfrom . import analogue_library\n",
        1,
    )
    print("analogue_library imported")

# 2. Rename constant
if "MAX_ATTEMPTS_BEFORE_HUMAN = 6" in src:
    src = src.replace(
        "MAX_ATTEMPTS_BEFORE_HUMAN = 6",
        "MAX_ATTEMPTS_BEFORE_ANALOGUE = 6  # after this many real attempts, show a similar worked problem",
        1,
    )
    print("constant renamed")

# 3. Replace the escalation block
old_block = '''        if (
            learner_state.attempts_total >= MAX_ATTEMPTS_BEFORE_HUMAN
            and learner_state.attempts_correct == 0
        ):
            action_type = ActionType.FLAG_FOR_HUMAN
            engine_rule = "ENG_ESCALATE_HUMAN"'''

new_block = '''        if (
            learner_state.attempts_total >= MAX_ATTEMPTS_BEFORE_ANALOGUE
            and learner_state.attempts_correct == 0
        ):
            # Never end the session. Never label the learner.
            # Show a simpler worked problem of the same type, then invite
            # the learner to try the original again.
            if analogue_library.has_analogue(problem.skill_id):
                action_type = ActionType.OFFER_WORKED_ANALOGUE
                engine_rule = "ENG_OFFER_ANALOGUE"
            else:
                # No analogue exists for this skill; keep the session open
                # with a gentle step-down hint instead.
                action_type = ActionType.GIVE_HINT
                hint_level = HintLevel.H2
                engine_rule = "ENG_STEP_DOWN_NO_ANALOGUE"'''

if old_block in src:
    src = src.replace(old_block, new_block, 1)
    print("escalation block replaced")
else:
    print("WARNING - escalation block not found")

# 4. Update the renderer
old_render = '''        if a == ActionType.FLAG_FOR_HUMAN:
            return (
                "I'm seeing a persistent difficulty here. Let's step back "
                "and rebuild this concept from the basics. I'll flag this "
                "for your teacher."
            )'''

new_render = '''        if a == ActionType.OFFER_WORKED_ANALOGUE:
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
            return "\\n".join(lines)'''

if old_render in src:
    src = src.replace(old_render, new_render, 1)
    print("renderer updated")
else:
    print("WARNING - old renderer block not found")

# 5. Log the struggle quietly
old_log = '''        event = {
            "event_id": event_id,
            "timestamp": now,
            "skill_id": problem.skill_id,'''

new_log = '''        # Quiet struggle signal for the teacher dashboard (does not
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
            "skill_id": problem.skill_id,'''

if old_log in src:
    src = src.replace(old_log, new_log, 1)
    print("quiet struggle signal added")

ENGINE.write_text(src, encoding="utf-8")
print("patch complete")
