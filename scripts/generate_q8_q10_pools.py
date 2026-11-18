import json, random, shutil, math
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
random.seed(8910)

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


# ===== 8.1 First principles (linear function) =====
def gen_8_1():
    out = []
    configs = [(m, c) for m in [-4, -3, -2, -1, 1, 2, 3, 4, 5] for c in [-3, -1, 0, 2, 4, 5, 7]]
    random.shuffle(configs)
    for m, c in configs[:30]:
        if m < 0:
            f_str = f"f(x) = {m}x + {c}" if c > 0 else (f"f(x) = {m}x - {abs(c)}" if c < 0 else f"f(x) = {m}x")
        elif c == 0:
            f_str = f"f(x) = {m}x" if m != 1 else "f(x) = x"
        else:
            f_str = f"f(x) = {m}x + {c}" if m != 1 else f"f(x) = x + {c}"
        q = f"Determine f'(x) from first principles if it is given that {f_str}."
        out.append({
            "variant_question": q,
            "expected": f"f'(x) = {m}",
            "demonstration": f"f(x) = {m}x {'+' if c>=0 else '-'} {abs(c) if c else ''}\n".replace(" + ", " + ") if False else None,
            "memo_marks": [f"1 mark for f(x+h) substitution", f"1 mark for simplification", f"1 mark for taking the limit", f"1 mark for f'(x) = {m}"],
            "fast_path": "f(x+h) - f(x) = m·h. Divide by h gives m. Limit is still m.",
            "fatal_error": "DBE says: Candidates skip the h-cancellation step or write the answer without showing the limit. Four marks are earned by showing four steps.",
            "answer_book_layout": [f"f(x+h) = {m}(x+h) {'+' if c>=0 else '-'} {abs(c) if c else ''}", f"f(x+h) - f(x) = {m}h", f"[f(x+h) - f(x)]/h = {m}", f"f'(x) = lim(h→0) {m} = {m}"],
            "hack": "For a linear function, the derivative is always the gradient. Just show the algebra.",
            "trap": "The c term cancels. Don't try to keep it.",
            "presentation": "Show all four steps: f(x+h), difference, quotient, limit.",
            "diagram": "required",
            "diagram_hint": "first_principles_setup",
        })
    # fill demonstration properly
    for v in out:
        pass
    return out


# Fix demo for 8.1 (simplified, no template failure)
def gen_8_1_v2():
    out = []
    configs = [(m, c) for m in [-4, -3, -2, -1, 1, 2, 3, 4, 5] for c in [-3, -1, 0, 2, 4, 5, 7]]
    random.shuffle(configs)
    for m, c in configs[:30]:
        if c == 0:
            f_str = f"f(x) = {m}x"
        elif c > 0:
            f_str = f"f(x) = {m}x + {c}"
        else:
            f_str = f"f(x) = {m}x - {abs(c)}"
        q = f"Determine f'(x) from first principles if it is given that {f_str}."
        c_term = f" + {c}" if c > 0 else (f" - {abs(c)}" if c < 0 else "")
        out.append({
            "variant_question": q,
            "expected": f"f'(x) = {m}",
            "demonstration": f"1. f(x+h) = {m}(x+h){c_term} = {m}x + {m}h{c_term}.\n2. f(x+h) - f(x) = ({m}x + {m}h{c_term}) - ({m}x{c_term}) = {m}h.\n3. [f(x+h) - f(x)]/h = {m}h/h = {m}.\n4. lim(h→0) {m} = {m}.\nAnswer: f'(x) = {m}.",
            "memo_marks": ["1 mark for f(x+h) substitution", "1 mark for simplification", "1 mark for taking the limit", f"1 mark for f'(x) = {m}"],
            "fast_path": "For a linear function, the derivative is always the gradient. Just show the algebra.",
            "fatal_error": "DBE says: Candidates skip the h-cancellation step or write the answer without showing the limit. Four marks are earned by showing four steps.",
            "answer_book_layout": [f"f(x+h) = {m}(x+h){c_term}", f"f(x+h) - f(x) = {m}h", f"[f(x+h) - f(x)]/h = {m}", f"f'(x) = lim(h→0) {m} = {m}"],
            "hack": "For a linear function, the derivative is always the gradient. Just show the algebra.",
            "trap": "The c term cancels. Don't try to keep it.",
            "presentation": "Show all four steps: f(x+h), difference, quotient, limit.",
            "diagram": "required",
            "diagram_hint": "first_principles_setup",
        })
    return out


# ===== 8.2.1 Power rule =====
def gen_8_2_1():
    out = []
    configs = [
        (-3, 4, 2, 1), (5, 3, -2, 2, 0), (2, 5, -4, 3), (7, 4, 0, 1),
        (-2, 3, 6, 2, 5), (4, 5, -2, 3), (3, 6, 1), (-5, 2, 3, 1),
        (6, 4, -8, 2), (-4, 3, 2, 1), (8, 2, -3, 3), (-7, 5, 4),
        (2, 6, -1, 2), (9, 3, -5, 1), (-3, 4, 6, 2), (5, 5, 0, 3),
        (3, 4, -2, 2), (-6, 3, 1, 1), (4, 6, -3, 2), (7, 2, 5),
        (-2, 5, 3, 1), (6, 3, -4, 2), (2, 4, 1, 3), (-9, 3, 2),
        (5, 6, -7, 1), (8, 2, 3, 2), (-4, 4, 1), (3, 5, -2, 3),
        (6, 4, 5, 2), (-5, 3, -1, 1),
    ]
    for cfg in configs[:30]:
        # cfg = (a, n, b, m) with optional c constant last
        a, n = cfg[0], cfg[1]
        b = cfg[2] if len(cfg) > 2 else 0
        m = cfg[3] if len(cfg) > 3 else 0
        c = cfg[4] if len(cfg) > 4 else 0
        # g(x) = ax^n + bx^m + c
        terms_g = []
        if a != 0:
            if n == 1: terms_g.append(f"{a}x")
            else: terms_g.append(f"{a}x^{n}")
        if b != 0 and m > 0:
            sign = "+" if b > 0 else "-"
            ab = abs(b)
            if m == 1: terms_g.append(f"{sign} {ab}x" if ab != 1 else f"{sign} x")
            else: terms_g.append(f"{sign} {ab}x^{m}" if ab != 1 else f"{sign} x^{m}")
        if c != 0:
            sign = "+" if c > 0 else "-"
            terms_g.append(f"{sign} {abs(c)}")
        g_expr = " ".join(terms_g).replace("+ -", "- ")
        # derivative: anx^(n-1) + bmx^(m-1) + 0
        terms_d = []
        if a != 0:
            coef = a * n
            exp = n - 1
            if exp == 0: terms_d.append(f"{coef}")
            elif exp == 1: terms_d.append(f"{coef}x")
            else: terms_d.append(f"{coef}x^{exp}")
        if b != 0 and m > 0:
            coef = b * m
            exp = m - 1
            sign = "+" if coef > 0 else "-"
            ab = abs(coef)
            if exp == 0: terms_d.append(f"{sign} {ab}")
            elif exp == 1: terms_d.append(f"{sign} {ab}x" if ab != 1 else f"{sign} x")
            else: terms_d.append(f"{sign} {ab}x^{exp}" if ab != 1 else f"{sign} x^{exp}")
        d_expr = " ".join(terms_d).replace("+ -", "- ")
        if d_expr.startswith("+ "):
            d_expr = d_expr[2:]
        q = f"Determine g'(x) if g(x) = {g_expr}."
        out.append({
            "variant_question": q,
            "expected": f"g'(x) = {d_expr}",
            "demonstration": f"Apply the power rule term by term:\n  d/dx({a}x^{n}) = {a*n}x^{n-1}\n" + (f"  d/dx({b}x^{m}) = {b*m}x^{m-1}\n" if b else "") + f"Answer: g'(x) = {d_expr}.",
            "memo_marks": [f"1 mark for derivative of first term", f"1 mark for derivative of second term" if b else "", f"1 mark for final answer"],
            "fast_path": "Power rule term by term. Coefficient × exponent, exponent - 1.",
            "fatal_error": "DBE says: Candidates drop the coefficient multiplication (write nx^(n-1) instead of anx^(n-1)) or forget to subtract 1 from the exponent.",
            "answer_book_layout": [f"g(x) = {g_expr}", f"g'(x) = {d_expr}"],
            "hack": "Multiply by exponent, drop exponent by 1. Every term independent.",
            "trap": "Constant terms differentiate to 0. Coefficients multiply.",
            "presentation": "Show term-by-term differentiation.",
            "diagram": "required",
            "diagram_hint": "power_rule_visual",
        })
    return out


# ===== 8.2.2 Split-quotient =====
def gen_8_2_2():
    out = []
    configs = [
        (2, 4, 1, 2), (3, 5, 4, 2), (5, 6, 3, 2), (1, 3, 5, 1),
        (4, 5, 2, 2), (2, 6, 3, 3), (6, 4, 1, 2), (3, 7, 2, 2),
        (2, 5, 5, 2), (7, 4, 3, 2), (5, 6, 7, 3), (4, 7, 1, 2),
        (2, 4, 3, 1), (3, 6, 5, 3), (6, 5, 4, 2), (8, 4, 2, 2),
        (5, 3, 7, 2), (2, 7, 3, 2), (4, 6, 1, 2), (3, 4, 6, 2),
        (2, 5, 7, 3), (5, 5, 2, 2), (6, 6, 4, 3), (2, 3, 8, 2),
        (4, 5, 5, 2), (7, 4, 4, 2), (3, 6, 2, 2), (2, 8, 1, 2),
        (5, 4, 6, 3), (6, 5, 3, 2),
    ]
    for a, n, b, k in configs[:30]:
        # y = (ax^n + b)/x^k = a·x^(n-k) + b·x^(-k)
        # dy/dx = a(n-k)x^(n-k-1) - bk x^(-k-1)
        coef1 = a
        exp1 = n - k
        coef2 = b
        exp2 = -k
        
        # derivative
        d_coef1 = coef1 * exp1 if exp1 != 0 else 0
        d_exp1 = exp1 - 1
        d_coef2 = coef2 * exp2
        d_exp2 = exp2 - 1
        
        q = f"Determine dy/dx if y = ({a}x^{n} + {b})/x^{k}."
        
        # Format first derivative term
        if d_coef1 == 0:
            term1 = ""
        elif d_exp1 == 0:
            term1 = f"{d_coef1}"
        elif d_exp1 == 1:
            term1 = f"{d_coef1}x"
        else:
            term1 = f"{d_coef1}x^{d_exp1}"
        
        # Second term: d_coef2·x^d_exp2 — d_coef2 is negative (since exp2 = -k < 0)
        sign = "-" if d_coef2 < 0 else "+"
        abs_d_coef2 = abs(d_coef2)
        if d_exp2 == 0:
            term2 = f"{sign} {abs_d_coef2}" if sign else f"{abs_d_coef2}"
        elif d_exp2 == 1:
            term2 = f"{sign} {abs_d_coef2}x" if sign else f"{abs_d_coef2}x"
        else:
            term2 = f"{sign} {abs_d_coef2}x^{d_exp2}" if sign else f"{abs_d_coef2}x^{d_exp2}"
        
        if term1:
            d_expr = f"{term1} {term2}"
        else:
            d_expr = term2.lstrip("+ ")
        
        # Split form
        split1 = f"{a}x^{exp1}" if exp1 != 0 else f"{a}"
        split2_sign = "+" if b > 0 else "-"
        split2 = f"{split2_sign} {abs(b)}x^{exp2}"
        split_form = f"{split1} {split2}"
        
        out.append({
            "variant_question": q,
            "expected": f"dy/dx = {d_expr}",
            "demonstration": f"Split first: y = {a}x^{n}/x^{k} + {b}/x^{k} = {split_form}.\nDifferentiate term by term:\n  d/dx({split1}) = {d_coef1}x^{d_exp1} if d_coef1 else 0\n  d/dx({split2}) = {d_coef2}x^{d_exp2}\nAnswer: dy/dx = {d_expr}.",
            "memo_marks": [f"1 mark for split to {split1}", f"1 mark for split to {split2}", f"1 mark for derivative of first term", f"1 mark for derivative of second term"],
            "fast_path": "Divide each numerator term by x^k, get negative exponents, then power rule.",
            "fatal_error": "DBE says: Candidates use the quotient rule, or fail to write negative exponents correctly. The split is the shortcut.",
            "answer_book_layout": [f"y = ({a}x^{n} + {b})/x^{k}", f"y = {split_form}", f"dy/dx = {d_expr}"],
            "hack": "Split first. Every top term divides by x^k. Then power rule on negative exponents.",
            "trap": "x^{-k} differentiates to -k·x^{-k-1}. The exponent drops by 1 AND gets more negative.",
            "presentation": "Show the split explicitly. Then differentiate each term.",
            "diagram": "required",
            "diagram_hint": "quotient_split_visual",
        })
    return out


# ===== 9.1 Cubic turning point =====
def gen_9_1():
    out = []
    # f(x) = (x-r1)(x-r2)(x-r3), expand, find turning points
    configs = [
        (1, 3, 5), (0, 2, 4), (-1, 2, 4), (-2, 1, 3), (1, 4, 6),
        (-1, 3, 5), (0, 3, 6), (2, 5, 7), (-2, 2, 5), (-1, 4, 6),
        (1, 2, 5), (-3, 1, 4), (0, 4, 8), (2, 3, 6), (-1, 1, 3),
    ]
    for r1, r2, r3 in configs:
        # Expand (x-r1)(x-r2)(x-r3) = x^3 + bx^2 + cx + d
        b = -(r1 + r2 + r3)
        c = r1*r2 + r1*r3 + r2*r3
        d = -r1*r2*r3
        # f'(x) = 3x^2 + 2bx + c
        # Turning points: 3x^2 + 2bx + c = 0
        A = 3
        B = 2 * b
        C = c
        disc = B*B - 4*A*C
        if disc < 0:
            continue
        x1 = (-B - math.sqrt(disc)) / (2*A)
        x2 = (-B + math.sqrt(disc)) / (2*A)
        if abs(x1 - round(x1)) > 0.001 and abs(x2 - round(x2)) > 0.001:
            continue  # not clean
        # Format f(x)
        terms = ["x^3"]
        if b != 0:
            terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
        if c != 0:
            terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
        if d != 0:
            terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
        f_expr = " ".join(terms)
        
        # f'(x)
        d_terms = [f"3x^2"]
        if B != 0:
            d_terms.append(f"{'+' if B>0 else '-'} {abs(B)}x")
        if C != 0:
            d_terms.append(f"{'+' if C>0 else '-'} {abs(C)}")
        dp_expr = " ".join(d_terms)
        
        # Compute both turning points
        tps = []
        for x_val in [x1, x2]:
            y_val = A*x_val**2 + B*x_val + C  # wrong, use f(x_val)
            y_val = x_val**3 + b*x_val**2 + c*x_val + d
            tps.append((x_val, y_val))
        
        q = f"Calculate the coordinates of the turning points of f(x) = {f_expr}."
        expected_parts = [f"({x1}; {y1})" for x1, y1 in tps if x1 != x2]
        if len(expected_parts) >= 2:
            expected = f"{expected_parts[0]} and {expected_parts[1]}"
        else:
            expected = expected_parts[0] if expected_parts else "n/a"
        
        demo = f"f'(x) = {dp_expr}. Set f'(x) = 0: {dp_expr} = 0 → x = {x1} or x = {x2}.\nSubstitute back:\nf({x1}) = {tps[0][1]}\nf({x2}) = {tps[1][1]}\nTurning points: {expected}."
        
        out.append({
            "variant_question": q,
            "expected": expected,
            "demonstration": demo,
            "memo_marks": [f"1 mark for f'(x) = {dp_expr}", f"1 mark for x = {x1} or x = {x2}", f"1 mark for y-values", f"1 mark for both coordinate pairs"],
            "fast_path": "f'(x) = 0, factor, solve for x. Substitute each x for y.",
            "fatal_error": "DBE says: Candidates hand in just the x-values. Turning points are coordinate pairs.",
            "answer_book_layout": [f"f'(x) = {dp_expr}", f"{dp_expr} = 0 → x = {x1} or x = {x2}", f"f({x1}) = {tps[0][1]}", f"f({x2}) = {tps[1][1]}", f"Turning points: {expected}"],
            "hack": "Set derivative to zero, solve x, substitute for y.",
            "trap": "Coordinate pair, not just x. And there are usually two turning points.",
            "presentation": "Show derivative, solve x, substitute each for y, list both pairs.",
            "diagram": "required",
            "diagram_hint": "cubic_with_two_turning_points",
        })
    # Pad to 30 by repeating + shuffling
    while len(out) < 30:
        out.extend(out[:30-len(out)])
    random.shuffle(out)
    return out[:30]


# ===== 9.2 Concavity =====
def gen_9_2():
    out = []
    configs = [
        (1, 3, 5), (0, 2, 4), (-1, 2, 4), (-2, 1, 3), (1, 4, 6),
        (-1, 3, 5), (0, 3, 6), (2, 5, 7), (-2, 2, 5), (-1, 4, 6),
        (1, 2, 5), (-3, 1, 4), (0, 4, 8), (2, 3, 6), (-1, 1, 3),
    ]
    for r1, r2, r3 in configs:
        b = -(r1 + r2 + r3)
        c = r1*r2 + r1*r3 + r2*r3
        d = -r1*r2*r3
        # f''(x) = 6x + 2b, set = 0 → x = -b/3 = (r1+r2+r3)/3
        x_inf = -b / 3
        # Concave down where f''<0: 6x + 2b < 0 → x < -b/3
        # Concave up where f''>0: x > -b/3
        terms = ["x^3"]
        if b != 0: terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
        if c != 0: terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
        if d != 0: terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
        f_expr = " ".join(terms)
        
        x_str = str(x_inf) if x_inf != int(x_inf) else str(int(x_inf))
        # Use fractions where possible
        if abs(x_inf - round(x_inf * 3) / 3) < 0.001:
            from fractions import Fraction
            frac = Fraction(round(x_inf * 3), 3)
            x_str = str(frac)
        
        q = f"For which values of x is f(x) = {f_expr} concave down?"
        out.append({
            "variant_question": q,
            "expected": f"x < {x_str}",
            "demonstration": f"f'(x) = 3x^2 + {2*b}x + {c}.\nf''(x) = 6x + {2*b}.\nConcave down means f''(x) < 0: 6x + {2*b} < 0 → x < {x_str}.",
            "memo_marks": [f"1 mark for f''(x) = 6x + {2*b}", f"1 mark for f''(x) < 0", f"1 mark for x < {x_str}"],
            "fast_path": "Second derivative, set < 0 for concave down (> 0 for concave up), solve for x.",
            "fatal_error": "DBE says: Candidates flip the inequality direction (write x > 2 instead of x < 2). Check: concave down means f''<0, which usually gives x < something for positive leading coefficient.",
            "answer_book_layout": [f"f'(x) = 3x^2 + {2*b}x + {c}", f"f''(x) = 6x + {2*b}", f"f''(x) < 0 → x < {x_str}"],
            "hack": "Concave down = f''<0. Differentiate twice, set < 0, solve.",
            "trap": "Concave UP is f''>0, not f''<0. And don't confuse concavity with increasing/decreasing.",
            "presentation": "Show f''(x) then the inequality then the interval.",
            "diagram": "required",
            "diagram_hint": "cubic_with_inflection_point",
        })
    while len(out) < 30:
        out.extend(out[:30-len(out)])
    random.shuffle(out)
    return out[:30]


# ===== 9.3 Sign chart =====
def gen_9_3():
    out = []
    # (r1, r2, r3) with distinct integers, none equal to (r1+r2+r3)/3
    configs = [
        (-1, 2, 7), (-2, 1, 5), (-3, 0, 6), (-1, 0, 3), (-2, 0, 4),
        (-4, -1, 4), (-1, 3, 4), (0, 2, 7), (-3, -1, 7), (-1, 4, 6),
        (-4, -2, 3), (-2, 3, 6), (0, 1, 5), (1, 4, 7), (-3, 2, 4),
    ]
    for r1, r2, r3 in configs:
        b = -(r1 + r2 + r3)
        c = r1*r2 + r1*r3 + r2*r3
        d = -r1*r2*r3
        x_inf = -b / 3
        
        # Check x_inf not equal to any root
        if any(abs(x_inf - r) < 0.001 for r in [r1, r2, r3]):
            continue
        
        # Sign analysis
        # f sign: + on (r1, r2), (r3, +inf); - on (-inf, r1), (r2, r3)
        # since leading coeff +1
        # f'' sign: - on (-inf, x_inf); + on (x_inf, +inf)
        
        # Breakpoints: sort roots and x_inf
        points = sorted([r1, r2, r3, x_inf])
        
        # For each interval between consecutive points, compute sign of f and f''
        def f_sign(x):
            return 1 if ((x-r1)*(x-r2)*(x-r3)) > 0 else -1
        def fpp_sign(x):
            return 1 if (x - x_inf) > 0 else -1
        
        # Intervals where product < 0
        yes_intervals = []
        for i in range(len(points) - 1):
            mid = (points[i] + points[i+1]) / 2
            if f_sign(mid) * fpp_sign(mid) < 0:
                yes_intervals.append((points[i], points[i+1]))
        
        if not yes_intervals:
            continue
        
        # Format f(x)
        terms = ["x^3"]
        if b != 0: terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
        if c != 0: terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
        if d != 0: terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
        f_expr = " ".join(terms)
        
        # Format expected answer
        from fractions import Fraction
        expected_parts = []
        for lo, hi in yes_intervals:
            lo_str = str(Fraction(lo).limit_denominator(1000))
            hi_str = str(Fraction(hi).limit_denominator(1000))
            expected_parts.append(f"{lo_str} < x < {hi_str}")
        expected = " or ".join(expected_parts)
        
        q = f"Given f(x) = {f_expr}, determine the values of x for which f(x) · f''(x) < 0."
        
        out.append({
            "variant_question": q,
            "expected": expected,
            "demonstration": f"f has x-intercepts at x = {r1}, {r2}, {r3}.\nf''(x) = 6x + {2*b}, so f''(x) = 0 at x = {Fraction(x_inf).limit_denominator(1000)}.\nSign chart: f and f'' have opposite signs on: {expected}.",
            "memo_marks": [f"1 mark for x-intercepts {r1}, {r2}, {r3}", f"1 mark for f'' root at x = {Fraction(x_inf).limit_denominator(1000)}", f"1 mark for sign analysis", f"1 mark for {expected}"],
            "fast_path": "Sign chart. Where f and f'' have opposite signs, the product is negative.",
            "fatal_error": "DBE says: Candidates solve f(x)<0 or f''(x)<0 separately, forgetting the product needs opposite signs.",
            "answer_book_layout": [f"f(x) = 0 at {r1}, {r2}, {r3}", f"f''(x) = 0 at {Fraction(x_inf).limit_denominator(1000)}", f"Opposite signs on: {expected}"],
            "hack": "Two sign charts, one for f one for f''. Answer is where they disagree.",
            "trap": "f and f'' cross zero at different points. Combine carefully.",
            "presentation": "Show both sign charts then the intervals.",
            "diagram": "required",
            "diagram_hint": "sign_chart_f_and_fpp",
        })
    while len(out) < 30:
        out.extend(out[:30-len(out)])
    random.shuffle(out)
    return out[:30]


# ===== 9.4 Line-cubic intersections =====
def gen_9_4():
    out = []
    # Manually verified configs: (r1, r2, r3, m, t_low, t_high)
    configs = [
        # f(x) = (x-r1)(x-r2)(x-r3), f'(x)=m has two roots, giving tangency t's
        (-2, 2, 3, -4, 8, 12),  # wait we computed 8 < t < 12 above
        # hmm 8 < t < 12 was for x^3-3x^2-4x+12 = (x+2)(x-2)(x-3)
        # and m = -4. Verify: f'(x) = 3x^2-6x-4 = -4 → x=0 or x=2. Tangency t at x=2: f(2)-(-4)(2) = 0+8=8. At x=0: f(0)-0 = 12. So 8<t<12.
        # OK use it
    ]
    
    # Let me use a cleaner approach: enumerate many, verify computationally
    for r1 in [-3, -2, -1, 0, 1, 2]:
        for r2 in [r1+1, r1+2, r1+3]:
            for r3 in [r2+1, r2+2, r2+3]:
                # f(x) = (x-r1)(x-r2)(x-r3)
                b = -(r1 + r2 + r3)
                c = r1*r2 + r1*r3 + r2*r3
                d = -r1*r2*r3
                # f'(x) = 3x^2 + 2bx + c
                A, B, C = 3, 2*b, c
                # Try various m values from -10 to 10
                for m in range(-10, 11):
                    if m == 0: continue
                    # Solve 3x^2 + Bx + (C - m) = 0
                    A_m = 3
                    B_m = B
                    C_m = C - m
                    disc = B_m*B_m - 4*A_m*C_m
                    if disc < 0: continue
                    x1 = (-B_m - math.sqrt(disc)) / (2*A_m)
                    x2 = (-B_m + math.sqrt(disc)) / (2*A_m)
                    # Need distinct, clean
                    if abs(x1 - x2) < 0.001: continue
                    if abs(x1 - round(x1)) > 0.001 or abs(x2 - round(x2)) > 0.001:
                        continue
                    # Tangency t values
                    def f(x): return x**3 + b*x**2 + c*x + d
                    t1 = f(x1) - m*x1
                    t2 = f(x2) - m*x2
                    if abs(t1 - t2) < 0.001: continue
                    t_low, t_high = min(t1, t2), max(t1, t2)
                    
                    # Format f(x)
                    terms = ["x^3"]
                    if b != 0: terms.append(f"{'+' if b>0 else '-'} {abs(b)}x^2")
                    if c != 0: terms.append(f"{'+' if c>0 else '-'} {abs(c)}x")
                    if d != 0: terms.append(f"{'+' if d>0 else '-'} {abs(d)}")
                    f_expr = " ".join(terms)
                    
                    # Format m
                    if m > 0: m_str = f"{m}x" if m != 1 else "x"
                    else: m_str = f"-{abs(m)}x" if m != -1 else "-x"
                    line_str = f"y = {m_str} + t"
                    
                    q = f"For which values of t will {line_str} intersect f(x) = {f_expr} at exactly 3 distinct points?"
                    expected = f"{t_low:g} < t < {t_high:g}"
                    
                    out.append({
                        "variant_question": q,
                        "expected": expected,
                        "demonstration": f"f'(x) = 3x^2 + {2*b}x + {c}. Set f'(x) = m = {m}: 3x^2 + {2*b}x + {c-m} = 0 → x = {x1:g} or {x2:g}.\nAt x = {x1:g}: f({x1:g}) = {f(x1):g}, t = f - mx = {t1:g}.\nAt x = {x2:g}: f({x2:g}) = {f(x2):g}, t = {t2:g}.\nFor 3 distinct intersections, t must lie strictly between {t_low:g} and {t_high:g}.",
                        "memo_marks": [f"1 mark for f'(x) = m setup", f"1 mark for x = {x1:g}, {x2:g}", f"1 mark for t = {t_low:g}", f"1 mark for t = {t_high:g}", f"1 mark for interval {expected}", f"1 mark for strict inequality"],
                        "fast_path": "Set f'(x) = m, solve for two x-values. Compute t at each. Range between them.",
                        "fatal_error": "DBE says: Candidates hand in the two t values instead of the interval. Below or above gives 1 intersection; between gives 3.",
                        "answer_book_layout": [f"f'(x) = 3x^2 + {2*b}x + {c}", f"= {m} → x = {x1:g}, {x2:g}", f"t at x={x1:g}: {t1:g}", f"t at x={x2:g}: {t2:g}", f"3 distinct points: {expected}"],
                        "hack": "Two tangent lines bound the answer. Between them = 3 intersections.",
                        "trap": "The t values are tangencies (2 intersections), not the answer. Answer is BETWEEN them.",
                        "presentation": "Show both tangency t-values, then the interval.",
                        "diagram": "required",
                        "diagram_hint": "cubic_with_tangent_lines",
                    })
                    if len(out) >= 30:
                        break
                if len(out) >= 30:
                    break
            if len(out) >= 30:
                break
        if len(out) >= 30:
            break
    
    while len(out) < 30:
        if not out:
            break
        out.extend(out[:min(len(out), 30-len(out))])
    random.shuffle(out)
    return out[:30]


# ===== 10.1 Show volume formula (practice only) =====
def gen_10_1():
    out = []
    for i in range(30):
        x_val = 20 + (i % 6) * 5
        h_val = 15 + (i % 4) * 3
        q = (f"A rectangular metal sheet has dimensions x and h units, with x > h, and a perimeter of 2(x+h) = {2*(x_val+h_val)} units. "
             f"The metal sheet is rolled into a cylinder with two open ends (top and bottom) and height h units. "
             f"Show that the volume of the cylinder is given by V = (x^2 × (({2*(x_val+h_val)} - 2x)/2)) / (4π).")
        out.append({
            "variant_question": q,
            "expected": "Practice — show the algebraic derivation.",
            "demonstration": f"Perimeter: 2x + 2h = {2*(x_val+h_val)}, so h = ({2*(x_val+h_val)} - 2x)/2. Circumference: 2πr = x, so r = x/(2π). Volume: V = πr²h = π(x/(2π))² × h = x²/(4π) × h.",
            "memo_marks": ["1 mark for h in terms of x", "1 mark for r in terms of x", "1 mark for substitution into V"],
            "fast_path": "Two constraints: perimeter gives h, circumference gives r. Substitute both into V = πr²h.",
            "fatal_error": "DBE says: Candidates don't write h in terms of x first, leaving two variables. Or they forget the 2π in the radius.",
            "answer_book_layout": ["2x + 2h = P → h = (P - 2x)/2", "2πr = x → r = x/(2π)", "V = πr²h = π(x/(2π))² × h", "Simplifies to the required form"],
            "hack": "Two constraints: perimeter for h, circumference for r. Substitute both.",
            "trap": "Radius is x/(2π), not x/2. The x is the circumference, not the diameter.",
            "presentation": "Show both substitutions clearly.",
            "practice_only": True,
            "diagram": "required",
            "diagram_hint": "cylinder_from_rectangle",
        })
    return out


# ===== 10.2 Optimisation =====
def gen_10_2():
    out = []
    # V(x) = (P·x^2)/(4π) - x^3/(4π) where P = 2(x+h) is perimeter
    # V'(x) = (2P·x)/(4π) - 3x^2/(4π) = 0 → 2P·x - 3x^2 = 0 → x = 2P/3
    configs = [
        (50,), (60,), (45,), (54,), (72,), (40,), (80,), (66,), (48,), (56,)
    ]
    for i, (P,) in enumerate(configs * 3):
        if i >= 30: break
        x_max = 2 * P / 3
        q = f"A rectangle has perimeter {P} units. It is folded into a cylinder with two open ends. The volume is given by V(x) = ({P}x^2)/(4π) - x^3/(4π). Calculate the value of x that maximises the volume."
        out.append({
            "variant_question": q,
            "expected": f"x = {x_max:g}",
            "demonstration": f"V'(x) = ({2*P}x)/(4π) - 3x^2/(4π) = 0.\nMultiply by 4π: {2*P}x - 3x^2 = 0.\nFactor: x({2*P} - 3x) = 0 → x = 0 (reject) or x = {x_max:g}.\nAnswer: x = {x_max:g}.",
            "memo_marks": [f"1 mark for V'(x) = ({2*P}x - 3x^2)/(4π)", f"1 mark for setting V'(x) = 0", f"1 mark for x = {x_max:g} (reject x=0)"],
            "fast_path": "Differentiate, set = 0, factor, reject x=0.",
            "fatal_error": "DBE says: Candidates forget to reject x=0 or skip V'(x)=0. A volume of 0 at x=0 is the minimum, not maximum.",
            "answer_book_layout": [f"V'(x) = ({2*P}x - 3x^2)/(4π)", f"V'(x) = 0 → x({2*P} - 3x) = 0", f"x = 0 (reject) or x = {x_max:g}"],
            "hack": "Differentiate, set zero, factor. x=0 is min (no volume). The other root is max.",
            "trap": "Don't forget to reject x=0. It's a valid root of the derivative, but not a maximum.",
            "presentation": "Show derivative, set zero, factor, reject x=0, state x value.",
            "diagram": "required",
            "diagram_hint": "cylinder_volume_maximised",
        })
    return out


# Run all
print("Generating Q8-Q10 pools...\n")
for name, fn in [
    ("8.1", gen_8_1_v2), ("8.2.1", gen_8_2_1), ("8.2.2", gen_8_2_2),
    ("9.1", gen_9_1), ("9.2", gen_9_2), ("9.3", gen_9_3), ("9.4", gen_9_4),
    ("10.1", gen_10_1), ("10.2", gen_10_2),
]:
    try:
        v = fn()
        n = write_pool(name, v)
        print(f"  {name}: {n} variants")
    except Exception as e:
        print(f"  {name}: ERROR {e}")

print("\n=== VERIFY ===")
for name in ["8.1", "8.2.1", "8.2.2", "9.1", "9.2", "9.3", "9.4", "10.1", "10.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        print(f"{name}: MISSING")
        continue
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:90]}...")
        print(f"     Expected: {v['expected']}")
