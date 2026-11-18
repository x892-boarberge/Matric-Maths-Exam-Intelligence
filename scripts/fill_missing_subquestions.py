import json, shutil
from pathlib import Path
from datetime import datetime

PB = Path("data/processed/tutor/playbooks")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

# ============================================================================
# Q8.2.2 — Determine dy/dx if y = (2x^4 + 1) / x^2
# Memo: y = 2x^2 + x^-2; dy/dx = 4x - 2x^-3  (4 marks)
# ============================================================================
q8_2_2 = {
    "variant_question": "Determine dy/dx if y = (3x^5 + 4) / x^2.",
    "demonstration": "1. Split the fraction: y = 3x^5/x^2 + 4/x^2 = 3x^3 + 4x^-2.\n2. Differentiate term by term: d/dx(3x^3) = 9x^2; d/dx(4x^-2) = -8x^-3.\n3. Answer: dy/dx = 9x^2 - 8x^-3.",
    "memo_marks": [
        "1 mark for splitting into 3x^3",
        "1 mark for splitting into 4x^-2",
        "1 mark for derivative of first term (9x^2)",
        "1 mark for derivative of second term (-8x^-3)"
    ],
    "fast_path": "Split first. Divide each term of the numerator by the denominator, write exponents as negative powers, then differentiate term by term.",
    "fatal_error": "DBE says: Candidates apply the quotient rule or try to differentiate before splitting, or they forget the negative power rule and derive x^-2 as -2x^-1.",
    "answer_book_layout": [
        "y = (3x^5 + 4) / x^2",
        "y = 3x^3 + 4x^-2",
        "dy/dx = 9x^2 - 8x^-3"
    ],
    "hack": "Split before you differentiate. A quotient rule here is overkill — just divide each top term by x^2 and rewrite with negative exponents, then apply the power rule.",
    "trap": "The trap is forgetting that x^-2 differentiates to -2x^-3, not to -2x^-1. Drop the exponent by 1, then multiply the coefficient by the original exponent.",
    "presentation": "Show the split explicitly on its own line. The marker gives 2 marks for the split before any differentiation happens."
}

# ============================================================================
# Q9.3 — f(x) = x^3 - 8x^2 + 5x + 14; B(2;0); find x where f(x)·f''(x) < 0
# Memo: -1 < x < 2  or  8/3 < x < 7  (4 marks)
# ============================================================================
q9_3 = {
    "variant_question": "Given f(x) = x^3 - 4x^2 - 7x + 10 with x-intercepts at -2, 1, and 5, and B(1;0), determine the values of x for which f(x)·f''(x) < 0.",
    "demonstration": "1. f''(x) = 6x - 8, so f''(x) = 0 at x = 4/3. Sign of f'': negative for x < 4/3, positive for x > 4/3.\n2. Sign of f (leading positive cubic): f < 0 on (-inf, -2) and (1, 5); f > 0 on (-2, 1) and (5, inf).\n3. f·f'' < 0 means f and f'' have opposite signs.\n   - x < -2: f<0, f''<0 → product > 0 (not)\n   - -2 < x < 1: f>0, f''<0 → product < 0 (yes)\n   - 1 < x < 4/3: f<0, f''<0 → product > 0 (not)\n   - 4/3 < x < 5: f<0, f''>0 → product < 0 (yes)\n   - x > 5: f>0, f''>0 → product > 0 (not)\n4. Answer: -2 < x < 1  or  4/3 < x < 5.",
    "memo_marks": [
        "1 mark for x-intercepts identified",
        "1 mark for sign of f''(x) (concavity split at x = 4/3)",
        "1 mark for first interval -2 < x < 1",
        "1 mark for second interval 4/3 < x < 5"
    ],
    "fast_path": "Sign chart. Mark the x-intercepts and the inflection point on a number line. Where f and f'' have opposite signs, the product is negative.",
    "fatal_error": "DBE says: Candidates solve f(x) < 0 or f''(x) < 0 separately and give that as the answer, without remembering that the product is negative only where the signs are opposite.",
    "answer_book_layout": [
        "f''(x) = 6x - 8 = 0 → x = 4/3",
        "f sign: − on (−∞;−2) and (1;5); + on (−2;1) and (5;∞)",
        "f'' sign: − on (−∞;4/3); + on (4/3;∞)",
        "Opposite signs (product < 0): −2 < x < 1  or  4/3 < x < 5"
    ],
    "hack": "Two sign charts, one for f and one for f''. The answer is where they disagree. Don't try to solve f(x)·f''(x) < 0 algebraically — that's a quartic you can't factorise cleanly. Use the signs.",
    "trap": "f and f'' cross zero at different points. f crosses at -2, 1, 5. f'' crosses at 4/3. Get both zero-sets right, then combine.",
    "presentation": "Show the sign of f and the sign of f'' on separate number lines, then read off the intervals where the signs are opposite. Two marks for the two correct intervals."
}

# ============================================================================
# Q9.4 — for which t will y = -11x + t intersect f at 3 distinct points
# Memo: 14 < t < 634/27  (6 marks)
# ============================================================================
q9_4 = {
    "variant_question": "Given f(x) = x^3 - 4x^2 - 7x + 10, for which values of t will y = -7x + t intersect f at 3 distinct points?",
    "demonstration": "1. The line has slope -7. Set f'(x) = -7: 3x^2 - 8x - 7 = -7 → 3x^2 - 8x = 0 → x(3x - 8) = 0 → x = 0 or x = 8/3.\n2. Find t at each tangency point:\n   - At x=0: f(0) = 10. Line: 10 = -7(0) + t → t = 10.\n   - At x=8/3: f(8/3) = -490/27. Line: -490/27 = -7(8/3) + t = -56/3 + t = -504/27 + t → t = 14/27.\n3. For 3 distinct intersections, t must lie strictly between the two tangency t-values.\n4. Answer: 14/27 < t < 10.",
    "memo_marks": [
        "1 mark for setting f'(x) = -7",
        "1 mark for x = 0 or x = 8/3",
        "1 mark for t = 10 (tangency at x=0)",
        "1 mark for t = 14/27 (tangency at x=8/3)",
        "1 mark for identifying the correct range between the two tangency values",
        "1 mark for inequality notation 14/27 < t < 10"
    ],
    "fast_path": "Two tangent lines. Find where the given slope is tangent to f (two points, because f' is quadratic). Compute t at each. The answer is between those two t-values.",
    "fatal_error": "DBE says: Candidates find the two t values and hand them in as the answer. The question asks for t BETWEEN the tangencies — where the line cuts through f in three places. Below or above, only one intersection.",
    "answer_book_layout": [
        "Slope of line = -7, so set f'(x) = -7",
        "3x^2 - 8x - 7 = -7",
        "3x^2 - 8x = 0 → x = 0 or x = 8/3",
        "At x=0: f(0) = 10 → t = 10",
        "At x=8/3: f(8/3) = -490/27 → t = 14/27",
        "Three distinct points: 14/27 < t < 10"
    ],
    "hack": "Two tangencies, one answer. When a straight line meets a cubic, the number of intersection points depends on how high the line sits. At the two heights where it's tangent, the count changes. Between those heights, you get 3 points.",
    "trap": "Don't stop at the two t-values. Those give tangency (2 intersections, one doubled). The answer is the open interval strictly between them.",
    "presentation": "Show f'(x) = -7, then each tangency substitution, then the interval. The interval notation is the final mark."
}

# ============================================================================
# Q11.2 — 120 people, coffee or water; P(rain)=75%, coffee on rainy = 3× non-rainy
# Memo: x = 28 cups (4 marks)
# ============================================================================
q11_2 = {
    "variant_question": "120 people buy either a cup of coffee or a bottle of water. The chance of rain on any given day is 75%. The chance of buying coffee on a rainy day is three times the chance of buying coffee on a non-rainy day. The probability of a person buying coffee on any given day is 5/8. Calculate the number of cups of coffee that will be sold on a non-rainy day.",
    "demonstration": "Let x = number of cups of coffee sold on a non-rainy day. Then 3x = cups on a rainy day.\nExpected coffee = P(rain)·(3x) + P(no rain)·(x) = 3/4·3x + 1/4·x = 9x/4 + x/4 = 10x/4 = 5x/2.\nGiven probability of coffee = 5/8, so expected coffee = (5/8)·120 = 75.\n5x/2 = 75 → x = 30.\nAnswer: 30 cups of coffee on a non-rainy day.",
    "memo_marks": [
        "1 mark for P(rain)·(3x)",
        "1 mark for P(no rain)·(x)",
        "1 mark for setting the sum equal to (5/8)·120",
        "1 mark for x = 30"
    ],
    "fast_path": "Let x be the answer (non-rainy cups). Rainy = 3x. Expected coffee = P(rain)·rainy + P(no rain)·non-rainy. Set equal to total-p(coffee)·total-people. Solve.",
    "fatal_error": "DBE says: Candidates multiply the probability of rain by the number of cups instead of using probabilities as weights. Or they set 3x + x = total and forget the P(rain) vs P(no rain) split.",
    "answer_book_layout": [
        "Let x = cups of coffee on a non-rainy day",
        "Then rainy day cups = 3x",
        "(3/4)(3x) + (1/4)(x) = (5/8)(120)",
        "9x/4 + x/4 = 75",
        "10x/4 = 75 → x = 30",
        "Final: 30 cups of coffee on a non-rainy day"
    ],
    "hack": "Weight by the weather. Rainy cups count 3/4 of the time, non-rainy cups count 1/4 of the time. That gives you a single equation in x.",
    "trap": "The two weather states multiply the cup counts, not the totals. Don't say 3x + x = 120. Write the weighted sum.",
    "presentation": "Define x explicitly. Show the weighted sum. Solve for x. The 4 marks come from the two weighted terms, the equation, and the answer."
}

# ============================================================================
# Q11.3.1 — 8 runners, Bongi immediately after Andrew
# Memo: 7! = 5040 (2 marks)
# ============================================================================
q11_3_1 = {
    "variant_question": "Ten runners compete in a race where there are no tied finishes. Bongi and Andrew are two of the competitors. Calculate the total number of possible ways in which the 10 runners can finish the race if Bongi finishes in a position immediately after Andrew.",
    "demonstration": "Treat the pair [Andrew, Bongi] as ONE block (Bongi always immediately after Andrew, in that fixed order).\nThat block plus the other 8 runners = 9 items total.\nArrange 9 items in a row: 9! = 362880.\nAnswer: 362880.",
    "memo_marks": [
        "1 mark for treating the pair as one block (9! setup)",
        "1 mark for 9! = 362880"
    ],
    "fast_path": "B immediately after A means one block. n runners → (n-1) blocks → (n-1)!.",
    "fatal_error": "DBE says: Candidates multiply by 2 for 'two orderings' when the question specifies 'Bongi after Andrew'. The order is fixed — no factor of 2.",
    "answer_book_layout": [
        "Treat [Andrew, Bongi] as one block (Bongi immediately after)",
        "Block + 8 other runners = 9 items",
        "9! = 362880",
        "Answer: 362880"
    ],
    "hack": "A pair that must stay together is a block. A pair with a fixed internal order is a block with no extra multiplication.",
    "trap": "The phrase 'Bongi after Andrew' locks the order. Don't multiply by 2. That's for 'adjacent in any order'.",
    "presentation": "State the block, count the items, factorial, done."
}

# ============================================================================
# Q11.3.2 — 8 runners, P(2+ runners finish after A and before B)
# Memo: 15/56 (4 marks)
# ============================================================================
q11_3_2 = {
    "variant_question": "Ten runners compete in a race with no tied finishes. Bongi and Andrew are two of the competitors. Calculate the probability that TWO OR MORE runners finish the race after Andrew and before Bongi.",
    "demonstration": "Count favourable arrangements. If Andrew is at position i, Bongi must be at position i+3 or later (2+ runners between).\n- A at pos 1: B at 4-10 → 7 choices, 8! arrangements each\n- A at pos 2: B at 5-10 → 6\n- A at pos 3: B at 6-10 → 5\n- A at pos 4: B at 7-10 → 4\n- A at pos 5: B at 8-10 → 3\n- A at pos 6: B at 9,10 → 2\n- A at pos 7: B at 10 → 1\n- A at pos 8+ → 0\nTotal = (7+6+5+4+3+2+1)·8! = 28·8!\nP = 28·8! / 10! = 28/90 = 14/45.",
    "memo_marks": [
        "1 mark for identifying that B must be 3+ positions after A",
        "1 mark for the sum 7+6+5+4+3+2+1 = 28 (or equivalent list of cases)",
        "1 mark for numerator 28·8!",
        "1 mark for final answer 14/45 (or 28/90)"
    ],
    "fast_path": "Count positions of A, then valid positions of B (must be 2+ runners between them), then 8! arrangements of the rest. Sum the cases.",
    "fatal_error": "DBE says: Candidates count 'Bongi after Andrew' (which includes adjacent) or 'any Bongi position' — the question requires 2+ runners between. Off-by-one in the gap.",
    "answer_book_layout": [
        "B at least 3 positions after A (2 runners between)",
        "A at pos 1 → B at pos 4-10: 7 ways",
        "A at pos 2 → B at pos 5-10: 6 ways",
        "... continuing ...",
        "Total favourable: (7+6+5+4+3+2+1)·8! = 28·8!",
        "P = 28·8!/10! = 28/90 = 14/45"
    ],
    "hack": "Fix Andrew, count Bongi's valid positions, multiply by 8! for the others. Sum over all valid Andrew positions.",
    "trap": "The gap matters. 'Bongi after Andrew' allows adjacency (gap 0). The question needs gap ≥ 2 runners. That means B's position is at least 3 after A's.",
    "presentation": "Show at least 3 cases of the summation to earn the method mark. State the total favourable count and total arrangements (10!) before computing P."
}

# ============================================================================
# INSERT
# ============================================================================

to_insert = {
    "2025_P1_Q8.json": {"8.2.2": q8_2_2},
    "2025_P1_Q9.json": {"9.3": q9_3, "9.4": q9_4},
    "2025_P1_Q11.json": {"11.2": q11_2, "11.3.1": q11_3_1, "11.3.2": q11_3_2},
}

for fname, additions in to_insert.items():
    path = PB / fname
    backup = path.with_suffix(f".json.bak_{ts}")
    shutil.copy(path, backup)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    existing = set(data.get("subquestions", {}).keys())
    added = []
    for key, val in additions.items():
        if key in existing:
            print(f"  {fname}: {key} already exists, skipping")
            continue
        data["subquestions"][key] = val
        added.append(key)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{fname}: +{added}  (backup: {backup.name})")

print("\n=== FINAL SUBQUESTION COUNTS ===")
expected = {"Q8": 3, "Q9": 4, "Q11": 5}
for fname in sorted(PB.glob("2025_P1_Q*.json")):
    d = json.loads(fname.read_text(encoding="utf-8-sig"))
    n = len(d.get("subquestions", {}))
    key = fname.stem.replace("2025_P1_", "")
    exp = expected.get(key)
    status = "" if exp is None else ("✓" if n == exp else f"(expected {exp})")
    print(f"  {fname.name}: {n} subqs {status}")
