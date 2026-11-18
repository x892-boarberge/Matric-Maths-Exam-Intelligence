"""Algebra diagnosis battery — 30 cases across 8 algebra skills.

Run:
    from tutor.diagnosis_battery_algebra import run
    run()
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tutor import diagnosis as diag


CASES = [
    ("algebra.quadratic.solve",
     "x = 2 and x = 3", "x = 2 or x = 3",
     "Solve x^2 - 5x + 6 = 0", "M_AND_OR_CONFUSION"),
    ("algebra.quadratic.solve",
     "x = (b + sqrt(b^2 + 4ac)) / 2a", "x = 2 or x = 3",
     "Solve x^2 - 5x + 6 = 0", "M_WRONG_QUADRATIC_FORMULA"),
    ("algebra.quadratic.solve",
     "x = (6 + sqrt(36 - 4ac)) / 2a", "x = 4 or x = -9",
     "Solve x^2 + 5x - 36 = 0", "M_INCORRECT_SUBSTITUTION"),
    ("algebra.quadratic.solve",
     "x = 5", "x = 0 or x = 5",
     "Solve x^2 - 5x = 0", "M_LOST_ROOT_BY_DIVISION"),
    ("algebra.quadratic.solve",
     "x = 5 or x = -2", "x = -5 or x = 2",
     "(x + 5)(x - 2) = 0", "M_SIGN_ERROR_READING_ROOT"),
    ("algebra.quadratic.solve",
     "x = -5 or x = 2", "x = 5 or x = -2",
     "Solve x^2 - 3x - 10 = 0", "M_SIGN_ERROR_FACTORISATION"),
    ("algebra.quadratic.solve",
     "x = 2", "x = 2 or x = 3",
     "Solve x^2 - 5x + 6 = 0", "M_INCOMPLETE_ROOTS"),
    ("algebra.quadratic.solve",
     "(x - 2)(x - 3) = 0", "x = 2 or x = 3",
     "Solve x^2 - 5x + 6 = 0", "M_FACTORISATION_INCOMPLETE"),
    ("algebra.quadratic.solve",
     "x = 2 or x = 3", "x = 2 or x = 3",
     "Solve x^2 - 5x + 6 = 0", None),

    ("algebra.quadratic.inequality",
     "x = 2", "x < 2 or x > 3",
     "Solve x^2 - 5x + 6 > 0", "M_INEQ_TREATED_AS_EQUATION"),
    ("algebra.quadratic.inequality",
     "2 < x and x < 3", "x < 2 or x > 3",
     "Solve x^2 - 5x + 6 > 0", "M_AND_OR_CONFUSION"),
    ("algebra.quadratic.inequality",
     "2 < x < 3", "x < 2 or x > 3",
     "Solve x^2 - 5x + 6 > 0", "M_INEQ_WRONG_INTERVAL"),
    ("algebra.quadratic.inequality",
     "x < 2 or x > 3", "x < 2 or x > 3",
     "Solve x^2 - 5x + 6 > 0", None),

    ("algebra.exponential.solve",
     "x = 2 or x = 3", "x = 2",
     "Solve 2^x = 4", "M_EXP_EXTRA_ROOT_NOT_REJECTED"),
    ("algebra.exponential.solve",
     "2^x - 2^x = 0", "x = 0",
     "Solve 2^x * 2^x = 4", "M_EXP_LAW_MISAPPLIED"),
    ("algebra.exponential.solve",
     "(2^x - 2) = 0", "x = 1",
     "Solve 2^(2x) - 3*2^x + 2 = 0", "M_EXP_FACTORISATION_ERROR"),
    ("algebra.exponential.solve",
     "x = 2", "x = 2",
     "Solve 2^x = 4", None),

    ("algebra.simultaneous.solve",
     "y = (x + 2)^2", "y = x^2 + 4x + 4",
     "Solve y = x + 2 and y = x^2 + 3x + 5", "M_SIM_OVERLOOKED_FACTOR"),
    ("algebra.simultaneous.solve",
     "3 + 4 = 7", "x = 1 or x = 2",
     "Solve y = 2x + 1 and y = x^2 + 1", "M_SIM_EQUATION_FROM_WORDS"),

    ("algebra.surd.solve",
     "1/sqrt(5)", "sqrt(5)/5",
     "Simplify", "M_FRACTIONAL_SURD_NOT_HANDLED"),
    ("algebra.surd.solve",
     "x^2 + 9 = 0", "x = 3 or x = -3",
     "Solve (x + 3)^2 = 0", "M_BINOMIAL_MIDDLE_TERM_DROPPED"),
    ("algebra.surd.solve",
     "sqrt(x + 1) = sqrt(x - 3) + 2", "x = 3",
     "Solve sqrt(x + 1) - sqrt(x - 3) = 2", "M_SURD_NOT_ISOLATED"),
    ("algebra.surd.solve",
     "(x + 2)^2 = 9", "x = 1 or x = -5",
     "Solve sqrt(x + 2) = 3", "M_RHS_SQUARED_INCORRECTLY"),
    ("algebra.surd.solve",
     "x = 3 or x = -1", "x = 3",
     "Solve sqrt(x + 1) = 2", "M_EXTRANEOUS_ROOT_NOT_REJECTED"),
    ("algebra.surd.solve",
     "x = 3", "x = 3",
     "Solve sqrt(x + 1) = 2", None),

    ("algebra.proof",
     "the discriminant is 4, so...", "non-real",
     "Prove the roots of x^2 + x + 1 = 0 are non-real",
     "M_PROOF_NONREAL_EXPLANATION"),
    ("algebra.proof.integer",
     "Let n be an integer. Consider 2n + 1.", "proved",
     "Prove that the sum of two odd numbers is even",
     "M_PROOF_INTEGER_PATTERN"),

    ("algebra.exponential.proof",
     "n < 11.18", "n = 11",
     "Find the largest n such that 2^n < 2500",
     "M_EXP_PROOF_NO_CONCLUSION"),
    ("algebra.exponential.proof",
     "2^n * 3^n + 5^n", "10^n + 5^n",
     "Factorise 2^n * 3^n + 5^n",
     "M_EXP_PROOF_NO_FACTORISE"),
    ("algebra.exponential.proof",
     "n < 11.18, so n = 11", "n = 11",
     "Find the largest n such that 2^n < 2500", None),
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
    fails = []
    if verbose:
        print(f"{'skill':<32} {'want':<40} {'got':<40} ok")
        print("-" * 120)
    for skill, learner, expected, prompt, want in CASES:
        got, ok = _check(skill, learner, expected, prompt, want)
        if ok:
            passed += 1
        else:
            fails.append((skill, want, got, learner, expected, prompt))
        if verbose:
            want_s = want or "(none)"
            got_s = got or "(none)"
            print(f"{skill:<32} {want_s[:38]:<40} {got_s[:38]:<40} {'OK' if ok else 'FAIL'}")
    if verbose:
        print()
        print(f"SUMMARY: {passed} pass, {len(CASES) - passed} fail")
    return passed, len(CASES), fails
