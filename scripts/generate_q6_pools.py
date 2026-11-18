import json, random, shutil
from pathlib import Path
from datetime import datetime
from fractions import Fraction

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
random.seed(2026)

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


# ===== 6.1 — x-intercept of g in terms of p =====
def gen_6_1():
    out = []
    pvals = [1, 2, 3, 4, 5, 6, -1, -2, -3, -4]
    phrasings = [
        "The vertical asymptote of f(x) = a/(x + p) + q is x = -{p}. The line g(x) = x + c intersects the vertical asymptote of f on the x-axis. Write down the coordinates of the x-intercept of g.",
        "Given f(x) = a/(x + {p}) + q with vertical asymptote x = {neg_p}, and g(x) = x + c. The intersection of g with the vertical asymptote of f lies on the x-axis. Determine the x-intercept of g.",
        "The vertical asymptote of f(x) = a/(x + p) + q is x = -{p}. Graph g(x) = x + c and this asymptote meet at the x-axis. Write down the coordinates of g's x-intercept.",
    ]
    for i, p in enumerate(pvals):
        for ph in phrasings[:3]:
            neg_p = -p
            q = ph.format(p=p, neg_p=neg_p)
            out.append({
                "variant_question": q,
                "expected": f"({neg_p}; 0)",
                "demonstration": f"The vertical asymptote of f is x = -p = {-p}. The point where g meets this asymptote lies on the x-axis, so it is ({-p}, 0). That is the x-intercept of g. Answer: ({-p}; 0).",
                "memo_marks": [f"1 mark for ({-p}; 0)"],
                "fast_path": "Where g meets the vertical asymptote IS the x-intercept of g.",
                "fatal_error": "DBE says: Candidates give just -p without the y-coordinate, or swap x and y. Intercepts are written as coordinates.",
                "answer_book_layout": [f"Vertical asymptote: x = {-p}", f"g meets it at x-axis: ({-p}, 0)", f"Answer: ({-p}; 0)"],
                "hack": "The x-intercept is where g meets the vertical asymptote. The x-value is exactly the vertical asymptote.",
                "trap": "Coordinates, not just the number. Write the y = 0 explicitly.",
                "presentation": "State the x-value, then the full coordinate pair.",
                "diagram": "required", "diagram_hint": "hyperbola_with_vertical_asymptote_and_line",
            })
    random.shuffle(out)
    return out[:30]


# ===== 6.2 — determine equation of f from three constraints =====
def gen_6_2():
    # (x1, x2) pairs: g intersects horizontal asymptote at x1, intersects f at x2
    # Derived: p = x1 - x2, a = x1*(x2-x1), c = p, q = 2*x1 - x2
    pairs = [
        (1, 3), (1, 4), (2, 5), (1, 2), (2, 4), (2, 3), (3, 5),
        (1, 5), (2, 6), (1, 6), (3, 6), (2, 7), (4, 6), (1, 7),
        (2, 8), (3, 7),
    ]
    out = []
    for x1, x2 in pairs:
        p = x1 - x2
        a = x1 * (x2 - x1)
        c = p
        q = 2 * x1 - x2
        # f(x) = a/(x+p) + q  = a/(x - x2) + q
        # g(x) = x + c
        # Note: vertical asymptote of f is x = -p = x2
        f_expr = f"f(x) = {a}/(x - {x2}) + ({q})" if q >= 0 else f"f(x) = {a}/(x - {x2}) - {abs(q)}"
        if q == 0:
            f_expr = f"f(x) = {a}/(x - {x2})"
        if q == 0:
            f_expr_simple = f"f(x) = {a}/(x - {x2})"
        elif q > 0:
            f_expr_simple = f"f(x) = {a}/(x - {x2}) + {q}"
        else:
            f_expr_simple = f"f(x) = {a}/(x - {x2}) - {abs(q)}"
        q_str = f"+ {q}" if q > 0 else (f"- {abs(q)}" if q < 0 else "")
        
        question = (
            f"The graphs of g(x) = x + c and f(x) = a/(x + p) + q are drawn. "
            f"g and the vertical asymptote of f intersect on the x-axis. "
            f"g intersects the horizontal asymptote of f at x = {x1}, "
            f"and g intersects f at x = {x2}. "
            f"f and g also intersect on the y-axis. Determine the equation of f."
        )
        
        demo = (
            f"Step 1: From the x-axis intersection, g(-p) = 0 → -p + c = 0 → c = p.\n"
            f"Step 2: From the horizontal asymptote intersection, g({x1}) = q → {x1} + c = q.\n"
            f"Step 3: From the y-axis intersection, f(0) = g(0) → a/p + q = c.\n"
            f"Step 4: From the f intersection, g({x2}) = f({x2}) → {x2} + c = a/({x2} + p) + q.\n"
            f"Solving: c = p = {p}, a = {a}, q = {q}.\n"
            f"Answer: f(x) = {a}/(x - {x2}) {q_str}."
        )
        
        out.append({
            "variant_question": question,
            "expected": f_expr_simple,
            "demonstration": demo,
            "memo_marks": [
                "1 mark for c = p (from x-axis intersection)",
                f"1 mark for q = {x1} + c",
                "1 mark for f(0) = g(0) giving a in terms of p",
                f"1 mark for substitution into f({x2}) = g({x2})",
                f"1 mark for a = {a}, p = {p}, q = {q} and the final f(x)"
            ],
            "fast_path": "Three constraints, three unknowns. c = p from x-axis. q from horizontal asymptote. a from either y-axis or f-intersection.",
            "fatal_error": "DBE says: Candidates try to use all three points simultaneously without exploiting c = p first. The x-axis intersection is the key — it gives c = p for free.",
            "answer_book_layout": [
                f"g(-p) = 0 → c = p = {p}",
                f"g({x1}) = q → q = {x1} + c = {q}",
                f"f(0) = g(0) → a/p + q = c → a = {a}",
                f"f(x) = {a}/(x - {x2}) {q_str}"
            ],
            "hack": "c = p from the x-axis. Then everything falls into place. Don't try to solve three equations in three unknowns from scratch — start with the free one.",
            "trap": "The vertical asymptote is x = -p, so the x-intercept is (-p, 0). Sign matters.",
            "presentation": "Show each constraint used. The five marks come from four steps plus final answer.",
            "diagram": "required", "diagram_hint": "line_and_hyperbola_with_all_intersections",
        })
    
    # Repeat to fill 30
    while len(out) < 30:
        out.extend(out[:30-len(out)])
    random.shuffle(out)
    return out[:30]


# ===== 6.3 — transformation description (practice only) =====
def gen_6_3():
    # Same (x1, x2) pairs → axis of symmetry y = x + (p+q), shift from g
    pairs = [
        (1, 3), (1, 4), (2, 5), (1, 2), (2, 4), (2, 3), (3, 5),
        (1, 5), (2, 6), (1, 6),
    ]
    out = []
    for x1, x2 in pairs:
        p = x1 - x2
        c = p
        q = 2 * x1 - x2
        # Axis of symmetry (slope +1): y = x + (p + q)
        shift_down = (p + q) - c  # how much to shift g down
        # g(x) = x + c, want y = x + (p+q). Shift down by (p+q-c) = shift up by (c-p-q).
        # Equivalent: shift right by (c - (p+q))
        shift_right = c - (p + q)
        
        if shift_down == 0 and shift_right == 0:
            continue  # g already is the axis
        
        # Provide one or both valid answers
        valid_answers = []
        if shift_down < 0:
            valid_answers.append(f"Translation {abs(shift_down)} units down")
        elif shift_down > 0:
            valid_answers.append(f"Translation {shift_down} units up")
        if shift_right > 0:
            valid_answers.append(f"Translation {shift_right} units right")
        elif shift_right < 0:
            valid_answers.append(f"Translation {abs(shift_right)} units left")
        
        if not valid_answers:
            continue
        
        question = (
            f"f(x) = {x1*(x2-x1)}/(x - {x2}) {('+ ' + str(q)) if q > 0 else (('- ' + str(abs(q))) if q < 0 else '')}, "
            f"g(x) = x + ({c}). Describe the transformation that g must undergo "
            f"to become an axis of symmetry of f that cuts f at two points."
        )
        
        out.append({
            "variant_question": question,
            "expected": valid_answers[0],
            "demonstration": f"The axis of symmetry of f with positive gradient is y = x + (p + q) = x + ({p} + {q}) = x + ({p+q}). g is y = x + ({c}). To transform g into the axis: {'shift down by ' + str(abs(shift_down)) + ' units' if shift_down < 0 else ('shift up by ' + str(shift_down) + ' units' if shift_down > 0 else 'no vertical shift')}, OR {'shift right by ' + str(shift_right) + ' units' if shift_right > 0 else ('shift left by ' + str(abs(shift_right)) + ' units' if shift_right < 0 else 'no horizontal shift')}. Either description is accepted.",
            "memo_marks": [f"2 marks for '{valid_answers[0]}' (or equivalent)"],
            "fast_path": "Axis of symmetry: y = x + (p+q). Compare to g = x + c. Difference in y-intercept = shift.",
            "fatal_error": "DBE says: Candidates give the wrong axis (the negative-gradient one y = -x + (q-p) usually does not cut f) or describe the shift without the number.",
            "answer_book_layout": ["Axis of symmetry: y = x + (p+q)", f"g is: y = x + {c}", f"Shift: {valid_answers[0]}"],
            "hack": "Positive-gradient axis is y = x + (p+q). Subtract g from it and you have the shift.",
            "trap": "The negative-gradient axis (y = -x + (q-p)) does not cut f. Use the positive one.",
            "presentation": "State the axis, state g, state the shift amount and direction.",
            "practice_only": True,
            "diagram": "required", "diagram_hint": "line_and_hyperbola_with_axis_of_symmetry",
        })
    
    while len(out) < 30:
        out.extend(out[:30-len(out)])
    random.shuffle(out)
    return out[:30]


print("Generating Q6 pools...\n")
for name, fn in [("6.1", gen_6_1), ("6.2", gen_6_2), ("6.3", gen_6_3)]:
    variants = fn()
    n = write_pool(name, variants)
    print(f"  {name}: {n} variants")

print("\n=== VERIFY ===")
for name in ["6.1", "6.2", "6.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:110]}")
        print(f"     Expected: {v['expected']}")
