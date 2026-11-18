import sys
sys.path.insert(0, '.')
from src.tutor.math_grader import grade

learner = "2 ^ p = 1/8\n2^p = 2^-3\np = -3"
expected = "p = -3"
r = grade(learner, expected)
print("kind    =", r.kind.value)
print("matcher =", r.matcher)
detail = getattr(r, "detail", None)
print("detail  =", detail)
print("---")
print("learner text repr:", repr(learner))
print("expected repr:   ", repr(expected))
