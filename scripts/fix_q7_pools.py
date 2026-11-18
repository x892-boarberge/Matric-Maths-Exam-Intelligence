import json, random, shutil, math
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
random.seed(702)

def write_pool(name, variants):
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(variants)

# ===== 7.2 — Annuity due. Generate 400+ configs =====
def gen_7_2():
    configs = []
    for x in [500, 750, 1000, 1250, 1500, 1750, 2000, 2300, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000]:
        for rate in [0.055, 0.062, 0.068, 0.072, 0.078, 0.082, 0.088, 0.095]:
            for ppy in [4, 12]:
                for yrs in [4, 5, 6, 8, 10]:
                    configs.append((x, rate, ppy, yrs))
    random.shuffle(configs)
    out = []
    for x, i_ann, ppy, yrs in configs[:30]:
        i = i_ann / ppy
        n = ppy * yrs
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
    return out

# ===== 7.3.1 + 7.3.2 — generate configs that pass the loan-repayable filter =====
def build_loan_configs():
    configs = []
    for P in [200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1200000, 1500000]:
        for rate in [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]:
            i = rate / 12
            for x_factor in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]:
                x_raw = P * i * x_factor
                x = round(x_raw / 100) * 100  # round to nearest 100
                if x <= P * i * 1.2:  # require meaningful margin
                    continue
                try:
                    inner = 1 - P * i / x
                    if inner <= 0 or inner >= 1:
                        continue
                    n_exact = -math.log(inner) / math.log(1 + i)
                    if 24 < n_exact < 360:
                        configs.append((P, x, rate, 12, n_exact))
                except (ValueError, ZeroDivisionError):
                    continue
    # Dedupe
    seen = set()
    unique = []
    for c in configs:
        key = (c[0], c[1], c[2])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique

LOAN_CONFIGS = build_loan_configs()
print(f"Valid loan configs: {len(LOAN_CONFIGS)}")
random.shuffle(LOAN_CONFIGS)

# 7.3.1
def gen_7_3_1():
    out = []
    for P, x, i_ann, ppy, n_exact in LOAN_CONFIGS[:30]:
        i = i_ann / ppy
        n_months = math.ceil(n_exact)
        rate_pct = f"{i_ann*100:.1f}"
        inner = 1 - P * i / x
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
            "fatal_error": "DBE says: Candidates round to nearest instead of up, or take log of a negative number because the inner term went negative (instalment too small).",
            "answer_book_layout": [f"i = {i:.6f}", f"(1+i)^-n = 1 - {P:,}·{i:.6f}/{x:,} = {inner:.6f}", f"-n·log(1+i) = log({inner:.6f})", f"n = {n_exact:.2f} → {n_months} months (round up)"],
            "hack": "PV formula, isolate the power, take logs. Round UP for payments.",
            "trap": "Log of negative is undefined. If (1 - P·i/x) is negative, the instalment is too small — the loan never ends.",
            "presentation": "Show i, the rearranged formula, the logs, the exact n, and the rounded answer.",
            "diagram": "required", "diagram_hint": "loan_amortisation_timeline",
        })
    return out

# 7.3.2
def gen_7_3_2():
    out = []
    for P, x, i_ann, ppy, n_exact in LOAN_CONFIGS[:30]:
        i = i_ann / ppy
        n_full = math.floor(n_exact)
        if n_full < 1:
            continue
        balance = P * (1 + i) ** n_full - x * ((1 + i) ** n_full - 1) / i
        final_payment = balance * (1 + i)
        if final_payment <= 0:
            continue
        rate_pct = f"{i_ann*100:.1f}"
        q = (f"Rajesh was granted a loan of R{P:,} at {rate_pct}% p.a., compounded monthly. "
             f"He made {n_full} full monthly repayments of R{x:,} each. "
             f"Calculate the value of the final payment to fully repay the loan one month later.")
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
    return out[:30]


print("\nRegenerating...")
for name, fn in [("7.2", gen_7_2), ("7.3.1", gen_7_3_1), ("7.3.2", gen_7_3_2)]:
    n = write_pool(name, fn())
    print(f"  {name}: {n} variants")

print("\n=== FINAL VERIFY ===")
for name in ["7.1", "7.2", "7.3.1", "7.3.2"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:100]}...")
        print(f"     Expected: {v['expected']}")
