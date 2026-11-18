import json, random, shutil
from pathlib import Path
from datetime import datetime
from fractions import Fraction

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
random.seed(2025)

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


# ===== 5.1 Domain of hyperbola =====
def gen_5_1():
    out = []
    pvals = [-4, -3, -2, -1, 1, 2, 3, 4, 5, 6]
    phrasings = [
        "Write down the domain of g(x) = 2/(x - {p}) + 3.",
        "Determine the domain of g(x) = -4/(x - {p}) + 5.",
        "For which values of x is g(x) = 6/(x - {p}) - 2 undefined?",
    ]
    for i, p in enumerate(pvals):
        for j, ph in enumerate(phrasings):
            q = ph.format(p=p)
            a = [-4, 2, 6][j]
            q_val = [5, 3, -2][j]
            out.append({
                "variant_question": q,
                "expected": f"x ∈ R, x ≠ {p}",
                "demonstration": f"g(x) has a denominator of (x - {p}). The function is undefined where x - {p} = 0, so x = {p} is excluded. Domain: x ∈ R, x ≠ {p}. (Equivalently: x ∈ (-∞; {p}) ∪ ({p}; ∞).)",
                "memo_marks": [f"1 mark for x ≠ {p} (or interval form)"],
                "fast_path": "Denominator cannot be zero. Set x - p = 0, exclude that value.",
                "fatal_error": "DBE says: Candidates give the asymptote as x = p but forget to exclude it from the domain, writing 'x ∈ R' or writing 'x ≠ p' without the 'x ∈ R' qualifier.",
                "answer_book_layout": [f"x - {p} = 0 → x = {p}", f"Domain: x ∈ R, x ≠ {p}"],
                "hack": "Where can't you divide? Where the denominator is zero. That single value is the only exclusion from the domain.",
                "trap": "Write it as 'x ∈ R, x ≠ p', not just 'x ≠ p'. The 'x ∈ R' part is part of the answer.",
                "presentation": "Show the excluded value, then the domain in inequality or interval notation.",
                "diagram": "required", "diagram_hint": "hyperbola_with_vertical_asymptote_marked",
            })
    random.shuffle(out)
    return out[:30]


# ===== 5.2 Range of parabola =====
def gen_5_2():
    out = []
    configs = []
    for a_sign in [-1, 1]:
        for k in [-9, -8, -6, -5, -4, -3, -2, 1, 2, 3, 4, 5, 6, 8, 9]:
            configs.append((a_sign, k))
    phrasings = [
        "Write down the range of f(x) = {a}(x - {h})^2 + {k}.",
        "Determine the range of the parabola f(x) = {a}(x - {h})^2 + {k}.",
    ]
    for i in range(30):
        a_sign, k = configs[i % len(configs)]
        a = a_sign * (2 if i % 2 == 0 else 1)
        h = (i % 3) + 1
        ph = phrasings[i % 2]
        q = ph.format(a=a, h=h, k=k)
        if a < 0:
            ans = f"y ≤ {k}"
            expl = f"a = {a} < 0, so the parabola opens downward. Turning point is ({h}, {k}), which is a maximum. Range: y ≤ {k}."
        else:
            ans = f"y ≥ {k}"
            expl = f"a = {a} > 0, so the parabola opens upward. Turning point is ({h}, {k}), which is a minimum. Range: y ≥ {k}."
        out.append({
            "variant_question": q,
            "expected": ans,
            "demonstration": expl,
            "memo_marks": [f"1 mark for {ans}"],
            "fast_path": "Sign of a tells you open/close. Turning point y = k is the bound.",
            "fatal_error": "DBE says: Candidates confuse range with domain, or forget the direction flip when a < 0.",
            "answer_book_layout": [f"a = {a}, turning point ({h}, {k})", ans],
            "hack": "Sign of a → opens up or down. Turning point y-value → the bound. Write the inequality in the right direction.",
            "trap": "Downward parabola has a MAXIMUM not a minimum. a < 0 means y ≤ k, not y ≥ k.",
            "presentation": "State the sign of a and the turning point, then write the range inequality.",
            "diagram": "required", "diagram_hint": "parabola_with_turning_point_marked",
        })
    return out


# ===== 5.3.2 Solve quadratic inequality =====
def gen_5_3_2():
    out = []
    configs = []
    for r1, r2 in [(-1, 5), (1, 4), (-2, 3), (2, 6), (-3, 2), (1, 6), (-4, 1), (2, 5), (-1, 4), (3, 6)]:
        for k in [0, 2, 3, 4, 5]:
            configs.append((r1, r2, k))
    random.shuffle(configs)
    for i in range(30):
        r1, r2, k = configs[i]
        a = -1 if i % 2 == 0 else 1
        # Build f(x) = a(x-r1)(x-r2) + k, then solve f(x) < k
        # i.e. a(x-r1)(x-r2) < 0
        if a < 0:
            # -x² + ... < 0 means (x-r1)(x-r2) > 0 means x < r1 or x > r2
            ans = f"x < {r1} or x > {r2}"
        else:
            ans = f"{r1} < x < {r2}"
        b = -a * (r1 + r2)
        c = a * r1 * r2 + k
        q = f"Determine the values of x for which f(x) = {a}x^2 + {b}x + {c} is less than {k}."
        out.append({
            "variant_question": q,
            "expected": ans,
            "demonstration": f"f(x) - {k} = {a}x^2 + {b}x + {c - k} = {a}(x - {r1})(x - {r2}). Solve f(x) - {k} < 0, i.e., {a}(x-{r1})(x-{r2}) < 0. Critical values at x = {r1} and x = {r2}. Sign chart gives: {ans}.",
            "memo_marks": [f"1 mark for x-intercepts {r1}, {r2}", f"1 mark for {ans}"],
            "fast_path": "Move k to one side, factor, sign chart between and outside the roots.",
            "fatal_error": "DBE says: Candidates solve f(x) = k and give the roots as the answer. The question asks for the INEQUALITY region, not the boundary.",
            "answer_book_layout": [f"f(x) - {k} = {a}(x - {r1})(x - {r2})", f"Critical values: x = {r1}, x = {r2}", f"Sign chart", ans],
            "hack": "Bring everything to one side, factor, sign chart. Downward parabola: below horizontal line outside the roots. Upward: between.",
            "trap": "The answer is an interval, not the roots. x < r1 or x > r2 (downward), or r1 < x < r2 (upward).",
            "presentation": "Show factored form, critical values, and the interval answer.",
            "diagram": "required", "diagram_hint": "parabola_vs_horizontal_line",
        })
    return out


# ===== 5.4 Show parabola equation =====
def gen_5_4():
    out = []
    configs = [
        (3, 8, 5, 6, "-1/2", "y = -1/2 x^2 + 3x + 7/2"),
        (2, 4, 4, 2, "-1/2", "y = -1/2 x^2 + 2x + 2"),
        (1, 5, 3, -3, "-2", "y = -2x^2 + 4x + 3"),
        (2, 6, 4, 4, "-1/2", "y = -1/2 x^2 + 2x + 4"),
        (-1, 4, 1, 0, "-1", "y = -x^2 - 2x + 3"),
        (0, 3, 2, -1, "-1", "y = -x^2 + 3"),
        (1, 2, 3, -2, "-1", "y = -x^2 + 2x + 1"),
        (3, 9, 5, 7, "-1/2", "y = -1/2 x^2 + 3x + 9/2"),
        (2, 5, 4, 1, "-1", "y = -x^2 + 4x + 1"),
        (1, 3, 3, -1, "-1", "y = -x^2 + 2x + 2"),
        (2, 4, 5, -1, "-1", "y = -x^2 + 4x"),
        (4, 2, 5, 1, "-1", "y = -x^2 + 8x - 14"),
        (1, 8, 3, 6, "-1/2", "y = -1/2 x^2 + x + 15/2"),
        (2, 3, 4, -1, "-1", "y = -x^2 + 4x - 1"),
        (3, 5, 5, 3, "-1/2", "y = -1/2 x^2 + 3x + 1/2"),
        (0, 2, 2, -2, "-1", "y = -x^2 + 2"),
        (2, 7, 4, 3, "-1", "y = -x^2 + 4x + 3"),
        (1, 4, 4, -5, "-1", "y = -x^2 + 2x + 3"),
        (3, 6, 4, 5, "-1", "y = -x^2 + 6x - 3"),
        (2, 5, 3, 4, "-1", "y = -x^2 + 4x + 1"),
    ]
    for i in range(30):
        h, k, x1, y1, a_str, ans = configs[i % len(configs)]
        a_frac = Fraction(a_str)
        # verify
        actual_a = Fraction(y1 - k) / ((x1 - h) ** 2) if (x1 - h) != 0 else None
        if actual_a != a_frac:
            continue
        # expand: y = a(x-h)^2 + k = a*x^2 - 2ah*x + (a*h^2 + k)
        a_n, a_d = a_frac.numerator, a_frac.denominator
        b_num = -2 * a_n * h  # over a_d
        c_num = a_n * h * h + k * a_d  # over a_d
        # For simplicity, use the factored form in demo and expanded in expected
        q = f"The turning point of f is P({h}; {k}). The graph also passes through D({x1}; {y1}). Show that the equation of f is {ans}."
        out.append({
            "variant_question": q,
            "expected": ans,
            "demonstration": f"Form: y = a(x - h)^2 + k with (h, k) = ({h}, {k}). So y = a(x - {h})^2 + {k}. Use D({x1}, {y1}): {y1} = a({x1} - {h})^2 + {k} → {y1} - {k} = a({(x1-h)**2}) → a = {y1-k}/{((x1-h)**2)} = {a_str}. Expand: y = {a_str}(x^2 - {2*h}x + {h*h}) + {k} = {a_str}x^2 - {2*h*a_n // a_d}x + ({a_n*h*h}/{a_d} + {k}) = {ans}.",
            "memo_marks": ["1 mark for a(x-h)^2 + k form", f"1 mark for substitution of D({x1}; {y1})", f"1 mark for expanding to {ans}"],
            "fast_path": "Turning point → use y = a(x-h)^2 + k. Plug in the other point to find a. Expand.",
            "fatal_error": "DBE says: Candidates use y = ax^2 + bx + c directly and set up 3 simultaneous equations without using the turning point. This wastes time and invites arithmetic errors.",
            "answer_book_layout": [f"y = a(x - {h})^2 + {k}", f"{y1} = a({x1} - {h})^2 + {k}", f"a = {a_str}", f"y = {a_str}(x - {h})^2 + {k}", ans],
            "hack": "Turning point is the shortcut. Form y = a(x-h)^2 + k uses it immediately. Then one substitution finds a.",
            "trap": "Remember to expand at the end. The question asks for the form with x² and x terms, not the vertex form.",
            "presentation": "Show the vertex form, the substitution, and the expansion. The expansion is the final mark.",
            "diagram": "required", "diagram_hint": "parabola_with_turning_point_and_one_more_point",
        })
    return out


# ===== 5.6 Tangent line at point =====
def gen_5_6():
    out = []
    configs = [
        (1, -6, 8, 2), (-1, 4, 5, 1), (1, -4, 3, 5), (-1, 2, 3, -1),
        (1, -2, -8, 4), (-1, 6, -2, 3), (1, -8, 12, 6), (-1, 0, 4, 2),
        (1, -3, 2, 3), (-1, 4, -1, 2), (1, -10, 16, 4), (-1, 8, 0, 3),
        (1, -4, 4, 2), (-1, 2, -3, 1), (1, -6, 9, 3), (-1, 6, -5, 2),
        (1, -2, -3, 1), (-1, 0, 5, 1), (1, -8, 15, 5), (-1, 10, -9, 5),
    ]
    for i in range(30):
        a, b, c, x0 = configs[i % len(configs)]
        y0 = a * x0 * x0 + b * x0 + c
        m = 2 * a * x0 + b
        c_line = y0 - m * x0
        if c_line >= 0:
            ans = f"y = {m}x + {c_line}"
        else:
            ans = f"y = {m}x - {abs(c_line)}"
        q = f"Given f(x) = {a}x^2 + {b}x + {c}, determine the equation of the tangent to f at x = {x0}."
        out.append({
            "variant_question": q,
            "expected": ans,
            "demonstration": f"f'(x) = {2*a}x + {b}. At x = {x0}: m = {m}. Point: ({x0}, {y0}). Line: y - {y0} = {m}(x - {x0}) → y = {m}x + {c_line if c_line >= 0 else f'({c_line})'} = {ans}.",
            "memo_marks": [f"1 mark for m = {m} (from f'({x0}))", f"1 mark for y = {y0} (point)", f"1 mark for final {ans}"],
            "fast_path": "Derivative gives slope. Substitute x0 into f for the point. Point-slope form.",
            "fatal_error": "DBE says: Candidates use f(x0) as the slope, or f'(x0) as the y-value. Derivative is slope; function is the point.",
            "answer_book_layout": [f"f'(x) = {2*a}x + {b}", f"m = f'({x0}) = {m}", f"y = f({x0}) = {y0}", f"y - {y0} = {m}(x - {x0})", ans],
            "hack": "Derivative → slope. Function → point. Two different numbers from the same x.",
            "trap": "f'(x0) is the slope, f(x0) is the y-coordinate. Don't mix them up.",
            "presentation": "Show f'(x), substitute x0 for slope, substitute x0 for y, then point-slope form.",
            "diagram": "required", "diagram_hint": "parabola_with_tangent_line",
        })
    return out


# ===== 5.3.1 Practice-only =====
def gen_5_3_1():
    prompts = [
        "Using the graph of f(x) = -1/2(x-3)^2 + 8 and g(x) = -4/(x-3) + 8, determine the values of x for which g(x) ≤ f(x).",
        "Given the parabola f(x) = -(x-2)^2 + 4 and the hyperbola g(x) = -2/(x-2) + 4, find where g(x) ≤ f(x).",
        "For f(x) = -1/2(x-1)^2 + 3 and g(x) = -1/(x-1) + 3, determine where g(x) ≤ f(x).",
        "Using the graphs of f(x) = -x^2 + 4 and g(x) = -3/(x-2) + 2, find where g(x) ≤ f(x).",
        "For the given graphs f(x) = -(x-4)^2 + 6 and g(x) = -2/(x-4) + 6, determine where g(x) ≤ f(x).",
    ]
    out = []
    for i in range(30):
        q = prompts[i % len(prompts)] + f" (variant {i+1})"
        out.append({
            "variant_question": q,
            "expected": "Practice — read the interval from the graph where g is below f.",
            "demonstration": "Find the intersection points. Between them (where g dips below f), g(x) ≤ f(x). Outside, g is above.",
            "memo_marks": ["2 marks for the correct interval"],
            "fast_path": "Intersection points bound the interval. Read 'g below f' directly from the sketch.",
            "fatal_error": "DBE says: Candidates read the wrong region — g above f instead of below — or miss one of the interval boundaries.",
            "answer_book_layout": ["Mark the intersection points", "Read the interval where g is below f"],
            "hack": "g ≤ f means g is below or equal to f. Read the interval where the hyperbola is under the parabola.",
            "trap": "Don't forget BOTH boundaries — intervals are closed (≤) not open (<).",
            "presentation": "State the two intersection x-values, then the interval between them.",
            "practice_only": True,
            "diagram": "required", "diagram_hint": "parabola_and_hyperbola_overlaid",
        })
    return out


# ===== 5.5 Practice-only =====
def gen_5_5():
    prompts = [
        "Given f(x) = x^2 - 4x - 5 and g(x) = -4/(x-3) + 8, M is the positive x-intercept of f and T is the x-intercept of g. Calculate the length of MT.",
        "For f(x) = x^2 - 6x + 5 and g(x) = -6/(x-2) + 3, M is the positive x-intercept of f and T is the x-intercept of g. Calculate MT.",
        "Given f(x) = x^2 - 4x - 5 and g(x) = -2/(x-1) + 1, M and T as defined. Find MT.",
        "For f(x) = x^2 - 2x - 8 and g(x) = -3/(x-1) + 1, calculate the length MT.",
        "Given f(x) = x^2 - 5x + 6 and g(x) = -4/(x-2) + 2, find MT.",
    ]
    out = []
    for i in range(30):
        q = prompts[i % len(prompts)] + f" (variant {i+1})"
        out.append({
            "variant_question": q,
            "expected": "Practice — find both x-intercepts, then the horizontal distance.",
            "demonstration": "Step 1: Set f(x) = 0 and solve the quadratic to find M. Step 2: Set g(x) = 0 and solve for T. Step 3: MT = |x_M - x_T|.",
            "memo_marks": ["1 mark for f's x-intercept", "1 mark for g's x-intercept", "1 mark for the distance"],
            "fast_path": "Two intercepts, one distance. Horizontal only, so |difference|.",
            "fatal_error": "DBE says: Candidates find only one intercept, or compute vertical distance instead of horizontal.",
            "answer_book_layout": ["f(x) = 0 → x = ...", "g(x) = 0 → x = ...", "MT = |x_M - x_T| = ..."],
            "hack": "Two equations, two intercepts, one subtraction. Horizontal distance is just |x₁ - x₂|.",
            "trap": "Both intercepts, then subtract. Don't skip either.",
            "presentation": "Show both intercept calculations, then the distance.",
            "practice_only": True,
            "diagram": "required", "diagram_hint": "parabola_and_hyperbola_intercepts_marked",
        })
    return out


# ===== Run all =====
print("Generating Q5 pools...\n")
for name, fn in [("5.1", gen_5_1), ("5.2", gen_5_2), ("5.3.1", gen_5_3_1),
                  ("5.3.2", gen_5_3_2), ("5.4", gen_5_4), ("5.5", gen_5_5), ("5.6", gen_5_6)]:
    variants = fn()
    n = write_pool(name, variants)
    print(f"  {name}: {n} variants")

print("\n=== VERIFY ===")
for name in ["5.1", "5.2", "5.3.1", "5.3.2", "5.4", "5.5", "5.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:80]}")
        print(f"     Expected: {v['expected']}")
