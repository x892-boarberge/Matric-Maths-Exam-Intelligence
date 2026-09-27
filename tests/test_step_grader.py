"""
Test harness for step_grader.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.step_grader import grade_steps

CASES = [
    # ============ 2023 P1 (regression) ============
    ("P1 Q1.1.1 perfect", "2023_P1_Q1.1.1",
     ["(x+4)(x-3)=0", "x+4=0 or x-3=0", "x=-4 or x=3"], 3, [], "", False),
    ("P1 Q1.1.2 perfect", "2023_P1_Q1.1.2",
     ["3x^2-2x-6=0", "x=(2\u00b1\u221a76)/6", "x=1.79", "x=-1.12"], 4, [], "", False),
    ("P1 Q1.1.3 perfect", "2023_P1_Q1.1.3",
     ["2x+1=(x-1)^2", "x^2-4x=0", "x=0 or x=4", "x=4"], 4, [], "", False),
    ("P1 Q1.1.4 perfect", "2023_P1_Q1.1.4",
     ["x^2-2x-3>0", "(x-3)(x+1)>0", "x<-1 or x>3"], 4, [], "", False),
    ("P1 Q1.2 method A", "2023_P1_Q1.2",
     ["x=2y-2", "1/(2y-2)+1/y=1", "2y^2-5y+2=0", "y=1/2 or y=2", "x=-1 or x=2"],
     5, [], "", False),
    ("P1 Q1.2 method B", "2023_P1_Q1.2",
     ["y=x/2+1", "1/x+2/(x+2)=1", "x^2-x-2=0", "x=-1 or x=2", "y=1/2 or y=2"],
     5, [], "", False),
    ("P1 Q1.3 perfect", "2023_P1_Q1.3",
     ["2^m(2+1)=3^n(3^2-1)", "2^m(3)=3^n(2^3)", "m=3 and n=1", "m+n=4"],
     4, [], "", False),
    ("P1 Q3.2 perfect", "2023_P1_Q3.2",
     ["S22=22/2[2a+21(3)]", "S22=22a+693", "S_inf=3a/2", "22a+693=3a/2+734", "a=2"],
     5, [], "", False),
    ("P1 Q5.6 method A", "2023_P1_Q5.6",
     ["-2x+k=8/x", "-2x^2+kx-8=0", "k^2-64<0", "-8<k<8"], 4, [], "", False),
    ("P1 Q6.2.2 perfect", "2023_P1_Q6.2.2",
     ["i=8.7/1200", "n=60", "20000=x[(1+8.7/1200)^60-1]/(8.7/1200)", "x=267.26"],
     4, [], "", False),
    ("P1 Q7.1 perfect", "2023_P1_Q7.1",
     ["f'(x)=lim(f(x+h)-f(x))/h", "f(x+h)=-4x^2-8xh-4h^2",
      "-8xh-4h^2", "h(-8x-4h)", "-8x"], 5, [], "", False),
    ("P1 Q8.4 perfect", "2023_P1_Q8.4",
     ["f''(x)=-6x+12", "f''(x)=0", "x=2", "y=2", "f'(2)=3", "g(x)=3x-4"],
     6, [], "", False),
    ("P1 Q9.2 perfect", "2023_P1_Q9.2",
     ["A(x)=3456x^-1+6x+480", "A'(x)=-3456/x^2+6", "x=24"], 3, [], "", False),
    ("P1 Q10.1.1 perfect", "2023_P1_Q10.1.1",
     ["P(A and B)=P(A)*P(B)", "P(A and B)=1/4"], 2, [], "", False),

    # ============ 2023 P2 Q1 (statistics regression) ============
    ("P2 Q1.1 / 01 perfect", "2023_P2_Q1.1",
     ["a=-23.85", "b=0.23", "y_hat=-23.85+0.23x"], 3, [], "", False),
    ("P2 Q1.1 / 02 answer only", "2023_P2_Q1.1",
     ["y_hat=-23.85+0.23x"], 1, [1, 2], "", False),
    ("P2 Q1.2 / 01 perfect", "2023_P2_Q1.2",
     ["y_hat=-23.85+0.23(550)", "y_hat=102.65"], 2, [], "", False),
    ("P2 Q1.2 / 02 answer only", "2023_P2_Q1.2", ["y_hat=102.65"], 1, [1], "", False),
    ("P2 Q1.3 / 01 perfect", "2023_P2_Q1.3", ["r=0.98"], 1, [], "", False),
    ("P2 Q1.4 / 01 perfect", "2023_P2_Q1.4", ["strong positive"], 1, [], "", False),
    ("P2 Q1.5.1 / 01 perfect", "2023_P2_Q1.5.1",
     ["x_bar=1200/8", "x_bar=150"], 2, [], "", False),
    ("P2 Q1.5.2 / 01 perfect", "2023_P2_Q1.5.2", ["sigma=50.50"], 1, [], "", False),
    ("P2 Q1.5.3 / 01 perfect", "2023_P2_Q1.5.3",
     ["x_bar-sigma=99.50", "1 stop"], 2, [], "", False),

    # ============ Q2 (frequency) ============
    ("P2 Q2.2 / 01 perfect", "2023_P2_Q2.2", ["40 staff"], 1, [], "", False),
    ("P2 Q2.3 / 01 perfect", "2023_P2_Q2.3", ["33 staff"], 1, [], "", False),
    ("P2 Q2.4 / 01 perfect", "2023_P2_Q2.4",
     ["x_bar=(1(5+k/2)+3(15)+5(13+k/2)+7(5)+9(2))/(40+k)",
      "3k+168=160+4k", "k=8"], 3, [], "", False),
    ("P2 Q2.4 / 02 answer only", "2023_P2_Q2.4", ["k=8"], 1, [1, 2], "", False),

    # ============ Q3 (analytical geometry) ============
    ("P2 Q3.1 / 01 perfect", "2023_P2_Q3.1",
     ["SL=sqrt((4-(-4))^2+(5-1)^2)", "SL=4sqrt(5)=8.94"], 2, [], "", False),
    ("P2 Q3.2 / 01 perfect", "2023_P2_Q3.2",
     ["m_SN=(5-(-3))/(4-(-2))", "m_SN=4/3"], 2, [], "", False),
    ("P2 Q3.3 / 01 perfect", "2023_P2_Q3.3",
     ["tan theta=m_SN", "theta=53.13"], 2, [], "", False),
    ("P2 Q3.4 / 01 perfect", "2023_P2_Q3.4",
     ["m_LN=-2", "LKO=116.57", "LNS=63.44"], 3, [], "", False),
    ("P2 Q3.5 / 01 perfect", "2023_P2_Q3.5", ["y=4/3x+19/3"], 1, [], "", False),
    ("P2 Q3.6 / 01 perfect", "2023_P2_Q3.6",
     ["LN=2sqrt(5)", "Area=1/2(4sqrt(5))(2sqrt(5))", "Area=20"], 3, [], "", False),
    ("P2 Q3.7 / 01 perfect", "2023_P2_Q3.7", ["L=90", "P(1;1)"], 2, [], "", False),
    ("P2 Q3.8 / 01 perfect", "2023_P2_Q3.8", ["LPN=53.13", "LPS=126.87"], 2, [], "", False),

    # ============ Q4 (analytical geometry 2) ============
    ("P2 Q4.1 / 01 perfect", "2023_P2_Q4.1",
     ["p^2+(-2)^2=20", "p=4"], 2, [], "", False),
    ("P2 Q4.2 / 01 perfect", "2023_P2_Q4.2", ["x_F=8", "F(8;6)"], 2, [], "", False),
    ("P2 Q4.3 / 01 perfect", "2023_P2_Q4.3",
     ["m_DE=2", "-2=2(4)+c", "y=2x-10"], 3, [], "", False),
    ("P2 Q4.4 / 01 perfect", "2023_P2_Q4.4",
     ["m_GF=-1/2", "(0-6)/(t-8)=-1/2", "t=20"], 3, [], "", False),
    ("P2 Q4.5 / 01 perfect", "2023_P2_Q4.5",
     ["(8-20)^2+(6-0)^2=r^2", "r^2=180", "(x-20)^2+y^2=180",
      "x^2+y^2-40x+220=0"], 4, [], "", False),
    ("P2 Q4.6 / 01 perfect", "2023_P2_Q4.6",
     ["k=20-4sqrt(5) or k=20+4sqrt(5)", "k=11.06", "k=28.94"], 3, [], "", False),

    # ============ Q5 (trig) ============
    ("P2 Q5.1.1 / 01 perfect", "2023_P2_Q5.1.1",
     ["x^2+y^2=r^2", "x=-2sqrt(2)", "cos beta=-2sqrt(2)/3"], 3, [], "", False),
    ("P2 Q5.1.2 / 01 perfect", "2023_P2_Q5.1.2",
     ["sin2beta=2sinb cosb", "2(1/3)(-sqrt(8)/3)", "sin2beta=-4sqrt(2)/9"],
     3, [], "", False),
    ("P2 Q5.2 / 01 perfect", "2023_P2_Q5.2",
     ["cos(450-beta)", "cos450cosb+sin450sinb", "sin beta=1/3"], 3, [], "", False),
    ("P2 Q5.2.2 / 01 perfect", "2023_P2_Q5.2.2",
     ["sin x+1=0", "x=270"], 2, [], "", False),
    ("P2 Q5.2.3 / 01 perfect", "2023_P2_Q5.2.3", ["min=0"], 1, [], "", False),
    ("P2 Q5.3.2 / 01 perfect", "2023_P2_Q5.3.2",
     ["sin(48-x)=cos2x", "sin(48-x)=sin(90-2x)", "x=42+k.360", "x=-14-k.120"],
     4, [], "", False),

    # ============ Q6 (trig graphs) ============
    ("P2 Q6.1 / 01 perfect", "2023_P2_Q6.1", ["period=180"], 1, [], "", False),
    ("P2 Q6.2 / 01 perfect", "2023_P2_Q6.2", ["y in [-sqrt(2)/2;1]"], 1, [], "", False),
    ("P2 Q6.3.1 / 01 perfect", "2023_P2_Q6.3.1", ["x in (45;90)"], 1, [], "", False),
    ("P2 Q6.3.2 / 01 perfect", "2023_P2_Q6.3.2", ["x in [105;165]"], 1, [], "", False),
    ("P2 Q6.4 / 01 perfect", "2023_P2_Q6.4",
     ["-2sin2x=-1", "k=15", "k=75"], 3, [], "", False),
    ("P2 Q6.5 / 01 perfect", "2023_P2_Q6.5",
     ["h(x)=-cos(x+90)", "h(x)=sin x"], 2, [], "", False),

    # ============ Q7 (3D trig) ============
    ("P2 Q7.1 / 01 perfect", "2023_P2_Q7.1",
     ["q=1/2 p(SK) sin alpha", "SK=2q/(p sin alpha)"], 2, [], "", False),
    ("P2 Q7.2 / 01 perfect", "2023_P2_Q7.2",
     ["RKS=beta", "RS/SK=tan beta", "RS=2q tan beta/(p sin alpha)"], 3, [], "", False),
    ("P2 Q7.3 / 01 perfect", "2023_P2_Q7.3",
     ["70=2(2500)tan42/(80 sin alpha)", "sin alpha=25/28 tan42", "alpha=53.51"],
     3, [], "", False),
]


def run() -> int:
    passed = failed = 0
    out = []
    for name, qid, working, exp_awarded, exp_missing, note, _xfail in CASES:
        try:
            r = grade_steps(qid, working)
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

    # UNCERTAIN assertion
    r20 = grade_steps("2023_P1_Q1.1.1",
                      ["x = (-1 +/- sqrt(49))/2", "x = (-1 +/- 7)/2", "x = 3 or x = -4"])
    statuses = [s["match_status"] for s in r20["steps"]]
    if statuses == ["UNCERTAIN", "UNCERTAIN", "MATCHED"]:
        passed += 1
        out.append("  [PASS ] assertion / UNCERTAIN")
    else:
        failed += 1
        out.append("  [FAIL ] assertion / UNCERTAIN")

    print("\n".join(out))
    print()
    print("  " + str(passed) + " passed  |  " + str(failed) + " failed  |  "
          + str(len(CASES) + 1) + " total")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
