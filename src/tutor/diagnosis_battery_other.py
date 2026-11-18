"""Combined battery — functions, euclidean, analytical_geom,
calculus, sequences, statistics. 16 cases.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tutor import diagnosis as diag


CASES = [
    # ═══════════ analytical_geom.parallelogram.prove ═══════════
    ("analytical_geom.parallelogram.prove",
     "as seen in the diagram, ABCD is a parallelogram",
     "AB || DC and AD || BC",
     "Prove ABCD is a parallelogram",
     "M_DIAGRAM_ASSUMPTION"),
    ("analytical_geom.parallelogram.prove",
     "AB || DC, so ABCD is a parallelogram",
     "AB || DC",
     "Prove ABCD is a parallelogram",
     None),

    # ═══════════ calculus.chain_rule ═══════════
    ("calculus.chain_rule",
     "3*(x+2)^5",                # dropped the inner derivative factor of 4
     "12*(x+2)^5",
     "Differentiate (x+2)^6",
     "M_CHAIN_RULE_DROP"),
    ("calculus.chain_rule",
     "6*(x+2)^5",                # full chain rule applied
     "6*(x+2)^5",
     "Differentiate (x+2)^6",
     None),

    # ═══════════ euclidean.semicircle.prove ═══════════
    ("euclidean.semicircle.prove",
     "angle = 90",
     "90 (angle in semicircle)",
     "Prove the angle in a semicircle is 90",
     "M_MISSING_THEOREM_CITATION"),
    ("euclidean.semicircle.prove",
     "angle in semicircle theorem gives 90",
     "90",
     "Prove the angle in a semicircle is 90",
     None),

    # ═══════════ euclidean.similarity.ratio ═══════════
    ("euclidean.similarity.ratio",
     "3:4",                     # expected 4:3 — reciprocal
     "4:3",
     "Find the similarity ratio",
     "M_SIMILARITY_RATIO"),
    ("euclidean.similarity.ratio",
     "4:3",                     # correct
     "4:3",
     "Find the similarity ratio",
     None),

    # ═══════════ functions.hyperbola.asymptotes ═══════════
    ("functions.hyperbola.asymptotes",
     "horizontal asymptote: x = 2",     # swapped axes
     "horizontal asymptote: y = 2",
     "State the asymptotes of y = a/(x-3) + 2",
     "M_ASYMPTOTE_CONFUSION"),
    ("functions.hyperbola.asymptotes",
     "horizontal asymptote: y = 2, vertical: x = 3",
     "horizontal: y = 2",
     "State the asymptotes",
     None),

    # ═══════════ functions.parabola.range ═══════════
    ("functions.parabola.range",
     "y >= -1",                  # the exact confusable value this predicate guards
     "y <= 2",
     "State the range of the parabola",
     "M_TP_COORD_CONFUSION"),

    # ═══════════ sequences.gp.term ═══════════
    ("sequences.gp.term",
     "2 * 3^n",                  # expected 2 * 3^(n-1) — off by one
     "2 * 3^(n-1)",
     "Find the nth term of 2, 6, 18, ...",
     "M_GP_COMMON_RATIO"),
    ("sequences.gp.term",
     "2 * 3^(n-1)",              # correct
     "2 * 3^(n-1)",
     "Find the nth term",
     None),

    # ═══════════ statistics.boxplot.iqr ═══════════
    ("statistics.boxplot.iqr",
     "28",                       # range (max-min), not IQR
     "{12,15,20,25,40} IQR = 10",
     "Find the IQR of the boxplot",
     "M_BOXPLOT_IQR"),
    ("statistics.boxplot.iqr",
     "10",                       # correct IQR
     "{12,15,20,25,40} IQR = 10",
     "Find the IQR",
     None),
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
        print(f"{'skill':<42} {'want':<30} {'got':<30} ok")
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
            print(f"{skill:<42} {want_s[:28]:<30} {got_s[:28]:<30} {'OK' if ok else 'FAIL'}")
    if verbose:
        print()
        print(f"SUMMARY: {passed} pass, {len(CASES) - passed} fail")
        if fails:
            print()
            print("── failures ──")
            for skill, want, got, learner, expected, prompt in fails:
                print(f"  [{skill}] want={want} got={got}")
                print(f"    learner={learner!r} expected={expected!r} prompt={prompt!r}")
    return passed, len(CASES), fails
