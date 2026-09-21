"""Add a dispatch helper to meta_library.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "src" / "tutor" / "meta_library.py"
src = META.read_text(encoding="utf-8")

if "def respond_to_disengagement" in src:
    print("Dispatch helper already present")
else:
    helper = '''


def respond_to_disengagement(kind_value, learner_id=None, attempts=None):
    """
    Dispatch a disengagement kind to the right meta-library function.

    kind_value: string value of DisengagementKind
                ("answer_demand", "frustrated", "help_seeking", "none")
    learner_id: for deterministic variant selection
    attempts:   number of prior same-kind events in this session

    Returns an empty string if the kind is not recognised.
    """
    repeat = attempts is not None and attempts >= 1

    if kind_value == "answer_demand":
        return say_answer_demand_repeat(learner_id) if repeat else say_answer_demand(learner_id)
    if kind_value == "frustrated":
        return say_frustrated_repeat(learner_id) if repeat else say_frustrated(learner_id)
    if kind_value == "help_seeking":
        return say_not_understanding_after_struggle(learner_id) if repeat else say_not_understanding(learner_id)
    if kind_value == "silent" or kind_value == "none":
        return say_silence(learner_id)
    return ""
'''
    src = src.rstrip() + helper
    META.write_text(src, encoding="utf-8")
    print("Dispatch helper added")
