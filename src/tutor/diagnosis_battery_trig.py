"""Trig diagnosis battery — 17 cases across 8 trig skills.

Run:
    from tutor.diagnosis_battery_trig import run
    run()

Add cases above the SUMMARY line when new trig rules are added.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tutor import diagnosis as diag


CASES = [
    # (skill, learner, expected, prompt, want_misc)
    ("trig.reduction",             "sin x",                       "-sin x",                          "",                                          "M_REDUCTION_SIGN"),
    ("trig.reduction",             "cos x",                       "sin x",                           "",                                          "M_REDUCTION_COFUNCTION"),
    ("trig.reduction",             "sin x",                       "sin x",                           "",                                          None),
    ("trig.double_angle",          "sin 2x = 2 sin x",            "sin 2x = 2 sin x cos x",          "",                                          "M_DOUBLE_ANGLE_LINEAR"),
    ("trig.equation",              "x = 30 + 360k",               "x = 30",                          "Solve for x in the interval 0 to 360.",     "M_TRIG_EQ_GENERAL_WHEN_INTERVAL"),
    ("trig.equation",              "x = 30 or x = 150",           "x = 30 or x = 150",               "",                                          None),
    ("trig.equation",              "x = 30",                      "x = 30 or x = 150",               "",                                          "M_TRIG_EQ_MISSING_SOLUTION"),
    ("trig.equation.general",      "x = 30",                      "x = 30 + 360k",                   "",                                          "M_TRIG_GENERAL_INCOMPLETE"),
    ("trig.equation.general",      "x = 30 + 360k",               "x = 30 + 360k",                   "",                                          None),
    ("trig.graph.period",          "domain is [0, 360]",          "180",                             "",                                          "M_PERIOD_DOMAIN_CONFUSION"),
    ("trig.graph.period",          "period = 180",                "180",                             "",                                          None),
    ("trig.graph.period",          "period = 180",                "90",                              "",                                          "M_PERIOD_COEFFICIENT"),
    ("trig.graph.value",           "y = 2",                       "x = 2",                           "",                                          "M_GRAPH_VALUE_LABEL_SWAPPED"),
    ("trig.compound.sin",          "cos a cos b + sin a sin b",   "sin a cos b + cos a sin b",       "",                                          "M_COMPOUND_WRONG_FORM"),
    ("trig.maximum",               "x = 45",                      "max = 1",                         "",                                          "M_MAX_ANGLE_NOT_RATIO"),
    ("trig.unitcircle",            "1/2",                         "-1/2",                            "",                                          "M_UNIT_QUADRANT_SIGN"),
    ("trig.3d.length",             "used tan for the ratio",      "sin rule applied",                "",                                          "M_3D_WRONG_RATIO"),
]


def _check(skill, learner, expected, prompt, want):
    for rule in diag.RULES.get(skill, []):
        misc_id = rule[0]
        pred = rule[3] if len(rule) >= 4 else None
        if not callable(pred):
            continue
        try:
            try:
                hit = pred(learner, expected, prompt)
            except TypeError:
                hit = pred(learner, expected)
        except Exception:
            hit = False
        if hit:
            return misc_id, (misc_id == want)
    return None, (want is None)


def run(verbose=True):
    passed = 0
    if verbose:
        print(f"{'skill':<26} {'want':<34} {'got':<34} ok")
        print("-" * 100)
    for skill, learner, expected, prompt, want in CASES:
        got, ok = _check(skill, learner, expected, prompt, want)
        if ok:
            passed += 1
        if verbose:
            want_s = want or "(none)"
            got_s = got or "(none)"
            print(f"{skill:<26} {want_s:<34} {got_s:<34} {'OK' if ok else 'FAIL'}")
    if verbose:
        print()
        print(f"SUMMARY: {passed} pass, {len(CASES) - passed} fail")
    return passed, len(CASES)
