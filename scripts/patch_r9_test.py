"""Update test_r9 to expect OFFER_WORKED_ANALOGUE."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "tests" / "test_tutor_engine.py"
src = TEST.read_text(encoding="utf-8")

old = '''def test_r9_escalation_to_human_after_repeated_failure():
    engine = TutorEngine()
    p = _problem("trig.reduction.simplify", "Simplify", "sin theta")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = None
    for _ in range(6):
        a = engine.step(s, p, "zzz")
        s = a.next_state
    assert a.action == ActionType.FLAG_FOR_HUMAN'''

new = '''def test_r9_offer_analogue_after_repeated_failure():
    """After 6 failed attempts, the tutor offers a worked analogue.
    It does not end the session and does not label the learner."""
    engine = TutorEngine()
    p = _problem("trig.reduction.simplify", "Simplify", "sin theta")
    s = LearnerState(learner_id="L", skill_id=p.skill_id)
    a = None
    for _ in range(6):
        a = engine.step(s, p, "zzz")
        s = a.next_state
    assert a.action == ActionType.OFFER_WORKED_ANALOGUE
    # The session must not be flagged for human and must not end
    assert a.action != ActionType.FLAG_FOR_HUMAN'''

if old in src:
    src = src.replace(old, new, 1)
    TEST.write_text(src, encoding="utf-8")
    print("test_r9 updated")
else:
    print("WARNING - old test_r9 body not found")
