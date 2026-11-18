import json, shutil, math
from pathlib import Path
from datetime import datetime
from fractions import Fraction

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def fmt_frac(f):
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

def write_pool(name, variants):
    if not variants:
        raise ValueError(f"{name}: 0 variants")
    # Safety: no Fractions in output
    def check(obj):
        if isinstance(obj, Fraction):
            raise TypeError(f"Fraction leaked into {name}")
        if isinstance(obj, dict):
            for v in obj.values(): check(v)
        if isinstance(obj, (list, tuple)):
            for v in obj: check(v)
    for v in variants: check(v)
    
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


def find_geometric_series():
    """Helper — returns list of (A, B, C, t, r) tuples. Not JSON output."""
    out = []
    seen = set()
    for A in range(-10, 16):
        for B in range(-6, 8):
            for C in range(-10, 16):
                denom = A + C + 2 * B
                if denom == 0: continue
                numer = B*B - A*C
                if numer % denom != 0: continue
                t = numer // denom
                if abs(t) > 5 or t == 0: continue
                if (t - B)**2 != (t + A) * (t + C): continue
                if t + A == 0: continue
                r = Fraction(t - B, t + A)
                if abs(r) >= 1: continue
                key = (A, B, C)
                if key in seen: continue
                seen.add(key)
                out.append((A, B, C, t, r))
    out.sort(key=lambda x: (abs(x[3]), x[0], x[1], x[2]))
    return out[:30]


# ============================================================================
# 2.1.1 — Show that t = value
# ============================================================================
def gen_2_1_1():
    out = []
    for A, B, C, t, r in find_geometric_series():
        q = (f"Given the geometric series: (t+{A}) + (t-{B}) + (t+{C}) + ..., "
             f"show that t = {t}.")
        first = t + A
        second = t - B
        third = t + C
        demo = (f"Geometric condition: middle squared = first × third.\n"
                f"(t-{B})^2 = (t+{A})(t+{C})\n"
                f"t^2 - {2*B}t + {B*B} = t^2 + {A+C}t + {A*C}\n"
                f"-{2*B}t - {A+C}t = {A*C} - {B*B}\n"
                f"{-2*B - A - C}t = {A*C - B*B}\n"
                f"t = {A*C - B*B}/{-(2*B + A + C)} = {t}\n"
                f"Verify: {first}, {second}, {third} — ratio = {fmt_frac(r)} constant.")
        out.append({
            "variant_question": q,
            "expected": f"t = {t}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for setting up (t-{B})^2 = (t+{A})(t+{C})",
                           f"1 mark for expansion",
                           f"1 mark for solving t = {t}"],
            "fast_path": "Geometric condition: middle squared = product of other two. Expand, solve.",
            "fatal_error": "DBE says: Candidates use the ratio equation but forget to cross-multiply. Or expand (t+A)(t+C) and lose signs.",
            "answer_book_layout": [f"(t-{B})^2 = (t+{A})(t+{C})",
                                    f"t^2 - {2*B}t + {B*B} = t^2 + {A+C}t + {A*C}",
                                    f"t = {t}"],
            "hack": "Geometric: middle^2 = outer product. Expand both sides, solve.",
            "trap": "Sign errors in expansion. Write each step on its own line.",
            "presentation": "Show the setup, expansion, solution.",
            "diagram": "required", "diagram_hint": "geometric_series_visual",
        })
    return out


# ============================================================================
# 2.1.2 — T_n in b^x form
# ============================================================================
def gen_2_1_2():
    out = []
    configs = []
    for p in [-2, -1, 1, 2, 3, 4]:
        for k in [1, 2, 3]:
            for sign in [1, -1]:
                for n in [10, 12, 15, 20, 25]:
                    a = Fraction(2)**p
                    r = Fraction(sign, 2**k)
                    T_n = a * r**(n-1)
                    if T_n == 0: continue
                    absT = abs(T_n)
                    if absT.denominator == 1:
                        log2v = math.log2(absT.numerator)
                        if log2v == int(log2v):
                            configs.append((p, k, sign, n, int(log2v)))
                    elif absT.numerator == 1:
                        log2v = math.log2(absT.denominator)
                        if log2v == int(log2v):
                            configs.append((p, k, sign, n, -int(log2v)))
    seen = set()
    unique = []
    for c in configs:
        if c[:4] not in seen:
            seen.add(c[:4])
            unique.append(c)
    unique.sort(key=lambda x: x[3])
    
    for p, k, sign, n, exp in unique[:30]:
        a_val = Fraction(2)**p
        a_str = fmt_frac(a_val)
        r_disp = f"1/{2**k}" if sign > 0 else f"-1/{2**k}"
        
        if exp >= 0:
            T_str = f"2^{exp}"
        else:
            T_str = f"2^({exp})"
        if sign < 0 and (n - 1) % 2 == 1:
            T_str = "-" + T_str if not T_str.startswith("-") else T_str[1:]
        
        q = (f"Given the geometric series: {a_str} + {a_str}·({r_disp}) + {a_str}·({r_disp})^2 + ..., "
             f"calculate T_{n}. Write your answer in the form T_n = b^x.")
        demo = (f"a = {a_str}, r = {r_disp}.\n"
                f"T_{n} = a·r^(n-1) = ({a_str})·({r_disp})^{n-1} = {T_str}.")
        out.append({
            "variant_question": q,
            "expected": f"T_{n} = {T_str}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for a = {a_str}, r = {r_disp}", f"1 mark for substitution", f"1 mark for {T_str}"],
            "fast_path": "T_n = a·r^(n-1). Identify a and r, plug in, simplify power.",
            "fatal_error": "DBE says: Candidates use n instead of (n-1). GAPS: seats minus 1.",
            "answer_book_layout": [f"a = {a_str}, r = {r_disp}", f"T_{n} = ({a_str})·({r_disp})^{n-1}", f"= {T_str}"],
            "hack": "Power is seats minus one (GAPS).",
            "trap": "For 25th term, exponent is 24, not 25.",
            "presentation": "Show a, r, substitution, simplified power.",
            "diagram": "required", "diagram_hint": "geometric_sequence_visual",
        })
    return out


# ============================================================================
# 2.1.3 — Sum to infinity
# ============================================================================
def gen_2_1_3():
    out = []
    for A, B, C, t, r in find_geometric_series():
        a = t + A
        if a == 0 or abs(r) >= 1: continue
        S = Fraction(a) / (1 - r)
        s1, s2, s3 = t + A, t - B, t + C
        q = (f"Given the geometric series: ({t}+{A}) + ({t}-{B}) + ({t}+{C}) + ... = "
             f"{s1} + {s2} + {s3} + ..., calculate the sum of the infinite series.")
        demo = (f"First term a = {s1}, ratio r = {fmt_frac(r)}.\n"
                f"|r| = {abs(r.numerator)}/{r.denominator} < 1, so S_infinity exists.\n"
                f"S_infinity = a / (1 - r) = {s1} / (1 - ({fmt_frac(r)})) = {fmt_frac(S)}.")
        out.append({
            "variant_question": q,
            "expected": fmt_frac(S),
            "demonstration": demo,
            "memo_marks": [f"1 mark for a = {s1}", f"1 mark for r = {fmt_frac(r)}",
                           f"1 mark for |r| < 1 check", f"1 mark for {fmt_frac(S)}"],
            "fast_path": "S_infinity = a/(1-r). Show |r|<1 first.",
            "fatal_error": "DBE says: Candidates forget the |r|<1 check or use wrong first term.",
            "answer_book_layout": [f"a = {s1}, r = {fmt_frac(r)}", f"|r| < 1 ✓",
                                    f"S_infinity = {s1}/(1 - ({fmt_frac(r)})) = {fmt_frac(S)}"],
            "hack": "First term / (1 − ratio). Brake check first.",
            "trap": "Show |r|<1 explicitly — it's a mark.",
            "presentation": "State a, r, check, then formula.",
            "diagram": "required", "diagram_hint": "geometric_series_infinite",
        })
    return out


# ============================================================================
# 2.2.1 — T_m − T_n difference
# ============================================================================
def gen_2_2_1():
    out = []
    configs = []
    for a in [2, 3, 4, 5, 6]:
        for b in [-5, -3, -1, 1, 3, 5]:
            for m, n in [(14, 6), (20, 10), (15, 7), (25, 11), (18, 4), (10, 3), (30, 12)]:
                if m <= n: continue
                diff = a * (m - n)
                configs.append((a, b, m, n, diff))
    seen = set()
    unique = []
    for c in configs:
        if (c[0], c[1], c[2], c[3]) not in seen:
            seen.add((c[0], c[1], c[2], c[3]))
            unique.append(c)
    unique.sort(key=lambda x: (x[0], x[2]))
    
    for a, b, m, n, diff in unique[:30]:
        b_str = f"+ {b}" if b > 0 else f"- {abs(b)}"
        q = (f"Given the arithmetic sequence T_p = {a}p {b_str}, "
             f"write down the difference between T_{m} and T_{n}.")
        tm = a*m + b
        tn = a*n + b
        demo = (f"T_{m} = {a}·{m} {b_str} = {tm}.\n"
                f"T_{n} = {a}·{n} {b_str} = {tn}.\n"
                f"Difference = {tm} - {tn} = {diff}.\n"
                f"Shortcut: {a}·({m}-{n}) = {a}·{m-n} = {diff}.")
        out.append({
            "variant_question": q,
            "expected": f"{diff}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for both term values", f"1 mark for {diff}"],
            "fast_path": "Difference in values = a × difference in positions.",
            "fatal_error": "DBE says: Candidates confuse T_p formula with sum formula, or drop the b term wrong.",
            "answer_book_layout": [f"T_{m} = {tm}, T_{n} = {tn}", f"Difference = {diff}"],
            "hack": "Difference = coefficient × position gap.",
            "trap": "Subtract carefully. b cancels but am - an doesn't.",
            "presentation": "Show both terms, then subtraction.",
            "diagram": "required", "diagram_hint": "arithmetic_sequence_visual",
        })
    return out


# ============================================================================
# 2.2.2 — Find k given sum = S
# ============================================================================
def gen_2_2_2():
    out = []
    configs = []
    for a in [2, 3, 4, 5]:
        for b in [-5, -3, -1, 1, 3]:
            for N in [50, 60, 80, 100, 117]:
                for k in [15, 18, 20, 21, 25, 30]:
                    if k >= N: continue
                    n_terms = N - k + 1
                    first = a*k + b
                    last = a*N + b
                    S = n_terms * (first + last) // 2
                    if S <= 0: continue
                    configs.append((a, b, N, k, S))
    seen = set()
    unique = []
    for c in configs:
        if (c[0], c[1], c[2], c[3]) not in seen:
            seen.add((c[0], c[1], c[2], c[3]))
            unique.append(c)
    unique.sort(key=lambda x: x[0])
    
    for a, b, N, k, S in unique[:30]:
        b_str = f"+ {b}" if b > 0 else f"- {abs(b)}"
        q = (f"Given that the sum from p=k to {N} of ({a}p {b_str}) equals {S}, "
             f"calculate the value of k.")
        last = a*N + b
        demo = (f"First term (p=k): {a}k {b_str}. Last term (p={N}): {last}.\n"
                f"Number of terms: {N} - k + 1.\n"
                f"Sum = ({N}-k+1)/2 · ({a}k {b_str} + {last}) = {S}.\n"
                f"Verify k = {k}: n_terms = {N-k+1}, first = {a*k+b}, last = {last}, "
                f"sum = {N-k+1}/2 × ({a*k+b} + {last}) = {S}. ✓")
        out.append({
            "variant_question": q,
            "expected": f"k = {k}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for first term {a}k {b_str}", f"1 mark for last term {last}",
                           f"1 mark for n_terms = {N}-k+1",
                           f"1 mark for equation setup", f"1 mark for k = {k}"],
            "fast_path": "Sum = n/2·(first+last). Set to S. Solve for k.",
            "fatal_error": "DBE says: Candidates lose the term count ({N}-k+1) and guess k values.",
            "answer_book_layout": [f"First = {a}k {b_str}, Last = {last}",
                                    f"n_terms = {N}-k+1",
                                    f"Sum = ({N}-k+1)/2 · ({a}k {b_str} + {last}) = {S}",
                                    f"k = {k}"],
            "hack": "Sum = n/2(first+last). Substitute k as unknown. Solve.",
            "trap": "Term count is N-k+1, not N-k. ICE rule.",
            "presentation": "Show first, last, count, equation, solve.",
            "diagram": "required", "diagram_hint": "sum_from_k_to_N",
        })
    return out


# Run
print("Generating Q2 pools...\n")
for name, fn in [("2.1.1", gen_2_1_1), ("2.1.2", gen_2_1_2), ("2.1.3", gen_2_1_3),
                  ("2.2.1", gen_2_2_1), ("2.2.2", gen_2_2_2)]:
    variants = fn()
    try:
        n = write_pool(name, variants)
        print(f"  {name}: {n} variants")
    except (ValueError, TypeError) as e:
        print(f"  {name}: FAILED — {e}")

print("\n=== VERIFY ===")
for name in ["2.1.1", "2.1.2", "2.1.3", "2.2.1", "2.2.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        print(f"\n{name}: MISSING")
        continue
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:110]}...")
        print(f"     Expected: {v['expected']}")
