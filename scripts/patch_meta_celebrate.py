"""Add celebration and meta_comment pools to the meta library."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "src" / "tutor" / "meta_library.py"
src = META.read_text(encoding="utf-8")

if "say_celebration" in src:
    print("Celebration pool already present")
else:
    block = '''


# ---------- Celebration ----------

_CELEBRATION = [
    "You got it. Ready for the next one?",
    "There it is. Take the win. What is next?",
    "Good. You solved it. Want another?",
    "Right, that is done. Ready to keep going?",
    "That is it. One down. Where do you want to go next?",
]


def say_celebration(learner_id=None, context=None):
    return pick(_CELEBRATION, learner_id, "celebration")


# ---------- Meta-comment about the tutor ----------

_META_COMMENT = [
    "I am a tutor program, and I am here for this problem. What is your first step?",
    "Fair question. I am software, not a person. Back to the maths — what do you see?",
    "I am a tutor. That part does not matter. What is the question asking you to find?",
    "Still here. Let us keep going on the problem. What do you have so far?",
    "I am a program, and I am paying attention. What is your next move?",
]


def say_meta_comment(learner_id=None, context=None):
    return pick(_META_COMMENT, learner_id, "meta_comment")
'''
    src = src.rstrip() + block

    # Extend the dispatch helper
    old_dispatch = '''    if kind_value == "other_language":
        return say_other_language_repeat(learner_id) if repeat else say_other_language(learner_id)
    return ""'''
    new_dispatch = '''    if kind_value == "other_language":
        return say_other_language_repeat(learner_id) if repeat else say_other_language(learner_id)
    if kind_value == "celebration":
        return say_celebration(learner_id)
    if kind_value == "meta_comment":
        return say_meta_comment(learner_id)
    return ""'''
    if old_dispatch in src:
        src = src.replace(old_dispatch, new_dispatch, 1)
        print("Dispatch extended for celebration and meta_comment")
    else:
        print("WARNING - dispatch block not found")

    META.write_text(src, encoding="utf-8")
    print("Celebration and meta_comment pools added")
