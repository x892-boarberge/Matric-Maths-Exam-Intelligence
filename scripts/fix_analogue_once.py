"""Fix analogue repetition and add near-miss detection."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"

# ---------- Fix 1: analogue fires once ----------
src = ENGINE.read_text(encoding="utf-8")

old = '''            if analogue_library.has_analogue(problem.skill_id):
                action_type = ActionType.OFFER_WORKED_ANALOGUE
                engine_rule = "ENG_OFFER_ANALOGUE"
            else:
                # No analogue exists for this skill; keep the session open
                # with a gentle step-down hint instead.
                action_type = ActionType.GIVE_HINT
                hint_level = HintLevel.H2
                engine_rule = "ENG_STEP_DOWN_NO_ANALOGUE"'''

new = '''            # Has this analogue already been shown in this session?
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
                engine_rule = "ENG_STEP_DOWN_NO_ANALOGUE"'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("Analogue now fires once per session")
else:
    print("WARNING - analogue block not found")

# ---------- Fix 2: near-miss detection in the matcher ----------
m = MATCHER.read_text(encoding="utf-8")

if "def near_miss" not in m:
    near_fn = '''


def near_miss(response, expected, max_edits=2):
    """
    Return True if the response is close to the expected answer, but not
    close enough for the matcher to accept it. Used to ask the learner
    "did you mean ...?" instead of saying wrong.
    """
    def edit_distance(a, b):
        if a == b:
            return 0
        if len(a) < len(b):
            a, b = b, a
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr = [i + 1]
            for j, cb in enumerate(b):
                curr.append(min(prev[j + 1] + 1, curr[j] + 1,
                                prev[j] + (ca != cb)))
            prev = curr
        return prev[-1]

    if not isinstance(response, str) or not isinstance(expected, str):
        return False
    r = _strip_all_spaces(_light_normalise(response))
    e = _strip_all_spaces(_light_normalise(expected))
    if not r or not e:
        return False
    return edit_distance(r, e) <= max_edits

'''
    m = m.rstrip() + near_fn
    MATCHER.write_text(m, encoding="utf-8")
    print("near_miss added to answer_matcher")
else:
    print("near_miss already present")

print()
print("Fixes applied")
