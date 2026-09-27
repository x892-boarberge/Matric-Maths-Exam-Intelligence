"""
Test harness for step_grader.py

Run:  python tests/test_step_grader.py
Exit code 0 if all cases pass, 1 otherwise.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.step_grader import grade_steps

CSV = ROOT / "data" / "processed" / "memo_step_marks" / "memo_step_marks_2023_P1.csv"

# (name, qid, learner_lines, exp_awarded, exp_missing, note, xfail)
CASES = [
    # ---- 2023 P1 Q1.1.1 (factorise) ----
    ("Q1.1.1 / 01 perfect working", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4 or x=3"],
     3, [], "", False),
    ("Q1.1.1 / 02 answer only", "2023_P1_Q1.1.1",
     ["x=-4 or x=3"],
     1, [1, 2], "", False),
    ("Q1.1.1 / 03 factor only", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0"],
     1, [2, 3], "", False),
    ("Q1.1.1 / 04 skip step 2", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("Q1.1.1 / 05 roots in memo order", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3 or x=-4"],
     3, [], "", False),
    ("Q1.1.1 / 06 semicolon roots", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3; x=-4"],
     3, [], "", False),
    ("Q1.1.1 / 07 comma roots", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4, x=3"],
     3, [], "", False),
    ("Q1.1.1 / 08 Therefore lead-in", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "Therefore x=-4 or x=3"],
     3, [], "", False),
    ("Q1.1.1 / 09 wrong factor sign", "2023_P1_Q1.1.1",
     ["(x-4)(x+3)=0", "x=-4 or x=3"],
     1, [1, 2], "", False),
    ("Q1.1.1 / 10 out-of-order roots first", "2023_P1_Q1.1.1",
     ["x=-4 or x=3", "(x+4)(x-3)=0", "x+4=0 or x-3=0"],
     3, [], "", False),
    ("Q1.1.1 / 11 alternate factor order", "2023_P1_Q1.1.1",
     ["(x-3)(x+4)=0", "x-3=0 or x+4=0", "x=-4 or x=3"],
     3, [], "", False),
    ("Q1.1.1 / 12 therefore symbol lead-in", "2023_P1_Q1.1.1",
     ["\u2234 (x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("Q1.1.1 / 13 comma-or mix", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x=-4, or x=3"],
     2, [2], "", False),
    ("Q1.1.1 / 14 one root only", "2023_P1_Q1.1.1",
     ["x=-4"],
     0, [1, 2, 3], "", False),
    ("Q1.1.1 / 15 one root wrong", "2023_P1_Q1.1.1",
     ["x=-4 or x=5"],
     0, [1, 2, 3], "", False),
    ("Q1.1.1 / 16 mixed notation", "2023_P1_Q1.1.1",
     ["x = -4 or 3"],
     0, [1, 2, 3], "", False),
    ("Q1.1.1 / 17 whitespace heavy", "2023_P1_Q1.1.1",
     ["  (x+4)(x-3)  =  0  ", "x = -4  or  x = 3"],
     2, [2], "", False),
    ("Q1.1.1 / 18 factor as (x+4)=0 form", "2023_P1_Q1.1.1",
     ["(x+4)=0 or (x-3)=0", "(x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("Q1.1.1 / 19 So lead-in on step 2", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "So x+4=0 or x-3=0", "x=-4 or x=3"],
     3, [], "", False),
    ("Q1.1.1 / 20 formula method (alternate)", "2023_P1_Q1.1.1",
     ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
     1, [],
     "steps 1-2 UNCERTAIN (alternate method)", False),

    # ---- 2023 P1 Q1.1.2 (formula) ----
    ("Q1.1.2 / 01 perfect separate roots", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2±√76)/6", "x=1.79", "x=-1.12"],
     4, [], "", False),
    ("Q1.1.2 / 02 perfect roots on one line", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2±√76)/6", "x=1.79 or x=-1.12"],
     4, [], "", False),
    ("Q1.1.2 / 03 standard form only", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0"],
     1, [2, 3, 4], "", False),
    ("Q1.1.2 / 04 standard form + formula", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2±√76)/6"],
     2, [3, 4], "", False),
    ("Q1.1.2 / 05 answers only both roots", "2023_P1_Q1.1.2",
     ["x=1.79 or x=-1.12"],
     2, [1, 2], "", False),
    ("Q1.1.2 / 06 answer only one root", "2023_P1_Q1.1.2",
     ["x=1.79"],
     1, [1, 2, 4], "", False),
    ("Q1.1.2 / 07 wrong rounding", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2±√76)/6", "x=1.8 or x=-1.1"],
     2, [3, 4], "", False),
    ("Q1.1.2 / 08 comma decimal notation", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2±√76)/6", "x=1,79 or x=-1,12"],
     4, [], "", False),
]


def run() -> int:
    passed = xfailed = failed = 0
    out = []

    for name, qid, working, exp_awarded, exp_missing, note, xfail in CASES:
        try:
            r = grade_steps(qid, working, CSV)
            awarded = r["awarded_marks"]
            missing = sorted(s["index"] for s in r["steps"] if s["match_status"] == "NOT_MATCHED")
            ok = (awarded == exp_awarded) and (missing == sorted(exp_missing))
        except Exception as e:
            awarded = missing = None
            ok = False
            note = "EXCEPTION: " + str(e) + " | " + note

        if ok and not xfail:
            passed += 1
            status = "PASS "
        elif (not ok) and xfail:
            xfailed += 1
            status = "XFAIL"
        else:
            failed += 1
            status = "FAIL "

        out.append("  [" + status + "] " + name)
        if note:
            out.append("           note: " + note)
        if not ok and not xfail:
            out.append("           expected " + str(exp_awarded) + " missing=" + str(sorted(exp_missing)))
            out.append("           got      " + str(awarded) + " missing=" + str(missing))

    # Assertion: Q1.1.1 case 20 -> UNCERTAIN, UNCERTAIN, MATCHED
    r20 = grade_steps("2023_P1_Q1.1.1",
                      ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
                      CSV)
    statuses = [s["match_status"] for s in r20["steps"]]
    if statuses == ["UNCERTAIN", "UNCERTAIN", "MATCHED"]:
        passed += 1
        out.append("  [PASS ] assertion / Q1.1.1 case 20 UNCERTAIN -> " + str(statuses))
    else:
        failed += 1
        out.append("  [FAIL ] assertion / Q1.1.1 case 20 UNCERTAIN")
        out.append("           expected ['UNCERTAIN', 'UNCERTAIN', 'MATCHED']")
        out.append("           got      " + str(statuses))

    print("\n".join(out))
    print()
    print("  " + str(passed) + " passed  |  " + str(xfailed) + " xfail  |  "
          + str(failed) + " failed  |  " + str(len(CASES) + 1) + " total")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
