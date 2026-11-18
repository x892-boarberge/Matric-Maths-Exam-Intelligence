import sys
sys.path.insert(0, '.')
from src.tutor.math_grader import grade

E = "p = -3"
cases = [
    ("no_trailing",  "2 ^ p = 1/8\n2^p = 2^-3\np = -3"),
    ("trailing_sp",  "2 ^ p = 1/8\n2^p = 2^-3\np = -3 "),
    ("trailing_nl",  "2 ^ p = 1/8\n2^p = 2^-3\np = -3\n"),
    ("double_nl",    "2 ^ p = 1/8\n2^p = 2^-3\np = -3\n\n"),
    ("with_answer_p", "2 ^ p = 1/8\n2^p = 2^-3\nanswer: p = -3"),
]
for name, text in cases:
    r = grade(text, E)
    print(f"{name:16} -> {r.kind.value:12} ({r.matcher})")
