"""Add hostile-input handling to the meta library."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "src" / "tutor" / "meta_library.py"
src = META.read_text(encoding="utf-8")

if "say_hostile_input" in src:
    print("Hostile handler already present")
else:
    block = '''


# ---------- Hostile input ----------

_HOSTILE = [
    "I am still here. Let us come back to the question. What is your first step?",
    "Okay. We do not have to like this problem. We do have to solve it. What do you see first?",
    "I hear you. Let us set the frustration down and look at the question. What is it asking for?",
    "No problem. I am not going anywhere. Show me what you have tried so far.",
    "Fine. Let us skip the talking and look at the numbers. What is in front of you?",
]

_HOSTILE_REPEAT = [
    "Still here. Let us focus on one small thing. What is the first line of your working?",
    "Okay. One question. What does the problem give you?",
    "That is fine. Let us start over. Read me the question slowly.",
]


def say_hostile_input(learner_id=None, context=None):
    return pick(_HOSTILE, learner_id, "hostile")


def say_hostile_input_repeat(learner_id=None, context=None):
    return pick(_HOSTILE_REPEAT, learner_id, "hostile_repeat")
'''
    src = src.rstrip() + block

    # Extend the dispatch helper
    old_dispatch = '''    if kind_value == "silent" or kind_value == "none":
        return say_silence(learner_id)
    return ""'''
    new_dispatch = '''    if kind_value == "silent" or kind_value == "none":
        return say_silence(learner_id)
    if kind_value == "hostile":
        return say_hostile_input_repeat(learner_id) if repeat else say_hostile_input(learner_id)
    return ""'''
    if old_dispatch in src:
        src = src.replace(old_dispatch, new_dispatch, 1)
        print("Dispatch helper extended")
    else:
        print("WARNING - dispatch helper block not found")

    META.write_text(src, encoding="utf-8")
    print("Hostile handler added")
