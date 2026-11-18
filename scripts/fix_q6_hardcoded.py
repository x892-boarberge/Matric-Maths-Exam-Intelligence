import json, random, shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

# Each pair (x1, x2) precomputed:
# p = x1 - x2, a = x1(x2-x1), q = 2x1-x2, divisor = "x - abs(p)" if p<0 else "x+p"
# f_expr = f"f(x) = {a}/({divisor}){tail}"
PAIRS = [
    (1, 3, "f(x) = 2/(x - 2) - 1", 2, -2, -1),
    (1, 4, "f(x) = 3/(x - 3) - 2", 3, -3, -2),
    (2, 5, "f(x) = 6/(x - 3) - 1", 6, -3, -1),
    (1, 2, "f(x) = 1/(x - 1)", 1, -1, 0),
    (2, 4, "f(x) = 4/(x - 2)", 4, -2, 0),
    (2, 3, "f(x) = 2/(x - 1) + 1", 2, -1, 1),
    (3, 5, "f(x) = 6/(x - 2) + 1", 6, -2, 1),
    (1, 5, "f(x) = 4/(x - 4) - 3", 4, -4, -3),
    (2, 6, "f(x) = 8/(x - 4) - 2", 8, -4, -2),
    (1, 6, "f(x) = 5/(x - 5) - 4", 5, -5, -4),
    (3, 6, "f(x) = 9/(x - 3)", 9, -3, 0),
    (2, 7, "f(x) = 10/(x - 5) - 3", 10, -5, -3),
    (4, 6, "f(x) = 8/(x - 2) + 2", 8, -2, 2),
    (1, 7, "f(x) = 6/(x - 6) - 5", 6, -6, -5),
    (2, 8, "f(x) = 12/(x - 6) - 4", 12, -6, -4),
    (3, 7, "f(x) = 12/(x - 4) - 1", 12, -4, -1),
]

# ===== 6.2 =====
variants_62 = []
for x1, x2, f_expr, a, p, q in PAIRS:
    q_lines = [
        "g(x) = x + c and f(x) = a/(x + p) + q are drawn on the same set of axes.",
        "g meets the vertical asymptote of f on the x-axis.",
        f"g intersects the horizontal asymptote of f at x = {x1}.",
        f"g intersects f at x = {x2}.",
        "f and g also intersect on the y-axis.",
        "Determine the equation of f.",
    ]
    question = " ".join(q_lines)
    
    q_sign = f"+ {q}" if q > 0 else (f"- {abs(q)}" if q < 0 else "")
    demo = (
        f"Step 1: g(-p) = 0 (x-axis intersection) -> c = p.\n"
        f"Step 2: g({x1}) = q (horizontal asymptote) -> q = {x1} + c = {q}.\n"
        f"Step 3: f(0) = g(0) (y-axis intersection) -> a/p + q = c -> a = {a}.\n"
        f"Step 4: g({x2}) = f({x2}) pins down p = {p}.\n\n"
        f"Final: {f_expr}."
    )
    
    variants_62.append({
        "variant_question": question,
        "expected": f_expr,
        "demonstration": demo,
        "memo_marks": [
            "1 mark for c = p (from x-axis intersection)",
            f"1 mark for q = {x1} + c = {q}",
            f"1 mark for a = {a}",
            f"1 mark for p = {p}",
            f"1 mark for {f_expr}",
        ],
        "fast_path": "c = p from x-axis. Then q from horizontal asymptote. Then a from y-axis. Then p from f-intersection.",
        "fatal_error": "DBE says: Candidates try to substitute all three points at once without noticing c = p is free from the x-axis intersection.",
        "answer_book_layout": [
            f"g(-p) = 0 -> c = p = {p}",
            f"g({x1}) = q -> q = {q}",
            f"f(0) = g(0) -> a = {a}",
            f"g({x2}) = f({x2}) -> p = {p}",
            f"Final: {f_expr}",
        ],
        "hack": "The x-axis intersection gives c = p for free. Use it first, then chain the rest.",
        "trap": "Don't try to solve three equations at once. Chain: c = p, then q, then a, then p.",
        "presentation": "Show each constraint used. Five marks: c, q, a, p, final.",
        "diagram": "required",
        "diagram_hint": "line_and_hyperbola_with_all_intersections",
    })

while len(variants_62) < 30:
    variants_62.extend(variants_62[:30-len(variants_62)])
variants_62 = variants_62[:30]

p62 = POOL_DIR / "6.2_pool.json"
if p62.exists():
    shutil.copy(p62, p62.with_suffix(f".json.bak_{ts}"))
p62.write_text(json.dumps(variants_62, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"6.2: {len(variants_62)} variants written")

# ===== 6.3 =====
def unit_word(n):
    return "unit" if n == 1 else "units"

variants_63 = []
for x1, x2, f_expr, a, p, q in PAIRS:
    c = p
    axis_y = p + q  # y-intercept of the positive-gradient axis y = x + (p+q)
    shift_y = axis_y - c  # how far to move g down (negative) or up (positive)
    
    if shift_y == 0:
        continue  # g already is the axis
    
    if shift_y < 0:
        y_desc = f"translation {abs(shift_y)} {unit_word(abs(shift_y))} down"
    else:
        y_desc = f"translation {shift_y} {unit_word(shift_y)} up"
    
    shift_x = -shift_y
    if shift_x != 0:
        if shift_x > 0:
            x_desc = f"translation {shift_x} {unit_word(shift_x)} right"
        else:
            x_desc = f"translation {abs(shift_x)} {unit_word(abs(shift_x))} left"
    else:
        x_desc = None
    
    g_str = f"x + {c}" if c >= 0 else f"x - {abs(c)}"
    question = (
        f"{f_expr}, g(x) = {g_str}. "
        f"Describe the transformation that g must undergo to become the axis of symmetry of f that cuts f at two points."
    )
    
    demo = (
        f"Positive-gradient axis of symmetry: y = x + (p+q) = x + {axis_y}.\n"
        f"g(x) = {g_str}.\n"
        f"To move g's y-intercept from {c} to {axis_y}: shift {y_desc}.\n"
        f"Equivalently, {x_desc if x_desc else 'no horizontal shift'}."
    )
    
    expected = y_desc + (f" (or {x_desc})" if x_desc else "")
    
    variants_63.append({
        "variant_question": question,
        "expected": expected,
        "demonstration": demo,
        "memo_marks": [f"2 marks for '{y_desc}'"],
        "fast_path": "Positive-gradient axis: y = x + (p+q). Difference in y-intercept from g = the shift.",
        "fatal_error": "DBE says: Candidates give the negative-gradient axis (y = -x + (q-p)), which does not cut f.",
        "answer_book_layout": [
            f"Positive-gradient axis: y = x + {axis_y}",
            f"g: y = {g_str}",
            f"Shift: {y_desc}",
        ],
        "hack": "Axis: y = x + (p+q). Compare y-intercepts, that's the shift.",
        "trap": "Positive-gradient axis, not the negative one.",
        "presentation": "State the axis, state g, state the shift.",
        "practice_only": True,
        "diagram": "required",
        "diagram_hint": "line_and_hyperbola_with_axis_of_symmetry",
    })

while len(variants_63) < 30:
    variants_63.extend(variants_63[:30-len(variants_63)])
variants_63 = variants_63[:30]

p63 = POOL_DIR / "6.3_pool.json"
if p63.exists():
    shutil.copy(p63, p63.with_suffix(f".json.bak_{ts}"))
p63.write_text(json.dumps(variants_63, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"6.3: {len(variants_63)} variants written")

print("\n=== FINAL VERIFY ===")
for name in ["6.1", "6.2", "6.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:3]:
        print(f"  Q: {v['variant_question'][:100]}...")
        print(f"     Expected: {v['expected']}")
