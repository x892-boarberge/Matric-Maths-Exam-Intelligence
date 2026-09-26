import sys
sys.path.insert(0, ".")
from src.tutor.math_grader import grade, MatchKind

CASES = [
    ("x = -6 or x = 1",            "x = -6 or x = 1"),
    ("x = 1, -6",                  "x = -6 or x = 1"),
    ("x = 0.75 or x = -0.5",       "x = 3/4 or x = -1/2"),
    ("x = 2 + sqrt3 or x = 2 - sqrt3", "x = 2 + sqrt3 or x = 2 - sqrt3"),
    ("x < -1 or x > 3",            "x < -1 or x > 3"),
    ("T_n = 5n + 2",               "T_n = 5n + 2"),
    ("Tn = 2 + 5n",                "T_n = 5n + 2"),
    ("S_20 = 1090",                "S_20 = 1090"),
    ("y = 2(x-1)^2 + 3",           "y = 2(x-1)^2 + 3"),
    ("x in R, x != 3",             "x in R, x != 3"),
    ("x in R, x not equal to 3",   "x in R, x != 3"),
    ("A = R58 230.94",             "A = R58 230.94"),
    ("R58230.94",                  "A = R58 230.94"),
    ("A = 58230.94",               "A = R58 230.94"),
    ("f'(x) = -2",                 "f'(x) = -2"),
    ("dy/dx = 4x - 2x^(-3)",       "dy/dx = 4x - 2x^(-3)"),
    ("12/35",                      "12/35"),
    ("0.34",                       "12/35"),
    ("P(A or B) = 5/6",            "5/6"),
    ("mean = 12.4",                "mean = 12.4"),
    ("12,4",                       "mean = 12.4"),
    ("S(15; 16)",                  "S(15; 16)"),
    ("S(15, 16)",                  "S(15; 16)"),
    ("-sin x",                     "-sin x"),
    ("sin 4x",                     "sin 4x"),
    ("x = 30 + k*360",             "x = 30 + k*360"),
    ("x = 30 + 360k",              "x = 30 + k*360"),
    ("PT is a diameter",           "PT is a diameter"),
    ("angle ACB = 90",             "angle ACB = 90"),
    ("x = 6 or x = -1",            "x = -6 or x = 1"),
    ("x = -6",                     "x = -6 or x = 1"),
]

ok = unc = bad = 0
for learner, expected in CASES:
    r = grade(learner, expected)
    if r.kind == MatchKind.MATCH:
        ok += 1
        flag = " OK "
    elif r.kind == MatchKind.UNCERTAIN:
        unc += 1
        flag = " ?  "
    else:
        bad += 1
        flag = " XX "
    print(f"{flag} [{r.matcher:22s}] {r.kind.value:9s} conf={r.confidence:.2f} | {learner[:35]:38s} vs {expected[:35]}")

print()
print(f"MATCH: {ok}   UNCERTAIN: {unc}   NO_MATCH: {bad}")
print(f"Total: {len(CASES)}")