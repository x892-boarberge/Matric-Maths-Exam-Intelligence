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

CASES = [
    # ================= Q1 (already proven) =================
    ("Q1.1.1 / 01 perfect", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4 or x=3"], 3, [], "", False),
    ("Q1.1.1 / 02 answer only", "2023_P1_Q1.1.1", ["x=-4 or x=3"], 1, [1, 2], "", False),
    ("Q1.1.1 / 03 factor only", "2023_P1_Q1.1.1", ["(x+4)(x-3)=0"], 1, [2, 3], "", False),
    ("Q1.1.1 / 04 skip step 2", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x=-4 or x=3"], 2, [2], "", False),
    ("Q1.1.1 / 05 memo order", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3 or x=-4"], 3, [], "", False),
    ("Q1.1.1 / 06 semicolon", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=3; x=-4"], 3, [], "", False),
    ("Q1.1.1 / 07 comma", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4, x=3"], 3, [], "", False),
    ("Q1.1.1 / 08 Therefore", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "Therefore x=-4 or x=3"], 3, [], "", False),
    ("Q1.1.1 / 09 wrong factor", "2023_P1_Q1.1.1",
     ["(x-4)(x+3)=0", "x=-4 or x=3"], 1, [1, 2], "", False),
    ("Q1.1.1 / 10 out of order", "2023_P1_Q1.1.1",
     ["x=-4 or x=3", "(x+4)(x-3)=0", "x+4=0 or x-3=0"], 3, [], "", False),
    ("Q1.1.1 / 11 alt factor order", "2023_P1_Q1.1.1",
     ["(x-3)(x+4)=0", "x-3=0 or x+4=0", "x=-4 or x=3"], 3, [], "", False),
    ("Q1.1.1 / 12 therefore symbol", "2023_P1_Q1.1.1",
     ["\u2234 (x+4)(x-3)=0", "x=-4 or x=3"], 2, [2], "", False),
    ("Q1.1.1 / 13 comma-or mix", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x=-4, or x=3"], 2, [2], "", False),
    ("Q1.1.1 / 14 one root", "2023_P1_Q1.1.1", ["x=-4"], 0, [1, 2, 3], "", False),
    ("Q1.1.1 / 15 wrong root", "2023_P1_Q1.1.1", ["x=-4 or x=5"], 0, [1, 2, 3], "", False),
    ("Q1.1.1 / 16 mixed", "2023_P1_Q1.1.1", ["x = -4 or 3"], 0, [1, 2, 3], "", False),
    ("Q1.1.1 / 17 whitespace", "2023_P1_Q1.1.1",
     ["  (x+4)(x-3)  =  0  ", "x = -4  or  x = 3"], 2, [2], "", False),
    ("Q1.1.1 / 18 (x+4)=0", "2023_P1_Q1.1.1",
     ["(x+4)=0 or (x-3)=0", "(x+4)(x-3)=0", "x=-4 or x=3"], 2, [2], "", False),
    ("Q1.1.1 / 19 So lead-in", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "So x+4=0 or x-3=0", "x=-4 or x=3"], 3, [], "", False),
    ("Q1.1.1 / 20 formula alt", "2023_P1_Q1.1.1",
     ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
     1, [], "steps 1-2 UNCERTAIN", False),

    ("Q1.1.2 / 01 perfect", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1.79", "x=-1.12"], 4, [], "", False),
    ("Q1.1.2 / 02 one line", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1.79 or x=-1.12"], 4, [], "", False),
    ("Q1.1.2 / 03 std form only", "2023_P1_Q1.1.2", ["3x^2-2x-6=0"], 1, [2, 3, 4], "", False),
    ("Q1.1.2 / 04 std + formula", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6"], 2, [3, 4], "", False),
    ("Q1.1.2 / 05 answers only", "2023_P1_Q1.1.2",
     ["x=1.79 or x=-1.12"], 2, [1, 2], "", False),
    ("Q1.1.2 / 06 one root", "2023_P1_Q1.1.2", ["x=1.79"], 1, [1, 2, 4], "", False),
    ("Q1.1.2 / 07 wrong rounding", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1.8 or x=-1.1"], 2, [3, 4], "", False),
    ("Q1.1.2 / 08 comma decimal", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1,79 or x=-1,12"], 4, [], "", False),

    ("Q1.1.3 / 01 perfect", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=0 or x=4", "x=4"], 4, [], "", False),
    ("Q1.1.3 / 02 compact", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x(x-4)=0", "x=0 or x=4", "x=4 only"], 4, [], "", False),
    ("Q1.1.3 / 03 no rejection", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=0 or x=4"], 3, [4], "", False),
    ("Q1.1.3 / 04 answer only", "2023_P1_Q1.1.3", ["x=4"], 1, [1, 2, 3], "", False),
    ("Q1.1.3 / 05 wrong root", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=0 or x=4", "x=0"], 3, [4], "", False),
    ("Q1.1.3 / 06 squaring only", "2023_P1_Q1.1.3", ["2x+1=(x-1)^2"], 1, [2, 3, 4], "", False),
    ("Q1.1.3 / 07 std form only", "2023_P1_Q1.1.3", ["x^2-4x=0"], 1, [1, 3, 4], "", False),
    ("Q1.1.3 / 08 reversed", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=4 or x=0", "x=4"], 4, [], "", False),

    ("Q1.1.4 / 01 perfect", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "(x-3)(x+1)>0", "x<-1 or x>3"], 4, [], "", False),
    ("Q1.1.4 / 02 answer only", "2023_P1_Q1.1.4", ["x<-1 or x>3"], 2, [1, 2], "", False),
    ("Q1.1.4 / 03 skip CVs", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "x<-1 or x>3"], 3, [2], "", False),
    ("Q1.1.4 / 04 wrong interval", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "(x-3)(x+1)>0", "-1<x<3"], 2, [3], "", False),
    ("Q1.1.4 / 05 reversed answer", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "(x-3)(x+1)>0", "x>3 or x<-1"], 4, [], "", False),

    ("Q1.2 / 01 method A", "2023_P1_Q1.2",
     ["x=2y-2", "1/(2y-2)+1/y=1", "2y^2-5y+2=0", "y=1/2 or y=2", "x=-1 or x=2"],
     5, [], "", False),
    ("Q1.2 / 02 method B", "2023_P1_Q1.2",
     ["y=x/2+1", "1/x+2/(x+2)=1", "x^2-x-2=0", "x=-1 or x=2", "y=1/2 or y=2"],
     5, [], "", False),
    ("Q1.2 / 03 no x-values", "2023_P1_Q1.2",
     ["x=2y-2", "1/(2y-2)+1/y=1", "2y^2-5y+2=0", "y=1/2 or y=2"],
     4, [5], "", False),
    ("Q1.2 / 04 answers only", "2023_P1_Q1.2",
     ["x=-1 or x=2", "y=1/2 or y=2"], 2, [1, 2, 3], "", False),
    ("Q1.2 / 05 std form only", "2023_P1_Q1.2", ["2y^2-5y+2=0"], 1, [1, 2, 4, 5], "", False),

    ("Q1.3 / 01 perfect", "2023_P1_Q1.3",
     ["2^m(2+1)=3^n(3^2-1)", "2^m(3)=3^n(2^3)", "m=3 and n=1", "m+n=4"],
     4, [], "", False),
    ("Q1.3 / 02 skip factor", "2023_P1_Q1.3",
     ["2^m(3)=3^n(8)", "m=3 and n=1", "m+n=4"], 3, [1], "", False),
    ("Q1.3 / 03 answer only", "2023_P1_Q1.3",
     ["m=3 and n=1", "m+n=4"], 2, [1, 2], "", False),
    ("Q1.3 / 04 skip conclusion", "2023_P1_Q1.3",
     ["2^m(2+1)=3^n(3^2-1)", "2^m(3)=3^n(2^3)", "m+n=4"], 3, [3], "", False),
    ("Q1.3 / 05 final only", "2023_P1_Q1.3", ["m+n=4"], 1, [1, 2, 3], "", False),

    # ================= Q2 (sequences) =================
    ("Q2.1.1 / 01 perfect", "2023_P1_Q2.1.1",
     ["d=5", "T91=7+(91-1)(5)", "T91=457"], 3, [], "", False),
    ("Q2.1.1 / 02 no d", "2023_P1_Q2.1.1",
     ["T91=7+(91-1)(5)", "T91=457"], 2, [1], "", False),
    ("Q2.1.1 / 03 answer only", "2023_P1_Q2.1.1", ["T91=457"], 1, [1, 2], "", False),
    ("Q2.1.1 / 04 Tn variant", "2023_P1_Q2.1.1",
     ["d=5", "Tn=7+(n-1)(5)", "T91=457"], 3, [], "", False),

    ("Q2.1.2 / 01 perfect", "2023_P1_Q2.1.2",
     ["S91=91/2[2(7)+(91-1)(5)]", "S91=21112"], 2, [], "", False),
    ("Q2.1.2 / 02 answer only", "2023_P1_Q2.1.2", ["S91=21112"], 1, [1], "", False),

    ("Q2.1.3 / 01 perfect", "2023_P1_Q2.1.3",
     ["Tn=7+(n-1)(5)", "Tn=517", "n=103"], 3, [], "", False),
    ("Q2.1.3 / 02 answer only", "2023_P1_Q2.1.3", ["n=103"], 1, [1, 2], "", False),

    ("Q2.2.1 / 01 perfect", "2023_P1_Q2.2.1",
     ["9; 21; 33; 45", "T5=111"], 2, [], "", False),
    ("Q2.2.1 / 02 answer only", "2023_P1_Q2.2.1", ["T5=111"], 1, [1], "", False),

    ("Q2.2.2 / 01 perfect", "2023_P1_Q2.2.2",
     ["2a=12", "3(6)+b=9", "Tn=6n^2-9n+6"], 3, [], "", False),
    ("Q2.2.2 / 02 wrong a", "2023_P1_Q2.2.2", ["2a=14"], 0, [1, 2, 3], "", False),

    ("Q2.2.3 / 01 perfect", "2023_P1_Q2.2.3",
     ["12n-9=0", "n=3/4", "T is increasing for n in N"], 3, [], "", False),
    ("Q2.2.3 / 02 answer only", "2023_P1_Q2.2.3",
     ["T is increasing for n in N"], 1, [1, 2], "", False),

    # ================= Q3 (geometric) =================
    ("Q3.1.1 / 01 perfect", "2023_P1_Q3.1.1", ["Tn=3(2)^(n-1)"], 1, [], "", False),

    ("Q3.1.2 / 01 perfect", "2023_P1_Q3.1.2",
     ["3+6+12+...", "n=k", "3(2^k-1)=98301", "k=15"], 4, [], "", False),
    ("Q3.1.2 / 02 no expansion", "2023_P1_Q3.1.2",
     ["n=k", "3(2^k-1)=98301", "k=15"], 3, [1], "", False),
    ("Q3.1.2 / 03 answer only", "2023_P1_Q3.1.2", ["k=15"], 1, [1, 2, 3], "", False),

    ("Q3.2 / 01 perfect", "2023_P1_Q3.2",
     ["S22=22/2[2a+21(3)]", "S22=22a+693", "S_inf=3a/2", "22a+693=3a/2+734", "a=2"],
     5, [], "", False),
    ("Q3.2 / 02 answer only", "2023_P1_Q3.2", ["a=2"], 1, [1, 2, 3, 4], "", False),
    ("Q3.2 / 03 no final answer", "2023_P1_Q3.2",
     ["S22=22/2[2a+21(3)]", "S22=22a+693", "S_inf=3a/2", "22a+693=3a/2+734"],
     4, [5], "", False),
]


def run() -> int:
    passed = failed = 0
    out = []
    for name, qid, working, exp_awarded, exp_missing, note, _xfail in CASES:
        try:
            r = grade_steps(qid, working, CSV)
            awarded = r["awarded_marks"]
            missing = sorted(s["index"] for s in r["steps"] if s["match_status"] == "NOT_MATCHED")
            ok = (awarded == exp_awarded) and (missing == sorted(exp_missing))
        except Exception as e:
            awarded = missing = None
            ok = False
            note = "EXCEPTION: " + str(e) + " | " + note

        if ok:
            passed += 1
            status = "PASS "
        else:
            failed += 1
            status = "FAIL "

        out.append("  [" + status + "] " + name)
        if note:
            out.append("           note: " + note)
        if not ok:
            out.append("           expected " + str(exp_awarded) + " missing=" + str(sorted(exp_missing)))
            out.append("           got      " + str(awarded) + " missing=" + str(missing))

    r20 = grade_steps("2023_P1_Q1.1.1",
                      ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"],
                      CSV)
    statuses = [s["match_status"] for s in r20["steps"]]
    if statuses == ["UNCERTAIN", "UNCERTAIN", "MATCHED"]:
        passed += 1
        out.append("  [PASS ] assertion / Q1.1.1 UNCERTAIN -> " + str(statuses))
    else:
        failed += 1
        out.append("  [FAIL ] assertion / Q1.1.1 UNCERTAIN")

    print("\n".join(out))
    print()
    print("  " + str(passed) + " passed  |  " + str(failed) + " failed  |  "
          + str(len(CASES) + 1) + " total")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
