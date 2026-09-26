"""
MatricMath — full program health check.

Tests:
  1. Router — every anchor routes to a template
  2. Template map — every skill has a template
  3. Analogue pool — every template has variants
  4. Grader — 31 notation cases across 10 topics
  5. Answer matcher — multi-root, order-independence
  6. Misconception library — 81 entries, loadable
  7. N08 loader — reads intervention spec
  8. End-to-end — anchor -> template -> drill problem construction
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PASS = "  OK  "
FAIL = "  XX  "
WARN = "  ~   "

results = []   # (category, status, label)


def report(category, status, label):
    results.append((category, status, label))
    print(f"{status} [{category:26s}] {label}")


print("=" * 72)
print("  MatricMath — full health check")
print("=" * 72)
print()

# ============================================================
# 1. Router
# ============================================================
print("--- 1. Template router ---")
from src.tutor.template_router import route_template

ROUTER_CASES = [
    ("algebra.quadratic.solve", "Solve x^2+x-12=0", "quadratic_standard_factorable"),
    ("algebra.quadratic.solve", "Solve for x: (x+5)(x-2)=0", "quadratic_factored"),
    ("algebra.quadratic.solve", "Solve 2x^2-4x+1=0", "quadratic_formula"),
    ("algebra.quadratic.solve", "Solve 5x^2+2=-9x (TWO decimals)", "quadratic_formula"),
    ("sequences.gp.term", "Calculate T25", None),
    ("functions.parabola.range", "State the range", None),
    ("calculus.derivative.first_principles", "First principles", None),
    ("probability.union", "P(A or B)", None),
    ("stats.median", "Find the median", None),
    ("analytical_geom.distance", "Distance AB", None),
    ("trig.reduction.simplify", "Simplify sin(180-x)", None),
    ("euclidean.semicircle.prove", "Prove ACB = 90", None),
]

for skill, prompt, expected in ROUTER_CASES:
    t = route_template(skill, prompt)
    if expected is None:
        ok = t is not None
    else:
        ok = t == expected
    report("router", PASS if ok else FAIL, f"{skill[:35]:37s} {prompt[:30]:32s} -> {t}")

print()

# ============================================================
# 2. Template map
# ============================================================
print("--- 2. Template map coverage ---")
from src.tutor.analogue_library import SKILL_TO_TEMPLATE, POOL

missing = [s for s in SKILL_TO_TEMPLATE if not SKILL_TO_TEMPLATE[s]]
if not missing:
    report("map", PASS, f"all {len(SKILL_TO_TEMPLATE)} skills mapped")
else:
    report("map", FAIL, f"{len(missing)} skills missing templates")

# Check every template in map has a pool
empty_pools = [t for t in set(SKILL_TO_TEMPLATE.values()) if not POOL.get(t)]
if not empty_pools:
    report("map", PASS, f"all {len(set(SKILL_TO_TEMPLATE.values()))} templates have pools")
else:
    report("map", WARN, f"empty pools: {empty_pools[:5]}")

print()

# ============================================================
# 3. Analogue pool
# ============================================================
print("--- 3. Analogue pool ---")
total_variants = sum(len(v) for v in POOL.values())
report("pool", PASS if total_variants >= 3000 else WARN,
       f"total variants: {total_variants} across {len(POOL)} templates")

# Sample a few pools
for tid in ["quadratic_factored", "quadratic_standard_factorable", "quadratic_formula"]:
    n = len(POOL.get(tid, []))
    st = PASS if n >= 50 else FAIL
    report("pool", st, f"{tid:35s} {n} variants")

print()

# ============================================================
# 4. Grader (all topics)
# ============================================================
print("--- 4. Grader across 10 topics ---")
from src.tutor.math_grader import grade, MatchKind

GRADER_CASES = [
    # (learner, expected, should_match)
    ("x = -6 or x = 1",            "x = -6 or x = 1",           True),
    ("x = 1, -6",                  "x = -6 or x = 1",           True),
    ("-6, 1",                      "x = -6 or x = 1",           True),
    ("x = 0.75 or x = -0.5",       "x = 3/4 or x = -1/2",       True),
    ("T_n = 5n + 2",               "T_n = 5n + 2",              True),
    ("Tn = 2 + 5n",                "T_n = 5n + 2",              True),
    ("S_20 = 1090",                "S_20 = 1090",               True),
    ("y = 2(x-1)^2 + 3",           "y = 2(x-1)^2 + 3",          True),
    ("x in R, x != 3",             "x in R, x != 3",            True),
    ("x in R, x not equal to 3",   "x in R, x != 3",            True),
    ("A = R58 230.94",             "A = R58 230.94",            True),
    ("R58230.94",                  "A = R58 230.94",            True),
    ("A = 58230.94",               "A = R58 230.94",            True),
    ("f'(x) = -2",                 "f'(x) = -2",                True),
    ("dy/dx = 4x - 2x^(-3)",       "dy/dx = 4x - 2x^(-3)",      True),
    ("12/35",                      "12/35",                     True),
    ("0.34",                       "12/35",                     True),
    ("P(A or B) = 5/6",            "5/6",                       True),
    ("mean = 12.4",                "mean = 12.4",               True),
    ("12,4",                       "mean = 12.4",               True),
    ("S(15; 16)",                  "S(15; 16)",                 True),
    ("S(15, 16)",                  "S(15; 16)",                 True),
    ("-sin x",                     "-sin x",                    True),
    ("sin 4x",                     "sin 4x",                    True),
    ("x = 30 + 360k",              "x = 30 + k*360",            True),
    ("angle ACB = 90",             "angle ACB = 90",            True),
    # Negatives — must NOT match
    ("x = 6 or x = -1",            "x = -6 or x = 1",           False),
    ("x = -6",                     "x = -6 or x = 1",           False),
]

grader_match = 0
grader_total = 0
for learner, expected, should in GRADER_CASES:
    r = grade(learner, expected)
    grader_total += 1
    if should and r.kind == MatchKind.MATCH:
        grader_match += 1
        report("grader", PASS, f"{learner[:35]:38s} -> {r.matcher}")
    elif not should and r.kind in (MatchKind.NO_MATCH, MatchKind.UNCERTAIN):
        grader_match += 1
        report("grader", PASS, f"{learner[:35]:38s} -> correctly {r.kind.value}")
    else:
        report("grader", FAIL, f"{learner[:35]:38s} -> {r.kind.value} (want {'MATCH' if should else 'NOT MATCH'})")

print(f"\n  Grader: {grader_match}/{grader_total}")
print()

# ============================================================
# 5. Answer matcher (backward-compat)
# ============================================================
print("--- 5. Answer matcher (legacy) ---")
from src.tutor.answer_matcher import compare, Match

MATCHER_CASES = [
    ("x = -4 or 3",     "x = -4 or x = 3",   Match.MATCH),
    ("x = -4 or x = 3", "x = -4 or 3",       Match.MATCH),
    ("x = 3",           "x = -4 or x = 3",   Match.NO_MATCH),
    ("x = -4 or -3",    "x = -4 or x = 3",   Match.NO_MATCH),
]

for learner, expected, want in MATCHER_CASES:
    got = compare(learner, expected)
    ok = got == want
    report("matcher", PASS if ok else FAIL, f"{learner[:25]:27s} -> {got.value}")

print()

# ============================================================
# 6. Misconception library
# ============================================================
print("--- 6. Misconception library ---")
try:
    import pandas as pd
    mis = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "processed" / "tutor" / "misconceptions_v2.csv")
    n = len(mis)
    report("n08", PASS if n >= 60 else WARN, f"{n} misconceptions loaded")
    # Coverage by topic
    topics = mis["topic"].value_counts().to_dict()
    report("n08", PASS, f"topics: {sorted(topics.keys())}")
except Exception as e:
    report("n08", FAIL, f"could not load misconceptions_v2.csv: {e}")

print()

# ============================================================
# 7. N08 loader
# ============================================================
print("--- 7. N08 intervention loader ---")
try:
    from src.tutor.n08_loader import get_library
    lib = get_library(force_reload=True)
    report("loader", PASS if lib.load_status == "csv" else FAIL,
           f"status: {lib.load_status}, {len(lib.by_misconception)} misconceptions")
except Exception as e:
    report("loader", FAIL, f"{e}")

print()

# ============================================================
# 8. Diagnosis two-layer
# ============================================================
print("--- 8. Diagnosis (two-layer) ---")
try:
    from src.tutor.diagnosis import diagnose, reachable_misconception_ids
    ids = reachable_misconception_ids()
    report("diagnosis", PASS if len(ids) >= 70 else WARN, f"{len(ids)} reachable misconception IDs")
    r = diagnose("algebra.quadratic.solve", "x = 5 or x = 2", "x = -5 or x = 2")
    report("diagnosis", PASS if r.misconception_id == "M_SIGN_ERROR_FACTORISATION" else FAIL,
           f"sign flip fired: {r.misconception_id}")
except Exception as e:
    report("diagnosis", FAIL, f"{e}")

print()

# ============================================================
# 9. End-to-end drill construction
# ============================================================
print("--- 9. End-to-end drill construction ---")
try:
    from src.tutor.drill import _load_pool, _analogue_to_problem
    from src.tutor.schemas import Problem
    anchor = Problem(
        problem_id="2025_P1_Q1_1.1.1",
        skill_id="algebra.quadratic.solve",
        topic="Algebra & Equations",
        subtopic="Quadratic equations",
        structure_type="routine_calculation",
        prompt="Solve x^2+x-12=0",
        expected_answer="x = -3 or x = 4",
        topic_v2="ALG",
    )
    tid = route_template(anchor.skill_id, anchor.prompt)
    pool = _load_pool(tid)
    report("e2e", PASS if len(pool) >= 50 else FAIL, f"anchor routed to {tid}, {len(pool)} variants")

    # Verify variations are same type
    sample_variants = [a["problem"] for a in pool[:5]]
    all_standard_form = all("x^2" in p and "(" not in p.split("=")[0].strip() for p in sample_variants)
    report("e2e", PASS if all_standard_form else FAIL,
           f"variations all standard-form: {all_standard_form}")

    # Verify drill problem construction
    dp = _analogue_to_problem(pool[0], tid, anchor.skill_id)
    ok = dp.prompt and dp.expected_answer
    report("e2e", PASS if ok else FAIL, f"drill problem: {dp.prompt[:60]}")
    report("e2e", PASS, f"expected: {dp.expected_answer[:60]}")

except Exception as e:
    report("e2e", FAIL, f"{e}")

print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 72)
print("  SUMMARY")
print("=" * 72)

from collections import Counter
counts = Counter(status for _, status, _ in results)
total = len(results)
ok = counts[PASS]
warn = counts[WARN]
fail = counts[FAIL]

print(f"  Total checks:  {total}")
print(f"  PASS:          {ok}")
print(f"  WARN:          {warn}")
print(f"  FAIL:          {fail}")
print()

if fail == 0:
    print("  ✅ All checks passed.")
elif fail <= 3:
    print(f"  ⚠️  {fail} failures — review above.")
else:
    print(f"  ❌ {fail} failures — needs attention.")

# Per-category breakdown
print()
print("  Per-category:")
cats = Counter(c for c, _, _ in results)
for cat, n in cats.most_common():
    cat_pass = sum(1 for c, s, _ in results if c == cat and s == PASS)
    cat_fail = sum(1 for c, s, _ in results if c == cat and s == FAIL)
    print(f"    {cat:26s} {cat_pass}/{n} pass, {cat_fail} fail")

print("=" * 72)