"""
Test harness for step_grader.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.step_grader import grade_steps

CSV = ROOT / "data" / "processed" / "memo_step_marks" / "memo_step_marks_2023_P1.csv"
QID = "2023_P1_Q1.1.1"

CASES = [
    ("01 perfect working",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4 or x=3"],
     3, [], "", False),
    ("02 answer only",
     ["x=-4 or x=3"],
     1, [1, 2], "", False),
    ("03 factor only",
     ["(x+4)(x-3)=0"],
     1, [2, 3], "", False),
    ("04 skip step 2 (factor + roots)",
     ["(x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("05 roots in memo order",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3 or x=-4"],
     3, [], "", False),
    ("06 semicolon roots",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3; x=-4"],
     3, [], "", False),
    ("07 comma roots",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4, x=3"],
     3, [], "", False),
    ("08 'Therefore' lead-in",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "Therefore x=-4 or x=3"],
     3, [], "", False),
    ("09 wrong factor sign",
     ["(x-4)(x+3)=0", "x=-4 or x=3"],
     1, [1, 2], "", False),
    ("10 out-of-order (roots first)",
     ["x=-4 or x=3", "(x+4)(x-3)=0", "x+4=0 or x-3=0"],
     3, [], "", False),
    ("11 alternate factor order",
     ["(x-3)(x+4)=0", "x-3=0 or x+4=0", "x=-4 or x=3"],
     3, [], "", False),
    ("12 therefore symbol lead-in",
     ["\u2234 (x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("13 comma-or mix",
     ["(x+4)(x-3)=0", "x=-4, or x=3"],
     2, [2], "", False),
    ("14 one root only",
     ["x=-4"],
     0, [1, 2, 3], "", False),
    ("15 one root wrong",
     ["x=-4 or x=5"],
     0, [1, 2, 3], "", False),
    ("16 mixed notation (x = ... or 3)",
     ["x = -4 or 3"],
     0, [1, 2, 3], "", False),
    ("17 whitespace heavy",
     ["  (x+4)(x-3)  =  0  ", "x = -4  or  x = 3"],
     2, [2], "", False),
    ("18 factor as (x+4)=0 form",
     ["(x+4)=0 or (x-3)=0", "(x+4)(x-3)=0", "x=-4 or x=3"],
     2, [2], "", False),
    ("19 extra 'So' lead-in on step 2",
     ["(x+4)(x-3)=0", "So x+4=0 or x-3=0", "x=-4 or x=3"],
     3, [], "", False),
    ("20 formula method (alternate valid)",
     ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
     1, [],
     "steps 1-2 UNCERTAIN (alternate method), not missing",
     False),
]


def run() -> int:
    passed = xfailed = failed = 0
    out = []

    for name, working, exp_awarded, exp_missing, note, xfail in CASES:
        try:
            r = grade_steps(QID, working, CSV)
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
            out.append("           expected " + str(exp_awarded) + "/3 missing=" + str(sorted(exp_missing)))
            out.append("           got      " + str(awarded) + "/3 missing=" + str(missing))

    r20 = grade_steps(QID, ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"], CSV)
    statuses = [s["match_status"] for s in r20["steps"]]
    if statuses == ["UNCERTAIN", "UNCERTAIN", "MATCHED"]:
        passed += 1
        out.append("  [PASS ] 21 case-20 UNCERTAIN status -> " + str(statuses))
    else:
        failed += 1
        out.append("  [FAIL ] 21 case-20 UNCERTAIN status")
        out.append("           expected ['UNCERTAIN', 'UNCERTAIN', 'MATCHED']")
        out.append("           got      " + str(statuses))

    print("\n".join(out))
    print()
    print("  " + str(passed) + " passed  |  " + str(xfailed) + " xfail  |  "
          + str(failed) + " failed  |  " + str(len(CASES) + 1) + " total")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)