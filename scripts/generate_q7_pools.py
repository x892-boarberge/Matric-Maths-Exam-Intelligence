import json, random, shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
random.seed(701)

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)

# ===== 7.1 Compound growth (find FV) =====
def gen_7_1():
    out = []
    # (PV, rate, years)
    configs = [
        (40000, 0.078, 5), (25000, 0.065, 8), (15000, 0.092, 6),
        (80000, 0.055, 10), (12000, 0.081, 7), (50000, 0.072, 4),
        (30000, 0.088, 9), (20000, 0.062, 12), (60000, 0.075, 3),
        (100000, 0.058, 6), (45000, 0.09, 5), (35000, 0.07, 8),
        (22000, 0.084, 7), (18000, 0.095, 4), (70000, 0.065, 10),
        (55000, 0.082, 6), (28000, 0.075, 5), (42000, 0.068, 9),
        (33000, 0.086, 3), (48000, 0.072, 11), (25000, 0.078, 12),
        (15000, 0.068, 15), (110000, 0.06, 5), (95000, 0.074, 4),
        (40000, 0.085, 7), (60000, 0.055, 8), (85000, 0.063, 6),
        (30000, 0.098, 5), (70000, 0.07, 3), (12000, 0.078, 10),
    ]
    for i, (pv, i_val, n) in enumerate(configs):
        # FV = PV(1+i)^n
        fv = pv * (1 + i_val) ** n
        rate_pct = f"{i_val*100:.1f}"
        q = f"A holiday to a certain destination costs R{pv:,} now. The company predicts that the cost will increase by {rate_pct}% per annum. What will this holiday cost in {n} years' time?"
        out.append({
            "variant_question": q,
            "expected": f"R{fv:,.2f}",
            "demonstration": f"FV = PV(1+i)^n\n= {pv:,}(1 + {i_val})^{n}\n= {pv:,}({1+i_val:.6f})^{n}\n= R{fv:,.2f}",
            "memo_marks": [f"1 mark for substitution into FV formula", f"1 mark for R{fv:,.2f}"],
            "fast_path": "Growth means FV. Multiply PV by (1+i)^n. Round only at the end.",
            "fatal_error": "DBE says: Candidates swap FV and PV, or round the rate mid-calculation. Keep the full rate in your calculator.",
            "answer_book_layout": [f"FV = {pv:,}(1 + {rate_pct}/100)^{n}", f"FV = R{fv:,.2f}"],
            "hack": "Growth = FV formula. Value at future date = current value × (1 + rate)^years.",
            "trap": "Rate must stay in decimal form throughout. Don't round 0.078 to 0.08.",
            "presentation": "Show the formula, the substitution, the answer. Round at the end.",
            "diagram": "required", "diagram_hint": "growth_curve_over_time",
        })
    random.shuffle(out)
    return out[:30]

# ===== 7.2 Annuity due (FV of deposits at beginning) =====
def gen_7_2():
    out = []
    # (x, i_annual, periods_per_year, years)
    configs = [
        (2300, 0.058, 4, 6), (1500, 0.075, 12, 5), (800, 0.062, 12, 8),
        (5000, 0.068, 4, 10), (1200, 0.055, 12, 7), (3000, 0.072, 12, 4),
        (2500, 0.065, 4, 6), (1800, 0.08, 12, 9), (4000, 0.06, 4, 5),
        (1000, 0.058, 12, 10), (3500, 0.075, 12, 3), (2200, 0.07, 4, 7),
        (1600, 0.085, 12, 6), (2800, 0.062, 4, 8), (900, 0.09, 12, 5),
        (4200, 0.065, 12, 4), (1400, 0.072, 4, 9), (2600, 0.058, 12, 7),
        (3800, 0.078, 12, 6), (1100, 0.088, 4, 5),
    ]
    for x, i_ann, ppy, yrs in configs:
        i = i_ann / ppy
        n = ppy * yrs
        # Annuity due: FV_due = x · [(1+i)^n - 1]/i · (1+i)
        fv_ord = x * ((1 + i) ** n - 1) / i
        fv_due = fv_ord * (1 + i)
        rate_pct = f"{i_ann*100:.1f}"
        freq = {4: "quarter", 12: "month"}[ppy]
        q = (f"Sarah opened a savings account that pays {rate_pct}% p.a., compounded "
             f"{'quarterly' if ppy==4 else 'monthly'}. She deposited R{x:,} into the account on 1 January "
             f"2020 and continued to make deposits of R{x:,} at the beginning of each {freq} thereafter. "
             f"She made her last deposit on 1 October 2025. Calculate the accumulated amount in the "
             f"account on 1 January 2026.")
        out.append({
            "variant_question": q,
            "expected": f"R{fv_due:,.2f}",
            "demonstration": f"Annuity due (deposits at beginning):\nFV = x·[(1+i)^n - 1]/i · (1+i)\n= {x:,}·[(1 + {i_ann}/{ppy})^{n} - 1]/({i_ann}/{ppy}) · (1 + {i_ann}/{ppy})\n= R{fv_due:,.2f}",
            "memo_marks": [f"1 mark for i = {i_ann}/{ppy}", f"1 mark for n = {n}", f"1 mark for substitution", f"1 mark for R{fv_due:,.2f}"],
            "fast_path": "Annuity due = ordinary annuity × (1+i). The extra factor is for the extra compounding period.",
            "fatal_error": "DBE says: Candidates use ordinary annuity formula (without ×(1+i)) when deposits are at the beginning. Read 'beginning of each month' carefully.",
            "answer_book_layout": [f"i = {i_ann}/{ppy}", f"n = {ppy} × {yrs} = {n}", f"FV_due = {x:,}·[(1+i)^n - 1]/i · (1+i)", f"= R{fv_due:,.2f}"],
            "hack": "Beginning of period → annuity due. End of period → ordinary. Annuity due = ordinary × (1+i).",
            "trap": "The ×(1+i) is the extra compounding on the first deposit.",
            "presentation": "State the type (annuity due), i, n, formula, answer.",
            "diagram": "required", "diagram_hint": "annuity_due_timeline",
        })
    random.shuffle(out)
    return out[:30]

# ===== 7.3.1 Solve for n (time to repay) =====
def gen_7_3_1():
    out = []
    # (P, x, i_annual, ppy)
    configs = [
        (900000, 10000, 0.068, 12), (500000, 5500, 0.12, 12),
        (750000, 8500, 0.095, 12), (250000, 3500, 0.11, 12),
        (400000, 4500, 0.10, 12), (1000000, 12000, 0.075, 12),
        (600000, 6500, 0.085, 12), (350000, 4200, 0.093, 12),
        (800000, 9500, 0.072, 12), (450000, 5800, 0.082, 12),
        (300000, 3500, 0.125, 12), (950000, 11000, 0.062, 12),
        (550000, 6000, 0.088, 12), (720000, 8500, 0.078, 12),
        (380000, 5000, 0.095, 12), (900000, 10000, 0.058, 12),
        (280000, 3000, 0.13, 12), (680000, 7500, 0.08, 12),
        (450000, 5200, 0.105, 12), (880000, 10500, 0.07, 12),
    ]
    for P, x, i_ann, ppy in configs:
        import math
        i = i_ann / ppy
        # PV = x[1 - (1+i)^-n]/i  →  solve for n
        # n = -log(1 - P·i/x) / log(1+i)
        try:
            inner = 1 - P * i / x
            if inner <= 0:
                continue
            n_exact = -math.log(inner) / math.log(1 + i)
        except (ValueError, ZeroDivisionError):
            continue
        n_months = math.ceil(n_exact)
        rate_pct = f"{i_ann*100:.1f}"
        q = (f"The bank granted Rajesh a loan of R{P:,} on 28 February 2024 at an interest rate of "
             f"{rate_pct}% p.a., compounded monthly. Rajesh was unable to make the first three payments. "
             f"He made his first repayment of R{x:,} on 30 June 2024. He continued to make monthly repayments "
             f"of R{x:,} at the end of each month thereafter. How long, in completed months, will it take "
             f"Rajesh to repay the loan from the time the loan was granted?")
        out.append({
            "variant_question": q,
            "expected": f"{n_months} months",
            "demonstration": f"i = {rate_pct}/100/12 = {i:.6f}. Use PV formula: P = x[1 - (1+i)^-n]/i.\nRearranging: (1+i)^-n = 1 - P·i/x = 1 - {P:,}·{i:.6f}/{x:,} = {inner:.6f}.\nTake logs: -n·log(1+i) = log({inner:.6f}). n = -log({inner:.6f})/log({1+i:.6f}) = {n_exact:.2f}.\nRound UP (you can't make a fraction of a payment). Answer: {n_months} months.",
            "memo_marks": [f"1 mark for i = {i:.6f}", f"1 mark for formula setup", f"1 mark for logs applied", f"1 mark for n = {n_exact:.2f}", f"1 mark for rounded up to {n_months}"],
            "fast_path": "PV formula → isolate (1+i)^-n → take logs → solve. Round UP.",
            "fatal_error": "DBE says: Candidates round to nearest (180.1 → 180, should be 181) or take log of negative number because inner term went negative (loan can't be repaid with that instalment).",
            "answer_book_layout": [f"i = {i:.6f}", f"(1+i)^-n = 1 - {P:,}·{i:.6f}/{x:,}", f"-n·log(1+i) = log({inner:.6f})", f"n = {n_exact:.2f} → {n_months} months (round up)"],
            "hack": "PV formula, isolate the power, take logs. Round UP for payments.",
            "trap": "Log of negative is undefined. If (1 - P·i/x) is negative, the instalment is too small — the loan never ends.",
            "presentation": "Show i, the rearranged formula, the logs, the exact n, and the rounded answer.",
            "diagram": "required", "diagram_hint": "loan_amortisation_timeline",
        })
    random.shuffle(out)
    return out[:30]

# ===== 7.3.2 Final payment =====
def gen_7_3_2():
    out = []
    # Same configs as 7.3.1
    configs = [
        (900000, 10000, 0.068, 12), (500000, 5500, 0.12, 12),
        (750000, 8500, 0.095, 12), (250000, 3500, 0.11, 12),
        (400000, 4500, 0.10, 12), (1000000, 12000, 0.075, 12),
        (600000, 6500, 0.085, 12), (350000, 4200, 0.093, 12),
        (800000, 9500, 0.072, 12), (450000, 5800, 0.082, 12),
    ]
    for P, x, i_ann, ppy in configs:
        import math
        i = i_ann / ppy
        try:
            inner = 1 - P * i / x
            if inner <= 0:
                continue
            n_exact = -math.log(inner) / math.log(1 + i)
        except (ValueError, ZeroDivisionError):
            continue
        n_full = math.floor(n_exact)
        # Balance after n_full payments:
        balance = P * (1 + i) ** n_full - x * ((1 + i) ** n_full - 1) / i
        # Final payment = balance × (1+i)
        final_payment = balance * (1 + i)
        rate_pct = f"{i_ann*100:.1f}"
        q = (f"Rajesh was granted a loan of R{P:,} at {rate_pct}% p.a., compounded monthly. "
             f"He made {n_full} full monthly repayments of R{x:,} each, ending 1 March 2039. "
             f"Calculate the value of the final payment to fully repay the loan on 1 April 2039.")
        out.append({
            "variant_question": q,
            "expected": f"R{final_payment:,.2f}",
            "demonstration": f"i = {rate_pct}/100/12 = {i:.6f}.\nBalance after {n_full} payments:\nB = P(1+i)^{n_full} - x·[(1+i)^{n_full} - 1]/i\n= {P:,}·(1+{i:.6f})^{n_full} - {x:,}·[(1+{i:.6f})^{n_full} - 1]/{i:.6f}\n= R{balance:,.2f}.\nFinal payment = B × (1+i) = {balance:,.2f} × {1+i:.6f} = R{final_payment:,.2f}.",
            "memo_marks": [f"1 mark for i = {i:.6f}", f"1 mark for balance after {n_full} payments", f"1 mark for final payment R{final_payment:,.2f}"],
            "fast_path": "Find balance after last full payment. Then one more month of interest = final payment.",
            "fatal_error": "DBE says: Candidates hand in the regular instalment as the final answer. Compute the balance first.",
            "answer_book_layout": [f"i = {i:.6f}", f"B = {P:,}(1+i)^{n_full} - {x:,}·[(1+i)^{n_full} - 1]/i", f"B = R{balance:,.2f}", f"Final = B × (1+i) = R{final_payment:,.2f}"],
            "hack": "Balance → ×(1+i) → final payment. The balance already accounts for the last full payment.",
            "trap": "If you don't compute balance, you hand in R{x:,} as your answer — which is the regular instalment, not the final.",
            "presentation": "Show balance formula, balance value, then one more month of interest.",
            "diagram": "required", "diagram_hint": "loan_final_payment_timeline",
        })
    random.shuffle(out)
    return out[:30]


print("Generating Q7 pools...\n")
for name, fn in [("7.1", gen_7_1), ("7.2", gen_7_2), ("7.3.1", gen_7_3_1), ("7.3.2", gen_7_3_2)]:
    n = write_pool(name, fn())
    print(f"  {name}: {n} variants")

print("\n=== VERIFY ===")
for name in ["7.1", "7.2", "7.3.1", "7.3.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:100]}...")
        print(f"     Expected: {v['expected']}")
