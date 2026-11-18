import json, shutil, math
from pathlib import Path
from datetime import datetime
from fractions import Fraction

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

PLACEHOLDERS = {"Calculation", "Fraction", "Number", "Interval", "Range of t", "Range of x", ""}

def fmt_frac(f):
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

def write_pool(name, variants):
    if not variants:
        raise ValueError(f"{name}: generator returned 0 variants — refusing to write")
    # Check no placeholder answers
    for v in variants[:3]:
        if v.get("expected", "") in PLACEHOLDERS:
            raise ValueError(f"{name}: first variant expected='{v.get('expected')}' — stub detected")
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)


# ============ 11.1.1 ============
def gen_11_1_1():
    out = []
    configs = []
    for N in [120, 150, 180, 200, 240, 250, 300, 320]:
        for M in [40, 50, 60, 75, 80, 100, 120, 150]:
            if M >= N: continue
            for T in [30, 40, 45, 50, 60, 75, 90, 100]:
                if T >= N: continue
                if (M * T) % N == 0:
                    k = (M * T) // N
                    F = N - M
                    C = N - T
                    mc = M - k
                    ft = T - k
                    fc = N - M - T + k
                    if all(x >= 0 for x in [k, mc, ft, fc]):
                        configs.append((N, M, T, k, mc, ft, fc))
    seen = set()
    unique = []
    for c in configs:
        key = (c[0], c[1], c[2])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    for N, M, T, mt, mc, ft, fc in unique[:30]:
        q = (f"In a survey of {N} learners, {M} are male and {T} prefer tea. "
             f"The events 'male' and 'preferring tea' are independent. "
             f"The table shows: Male-Tea = {mt}, Male-Coffee = {mc}, Female-Tea = {ft}, "
             f"Female-Coffee = e. Show that e = {fc}.")
        demo = (f"Independence: P(male and tea) = P(male) × P(tea).\n"
                f"P(male) = {M}/{N}. P(tea) = {T}/{N}. P(male and tea) = {mt}/{N}.\n"
                f"Check: ({M}/{N})·({T}/{N}) = {M*T}/{N*N} = {mt}/{N}  ✓ ({mt} = {M*T}/{N}).\n"
                f"Total: {mt} + {mc} + {ft} + e = {N} → e = {fc}.")
        out.append({
            "variant_question": q,
            "expected": f"e = {fc}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for P(male and tea) = P(male)·P(tea)",
                           f"1 mark for verifying {mt}/{N} = ({M}/{N})·({T}/{N})",
                           f"1 mark for e = {fc}"],
            "fast_path": "Independence = product. Then total minus known cells gives e.",
            "fatal_error": "DBE says: Candidates confuse independent with mutually exclusive. Independent → P(A and B) = P(A)·P(B).",
            "answer_book_layout": [f"P(male and tea) = {mt}/{N}",
                                    f"P(male)·P(tea) = {M}/{N}·{T}/{N} = {mt}/{N}",
                                    f"e = {N} - {mt} - {mc} - {ft} = {fc}"],
            "hack": "Independent → multiply. Missing cell → total minus known.",
            "trap": "Mutually exclusive vs independent. Different concepts.",
            "presentation": "Show P·P, compare, complete the table.",
            "diagram": "required", "diagram_hint": "contingency_table",
        })
    return out


# ============ 11.1.2 ============
def gen_11_1_2():
    out = []
    configs = [
        (200, 100, 70, 30, 30, 70), (150, 80, 50, 30, 40, 30),
        (240, 120, 80, 40, 60, 60), (300, 150, 100, 50, 80, 70),
        (160, 80, 60, 20, 40, 40), (250, 130, 90, 40, 70, 50),
        (180, 100, 65, 35, 45, 35), (220, 110, 70, 40, 60, 50),
        (120, 70, 45, 25, 30, 20), (100, 60, 40, 20, 30, 10),
        (280, 140, 95, 45, 85, 55), (320, 160, 110, 50, 100, 60),
    ]
    for N, F, FC, FT, MC, MT in configs:
        if F != FC + FT or (N - F) != MC + MT:
            continue
        prob = Fraction(FC, F)
        q = (f"A survey of {N} learners found: Male-Tea = {MT}, Male-Coffee = {MC}, "
             f"Female-Tea = {FT}, Female-Coffee = {FC}. "
             f"Calculate the probability that a female learner, chosen at random, prefers coffee.")
        demo = (f"Conditional on females: denominator = female total = {F}.\n"
                f"Female-coffee = {FC}.\n"
                f"P(coffee | female) = {FC}/{F} = {fmt_frac(prob)}.")
        out.append({
            "variant_question": q,
            "expected": fmt_frac(prob),
            "demonstration": demo,
            "memo_marks": [f"1 mark for denominator {F}", f"1 mark for {FC}/{F}", f"1 mark for {fmt_frac(prob)}"],
            "fast_path": "'Given female' → denominator = female total.",
            "fatal_error": "DBE says: Candidates use grand total {N} as denominator. 'Chosen from females' fixes sample space to females.",
            "answer_book_layout": [f"Female total = {F}", f"Female-coffee = {FC}", f"P = {FC}/{F} = {fmt_frac(prob)}"],
            "hack": "'Given X' → X's total is denominator.",
            "trap": "Females only. Not all learners.",
            "presentation": "State conditional group, cell, ratio.",
            "diagram": "required", "diagram_hint": "contingency_table",
        })
    return out


# ============ 11.2 ============
def gen_11_2():
    out = []
    candidates = []
    Ns = [120, 150, 180, 200, 240, 250, 300]
    ps = [Fraction(2,3), Fraction(3,4), Fraction(3,5), Fraction(4,5), Fraction(1,2), Fraction(2,5), Fraction(7,10)]
    ks = [2, 3, 4]
    qs = [Fraction(1,2), Fraction(3,5), Fraction(2,3), Fraction(5,8), Fraction(7,12), Fraction(7,10), Fraction(3,4), Fraction(4,5)]
    for N in Ns:
        for p in ps:
            for k in ks:
                for q in qs:
                    denom = k * p + (1 - p)
                    if denom == 0: continue
                    x = q * N / denom
                    if x.denominator != 1: continue
                    if x <= 0 or x >= N: continue
                    if k * x >= N: continue  # rainy cups should be < N
                    candidates.append((N, p, k, q, int(x)))
    seen = set()
    unique = []
    for c in candidates:
        key = (c[0], c[1], c[2], c[3])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    
    for N, p, k, q, x in unique[:30]:
        rate_pct = f"{p*100:.0f}"
        q_str = fmt_frac(q)
        q_text = (f"{N} people buy either a cup of coffee or a bottle of water. "
                  f"The chance of rain on any given day is {rate_pct}%. "
                  f"The chance of buying coffee on a rainy day is {k} times the chance on a non-rainy day. "
                  f"The probability of a person buying coffee on any given day is {q_str}. "
                  f"Calculate the number of cups of coffee sold on a non-rainy day.")
        weighted = k * p + (1 - p)
        expected_total = q * N
        demo = (f"Let x = coffee cups on a non-rainy day. Rainy-day cups = {k}x.\n"
                f"Expected coffee = P(rain)·({k}x) + P(no rain)·x\n"
                f"= ({fmt_frac(p)})·{k}x + ({fmt_frac(1-p)})·x = {fmt_frac(weighted)}x.\n"
                f"Also: expected coffee = {q_str} × {N} = {fmt_frac(expected_total)}.\n"
                f"Solve: {fmt_frac(weighted)}x = {fmt_frac(expected_total)} → x = {x}.\n"
                f"Answer: {x} cups on a non-rainy day.")
        out.append({
            "variant_question": q_text,
            "expected": f"x = {x}",
            "demonstration": demo,
            "memo_marks": [f"1 mark for P(rain)·({k}x)", f"1 mark for P(no rain)·x",
                           f"1 mark for equation {fmt_frac(weighted)}x = {fmt_frac(expected_total)}",
                           f"1 mark for x = {x}"],
            "fast_path": "Let x = non-rainy cups. Rainy = kx. Weighted sum = total expected. Solve.",
            "fatal_error": "DBE says: Candidates forget the weather weights (write 3x + x = N). The two weather states weight the cup counts.",
            "answer_book_layout": [f"Let x = cups on non-rainy day", f"Rainy = {k}x",
                                    f"({fmt_frac(p)})·{k}x + ({fmt_frac(1-p)})·x = {q_str}·{N}",
                                    f"x = {x}"],
            "hack": "Weather weights the cups. Two states, two weights.",
            "trap": "Not 3x + x = N. Weighted by weather.",
            "presentation": "Define x, weighted sum, solve.",
            "diagram": "required", "diagram_hint": "tree_diagram_rain_coffee",
        })
    return out


# ============ 11.3.2 ============
def gen_11_3_2():
    out = []
    for n in [6, 7, 8, 9, 10, 11, 12]:
        fav_pairs = sum(n - 2 - i for i in range(1, n - 2))
        total_pairs = n * (n - 1)
        prob = Fraction(fav_pairs, total_pairs)
        q = (f"{n} runners compete in a race with no tied finishes. Bongi and Andrew are two "
             f"of the competitors. Calculate the probability that TWO OR MORE runners finish "
             f"after Andrew and before Bongi.")
        demo = (f"If A is at position i, B must be at position i+3 or later (2+ runners between).\n"
                f"Sum valid B positions over A's positions:\n"
                f"  A at 1: {n-3} choices for B\n"
                f"  A at 2: {n-4}\n"
                f"  ...\n"
                f"  A at {n-2}: 1\n"
                f"Total (A,B) pairs = {fav_pairs}.\n"
                f"Total possible (A,B) pairs = {n}·{n-1} = {total_pairs}.\n"
                f"P = {fav_pairs}/{total_pairs} = {fmt_frac(prob)}.")
        out.append({
            "variant_question": q,
            "expected": fmt_frac(prob),
            "demonstration": demo,
            "memo_marks": [f"1 mark for valid B-position sum ({fav_pairs})",
                           f"1 mark for total pairs ({total_pairs})",
                           f"1 mark for {fmt_frac(prob)}"],
            "fast_path": "Count ordered (A,B) pairs, divide by n(n-1).",
            "fatal_error": "DBE says: Candidates count 'B after A' (allows adjacent) or forget the 2+ gap requirement.",
            "answer_book_layout": [f"Valid (A,B) pairs = {fav_pairs}", f"Total pairs = {total_pairs}",
                                    f"P = {fmt_frac(prob)}"],
            "hack": "Gap ≥ 2 means B at A_pos + 3 or later. Sum over A's positions.",
            "trap": "'After' includes adjacency. Question needs 2+ between.",
            "presentation": "Show the sum, then the fraction.",
            "diagram": "required", "diagram_hint": "runners_with_gap",
        })
    return out


def fill(variants, target=30):
    if not variants:
        return []
    result = []
    while len(result) < target:
        result.extend(variants)
    return result[:target]


print("Regenerating 11.1.1, 11.1.2, 11.2, 11.3.2...\n")
for name, fn in [("11.1.1", gen_11_1_1), ("11.1.2", gen_11_1_2),
                  ("11.2", gen_11_2), ("11.3.2", gen_11_3_2)]:
    v = fn()
    v = fill(v, 30)
    try:
        n = write_pool(name, v)
        print(f"  {name}: {n} variants")
    except ValueError as e:
        print(f"  {name}: FAILED — {e}")

print("\n=== VERIFY ===")
for name in ["11.1.1", "11.1.2", "11.2", "11.3.1", "11.3.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:100]}...")
        print(f"     Expected: {v['expected']}")
