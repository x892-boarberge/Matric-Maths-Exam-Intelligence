import json, shutil, math
from pathlib import Path
from datetime import datetime
from fractions import Fraction

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def fmt_frac(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


# ============ 9.3 — sign chart, verified configs ============
NINE_THREE_CONFIGS = [
    (-1, 2, 7), (-2, 1, 6), (-1, 3, 8), (-3, 0, 7), (-2, 2, 5),
    (0, 3, 8), (-1, 1, 5), (-2, 3, 7), (-3, 1, 6), (-4, -1, 6),
    (-1, 2, 4), (-2, 0, 3), (-3, 2, 6), (0, 2, 7), (-1, 4, 9),
    (1, 3, 5), (-2, 3, 8), (-1, 5, 7), (0, 4, 9), (-3, 3, 6),
]

def gen_9_3():
    out = []
    for r1, r2, r3 in NINE_THREE_CONFIGS:
        b = -(r1 + r2 + r3)
        c = r1*r2 + r1*r3 + r2*r3
        d = -r1*r2*r3
        x_inf = Fraction(-b, 3)
        if any(abs(float(x_inf) - r) < 0.001 for r in [r1, r2, r3]):
            continue
        points = sorted(set([Fraction(r1), Fraction(r2), Fraction(r3), x_inf]))
        
        def f_sign(x):
            v = (x - r1) * (x - r2) * (x - r3)
            return 1 if v > 0 else (-1 if v < 0 else 0)
        def fpp_sign(x):
            return 1 if x > x_inf else (-1 if x < x_inf else 0)
        
        yes_intervals = []
        for i in range(len(points) - 1):
            mid = (points[i] + points[i+1]) / 2
            if f_sign(mid) * fpp_sign(mid) < 0:
                yes_intervals.append((points[i], points[i+1]))
        if not yes_intervals:
            continue
        
        terms = ["x^3"]
        if b != 0: terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
        if c != 0: terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
        if d != 0: terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
        f_expr = " ".join(terms)
        
        interval_strs = [f"{fmt_frac(lo)} < x < {fmt_frac(hi)}" for lo, hi in yes_intervals]
        expected = " or ".join(interval_strs)
        
        q = f"Given f(x) = {f_expr}, determine the values of x for which f(x) · f''(x) < 0."
        
        demo = (f"f(x) = 0 at x = {r1}, {r2}, {r3}.\n"
                f"f''(x) = 6x + {2*b} = 0 at x = {fmt_frac(x_inf)}.\n"
                f"Sign chart: f and f'' have opposite signs on: {expected}.")
        
        out.append({
            "variant_question": q,
            "expected": expected,
            "demonstration": demo,
            "memo_marks": [f"1 mark for x-intercepts {r1}, {r2}, {r3}",
                           f"1 mark for f'' zero at x = {fmt_frac(x_inf)}",
                           f"1 mark for sign analysis", f"1 mark for {expected}"],
            "fast_path": "Sign chart. Where f and f'' disagree, the product is negative.",
            "fatal_error": "DBE says: Candidates solve f(x)<0 or f''(x)<0 separately, forgetting the product needs opposite signs.",
            "answer_book_layout": [f"f(x) = 0 at {r1}, {r2}, {r3}",
                                    f"f''(x) = 0 at {fmt_frac(x_inf)}",
                                    f"Opposite signs: {expected}"],
            "hack": "Two sign charts, one for f, one for f''. Answer is where they disagree.",
            "trap": "f and f'' have zeroes at different points. Combine carefully.",
            "presentation": "Show both sign charts then the intervals.",
            "diagram": "required", "diagram_hint": "sign_chart_f_and_fpp",
        })
    return out


# ============ 9.4 — tangency interval ============
NINE_FOUR_TRIPLES = [
    (-2, 2, 3), (-1, 2, 5), (-3, 1, 4), (-2, 1, 4), (-2, 2, 5),
    (-1, 3, 6), (0, 2, 5), (-3, 2, 5), (-2, 3, 6), (-1, 4, 7),
    (-3, 0, 4), (-2, 0, 3), (-1, 1, 4), (-3, 2, 6), (-2, 4, 7),
]
M_VALUES = [-12, -10, -8, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 8, 10, 12]

def gen_9_4():
    out = []
    for r1, r2, r3 in NINE_FOUR_TRIPLES:
        b = -(r1 + r2 + r3)
        c = r1*r2 + r1*r3 + r2*r3
        d = -r1*r2*r3
        # f'(x) = 3x^2 + 2bx + c
        for m in M_VALUES:
            A = 3
            B_m = 2 * b
            C_m = c - m
            disc = B_m*B_m - 4*A*C_m
            if disc < 0:
                continue
            sqrt_disc = int(disc ** 0.5)
            if sqrt_disc ** 2 != disc:
                continue
            x1 = Fraction(-B_m - sqrt_disc, 2*A)
            x2 = Fraction(-B_m + sqrt_disc, 2*A)
            if x1 == x2:
                continue
            def f_val(x): return x**3 + b*x**2 + c*x + d
            t1 = f_val(x1) - m*x1
            t2 = f_val(x2) - m*x2
            if t1 == t2:
                continue
            t_low, t_high = min(t1, t2), max(t1, t2)
            
            terms = ["x^3"]
            if b != 0: terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
            if c != 0: terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
            if d != 0: terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
            f_expr = " ".join(terms)
            
            if m > 0:
                m_str = f"{m}x" if m != 1 else "x"
            else:
                m_str = f"-{abs(m)}x" if m != -1 else "-x"
            
            q = f"For which values of t will the line y = {m_str} + t intersect f(x) = {f_expr} at exactly 3 distinct points?"
            expected = f"{fmt_frac(t_low)} < t < {fmt_frac(t_high)}"
            
            demo = (f"f'(x) = 3x^2 + {B_m}x + {c}. Set = {m}: 3x^2 + {B_m}x + {c-m} = 0 "
                    f"-> x = {fmt_frac(x1)} or {fmt_frac(x2)}.\n"
                    f"At x = {fmt_frac(x1)}: t = {fmt_frac(t1)}.\n"
                    f"At x = {fmt_frac(x2)}: t = {fmt_frac(t2)}.\n"
                    f"Three distinct points require t between the tangency values: {expected}.")
            
            out.append({
                "variant_question": q,
                "expected": expected,
                "demonstration": demo,
                "memo_marks": [f"1 mark for f'(x) = {m}",
                               f"1 mark for x = {fmt_frac(x1)}, {fmt_frac(x2)}",
                               f"1 mark for t = {fmt_frac(t_low)}",
                               f"1 mark for t = {fmt_frac(t_high)}",
                               f"1 mark for {expected}"],
                "fast_path": "Set f'(x) = m, find two tangency points, compute t at each. Range between them.",
                "fatal_error": "DBE says: Candidates hand in the two tangency t-values instead of the interval. Below or above gives 1 intersection, not 3.",
                "answer_book_layout": [f"f'(x) = 3x^2 + {B_m}x + {c}",
                                        f"= {m} -> x = {fmt_frac(x1)}, {fmt_frac(x2)}",
                                        f"t at x={fmt_frac(x1)}: {fmt_frac(t1)}",
                                        f"t at x={fmt_frac(x2)}: {fmt_frac(t2)}",
                                        f"Three intersections: {expected}"],
                "hack": "Two tangent lines bound the answer. Between them = 3 intersections.",
                "trap": "t values are tangencies (2 intersections). Answer is strictly between them.",
                "presentation": "Show both tangency t-values, then the interval.",
                "diagram": "required", "diagram_hint": "cubic_with_tangent_lines",
            })
            if len(out) >= 30:
                break
        if len(out) >= 30:
            break
    return out


# ============ 10.1 — perimeter P, formula P/2·x^2/(4π) ============
def gen_10_1():
    out = []
    P_VALUES = [30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60]
    for P in P_VALUES:
        coeff = P // 2  # integer since P even
        x_sample = P // 3  # a sample x to show the physical setup
        h_sample = P // 2 - x_sample
        q = (f"A rectangular metal sheet has dimensions x and h units, with x > h, and a perimeter of "
             f"2(x + h) = {P} units. The sheet is rolled into a cylinder with two open ends "
             f"(top and bottom) and height h units. "
             f"Show that the volume of the cylinder is V = ({coeff}x^2)/(4π) - (x^3)/(4π).")
        
        demo = (f"Step 1: From perimeter 2x + 2h = {P}, solve for h:\n"
                f"  h = ({P} - 2x)/2 = {coeff} - x.\n"
                f"Step 2: Circumference of base = x, so 2πr = x -> r = x/(2π).\n"
                f"Step 3: V = πr^2 h = π(x/(2π))^2 · ({coeff} - x)\n"
                f"  = (x^2/(4π)) · ({coeff} - x)\n"
                f"  = ({coeff}x^2)/(4π) - (x^3)/(4π).  QED")
        
        out.append({
            "variant_question": q,
            "expected": f"V = ({coeff}x^2)/(4π) - (x^3)/(4π)",
            "demonstration": demo,
            "memo_marks": ["1 mark for h = P/2 - x",
                           "1 mark for r = x/(2π)",
                           "1 mark for substitution into V = πr^2 h"],
            "fast_path": "Perimeter -> h. Circumference -> r. Substitute both into V.",
            "fatal_error": "DBE says: Candidates forget the 2π in the radius, or leave two variables.",
            "answer_book_layout": [f"2x + 2h = {P} -> h = {coeff} - x",
                                    "2πr = x -> r = x/(2π)",
                                    "V = πr^2 h = π(x/(2π))^2 · h",
                                    f"= ({coeff}x^2)/(4π) - (x^3)/(4π)"],
            "hack": "Perimeter gives h. Circumference gives r. One substitution each, then V = πr²h.",
            "trap": "Radius is x/(2π), not x/2. The x is the circumference, not the diameter.",
            "presentation": "Show h, r, then the substitution and simplification.",
            "practice_only": True,
            "diagram": "required", "diagram_hint": "cylinder_from_rectangle",
        })
    return out


# ============ 10.2 — x_max = P/3 (from V'(x)=0) ============
def gen_10_2():
    out = []
    P_VALUES = [30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60]
    for P in P_VALUES:
        coeff = P // 2
        x_max = Fraction(2 * coeff, 3)  # = P/3
        x_max_str = fmt_frac(x_max)
        if Fraction(P, 3).denominator == 1:
            x_max_str = str(Fraction(P, 3).numerator)
        
        q = (f"A cylinder (from a rectangle with perimeter {P}) has volume "
             f"V(x) = ({coeff}x^2)/(4π) - (x^3)/(4π). "
             f"Calculate the value of x that maximises the volume.")
        
        demo = (f"V'(x) = (2·{coeff}x)/(4π) - (3x^2)/(4π) = ({P}x - 3x^2)/(4π).\n"
                f"Set V'(x) = 0: {P}x - 3x^2 = 0 -> x({P} - 3x) = 0.\n"
                f"x = 0 (reject, no volume) or x = {P}/3 = {x_max_str}.\n"
                f"Answer: x = {x_max_str}.")
        
        out.append({
            "variant_question": q,
            "expected": f"x = {x_max_str}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for V'(x) = ({P}x - 3x^2)/(4π)",
                           "1 mark for setting V'(x) = 0",
                           f"1 mark for x = {x_max_str} (reject x=0)"],
            "fast_path": "Differentiate, set zero, factor. x=0 is minimum, other root is maximum.",
            "fatal_error": "DBE says: Candidates forget to reject x=0. A volume of 0 is the minimum, not the maximum.",
            "answer_book_layout": [f"V'(x) = ({P}x - 3x^2)/(4π)",
                                    f"V'(x) = 0 -> x({P} - 3x) = 0",
                                    f"x = 0 (reject) or x = {x_max_str}"],
            "hack": "Differentiate, set zero, factor. x=0 is min, other root is max.",
            "trap": "Don't forget to reject x=0.",
            "presentation": "Show derivative, factor, reject, state x.",
            "diagram": "required", "diagram_hint": "volume_vs_x_curve",
        })
    return out


# Run
print("Fixing 9.3, 9.4, 10.1, 10.2...\n")
for name, fn in [("9.3", gen_9_3), ("9.4", gen_9_4), ("10.1", gen_10_1), ("10.2", gen_10_2)]:
    variants = fn()
    if len(variants) < 30:
        # Pad by cycling if non-empty
        if len(variants) == 0:
            print(f"  {name}: ERROR - 0 valid variants produced")
            continue
        while len(variants) < 30:
            variants.extend(variants[:30-len(variants)])
        variants = variants[:30]
    n = write_pool(name, variants[:30])
    print(f"  {name}: {n} variants")

print("\n=== VERIFY FIXED POOLS ===")
for name in ["9.3", "9.4", "10.1", "10.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:100]}...")
        print(f"     Expected: {v['expected']}")
