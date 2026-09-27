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
    # ================= Q1 =================
    ("Q1.1.1 / 01 perfect", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4 or x=3"], 3, [], "", False),
    ("Q1.1.1 / 02 answer only", "2023_P1_Q1.1.1", ["x=-4 or x=3"], 1, [1, 2], "", False),
    ("Q1.1.2 / 01 perfect", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1.79", "x=-1.12"], 4, [], "", False),
    ("Q1.1.3 / 01 perfect", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=0 or x=4", "x=4"], 4, [], "", False),
    ("Q1.1.4 / 01 perfect", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "(x-3)(x+1)>0", "x<-1 or x>3"], 4, [], "", False),
    ("Q1.2 / 01 method A", "2023_P1_Q1.2",
     ["x=2y-2", "1/(2y-2)+1/y=1", "2y^2-5y+2=0", "y=1/2 or y=2", "x=-1 or x=2"],
     5, [], "", False),
    ("Q1.2 / 02 method B", "2023_P1_Q1.2",
     ["y=x/2+1", "1/x+2/(x+2)=1", "x^2-x-2=0", "x=-1 or x=2", "y=1/2 or y=2"],
     5, [], "", False),
    ("Q1.3 / 01 perfect", "2023_P1_Q1.3",
     ["2^m(2+1)=3^n(3^2-1)", "2^m(3)=3^n(2^3)", "m=3 and n=1", "m+n=4"],
     4, [], "", False),

    # ================= Q2 =================
    ("Q2.1.1 / 01 perfect", "2023_P1_Q2.1.1",
     ["d=5", "T91=7+(91-1)(5)", "T91=457"], 3, [], "", False),
    ("Q2.1.1 / 02 Tn variant", "2023_P1_Q2.1.1",
     ["d=5", "Tn=7+(n-1)(5)", "T91=457"], 3, [], "", False),
    ("Q2.1.2 / 01 perfect", "2023_P1_Q2.1.2",
     ["S91=91/2[2(7)+(91-1)(5)]", "S91=21112"], 2, [], "", False),
    ("Q2.1.3 / 01 perfect", "2023_P1_Q2.1.3",
     ["Tn=7+(n-1)(5)", "Tn=517", "n=103"], 3, [], "", False),
    ("Q2.2.1 / 01 perfect", "2023_P1_Q2.2.1",
     ["9; 21; 33; 45", "T5=111"], 2, [], "", False),
    ("Q2.2.2 / 01 perfect", "2023_P1_Q2.2.2",
     ["2a=12", "3(6)+b=9", "Tn=6n^2-9n+6"], 3, [], "", False),
    ("Q2.2.3 / 01 perfect", "2023_P1_Q2.2.3",
     ["12n-9=0", "n=3/4", "T is increasing for n in N"], 3, [], "", False),

    # ================= Q3 =================
    ("Q3.1.1 / 01 perfect", "2023_P1_Q3.1.1", ["Tn=3(2)^(n-1)"], 1, [], "", False),
    ("Q3.1.2 / 01 perfect", "2023_P1_Q3.1.2",
     ["3+6+12+...", "n=k", "3(2^k-1)=98301", "k=15"], 4, [], "", False),
    ("Q3.2 / 01 perfect", "2023_P1_Q3.2",
     ["S22=22/2[2a+21(3)]", "S22=22a+693", "S_inf=3a/2", "22a+693=3a/2+734", "a=2"],
     5, [], "", False),

    # ================= Q4 =================
    ("Q4.1 / 01 perfect", "2023_P1_Q4.1", ["y=-4"], 1, [], "", False),
    ("Q4.2 / 01 perfect", "2023_P1_Q4.2", ["0=2^x-4", "x=2"], 2, [], "", False),
    ("Q4.2 / 02 answer only", "2023_P1_Q4.2", ["x=2"], 1, [1], "", False),
    ("Q4.3 / 01 perfect", "2023_P1_Q4.3",
     ["y=2^0-4=-3", "m=3/2", "k(x)=3/2x-3"], 3, [], "", False),
    ("Q4.3 / 02 answer only", "2023_P1_Q4.3", ["k(x)=3/2x-3"], 1, [1, 2], "", False),
    ("Q4.4 / 01 perfect", "2023_P1_Q4.4",
     ["k(1)=-3/2", "f(1)=-2", "1/2"], 3, [], "", False),
    ("Q4.5 / 01 perfect", "2023_P1_Q4.5", ["g(x)=2^x"], 1, [], "", False),
    ("Q4.6 / 01 perfect", "2023_P1_Q4.6", ["x in [1/4;16]"], 1, [], "", False),
    ("Q4.7 / 01 perfect", "2023_P1_Q4.7",
     ["x=2^y", "g^-1(x)=log_2 x"], 2, [], "", False),

    # ================= Q5 =================
    ("Q5.1 / 01 perfect", "2023_P1_Q5.1", ["x=1", "y=8"], 2, [], "", False),
    ("Q5.2 / 01 perfect", "2023_P1_Q5.2",
     ["y=-1/2(0-1)^2+8", "C(0;15/2)"], 2, [], "", False),
    ("Q5.3 / 01 perfect", "2023_P1_Q5.3", ["8=d/1"], 1, [], "", False),
    ("Q5.4 / 01 perfect", "2023_P1_Q5.4", ["y != 0"], 1, [], "", False),
    ("Q5.5 / 01 perfect", "2023_P1_Q5.5",
     ["-3<=x<0", "x>=5", "-3<=x<0 or x>=5"], 3, [], "", False),
    ("Q5.6 / 01 method A", "2023_P1_Q5.6",
     ["-2x+k=8/x", "-2x^2+kx-8=0", "k^2-64<0", "-8<k<8"], 4, [], "", False),
    ("Q5.6 / 02 method B", "2023_P1_Q5.6",
     ["-8/x^2=-2", "x=2 or x=-2", "k=8", "-8<k<8"], 4, [], "", False),
    ("Q5.7 / 01 perfect", "2023_P1_Q5.7",
     ["-2x+8=8/x", "(x-2)^2=0", "f(2)=15/2; h(2)=4", "t=-7/2"], 4, [], "", False),
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
        out.append("  [PASS ] assertion / Q1.1.1 UNCERTAIN")
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
