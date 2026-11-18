import json
import shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")

# Step 1: find log pools
found = []
for f in POOL_DIR.glob("*.json"):
    try:
        content = f.read_text(encoding="utf-8")
        if "log_" in content.lower():
            variants = json.loads(content)
            found.append((f, len(variants)))
    except Exception:
        pass

print(f"Found {len(found)} log pool(s):")
for path, count in found:
    print(f"  {path.name}: {count} variants, {path.stat().st_size} bytes")

if len(found) == 0:
    print("\nNo log pool found. Report the pool listing for next step.")
    raise SystemExit(0)
if len(found) > 1:
    print("\nMultiple log pools. Pick one, re-run with explicit filename.")
    raise SystemExit(0)

pool_path, _ = found[0]
print(f"\nProceeding with: {pool_path.name}")

# Step 2: back up
ts = datetime.now().strftime("%Y%m%d%H%M%S")
backup = pool_path.with_suffix(f".json.bak_{ts}")
shutil.copy(pool_path, backup)
print(f"Backup: {backup.name}")

# Shared teaching fields
POS = {
    "fast_path": "Raise both sides to the base. The log cancels the base, so whatever was inside the log comes out alone - and you're left with a normal exponential equation to solve.",
    "fatal_error": "DBE says: Candidates stay stuck in log form and guess. A log is just 'what power?' - raise both sides to the base, watch the log and base cancel, then solve the exponential that's left.",
    "hack": "A log and its base are a team. When you raise both sides to the base, they cancel - and the thing inside the log comes out alone. That's the entire move. log_b(x) = y means b^y = x. Nothing else to memorise.",
    "trap": "Don't stay in log form. The exam wants the answer, not the equation. Convert first, then solve.",
    "presentation": "Show the conversion explicitly. Write 'raise both sides to base B.' Show the exponential equation before you compute.",
}

FRAC = {
    "fast_path": "Raise both sides to the base. The log cancels the base. When the base is a fraction like 1/3, the answer will be negative - the fraction is doing the sign flip for you. Don't panic at the sign.",
    "fatal_error": "DBE says: Candidates get a negative answer from a fraction base and panic - they flip it back to positive, or they write the base itself as the answer. The fraction base guarantees a negative log value. Trust the exponential; it's carrying the sign.",
    "hack": "A log and its base are a team. Raise both sides to the base, they cancel, the thing inside comes out alone. When the base is a fraction, the answer will be negative. The fraction is doing the flip.",
    "trap": "Don't stay in log form, and don't panic at a negative answer from a fraction base. Convert first, trust the sign, solve.",
    "presentation": "Show the conversion. Write 'raise both sides to base 1/3.' The negative answer is correct - fraction base means negative log.",
}


def pos_variant(base, x_str, t_num, t_expr):
    return {
        "variant_question": f"Find t if ({x_str}; t) lies on f(x) = log_{base}(x).",
        "expected": f"t = {t_num}",
        "demonstration": f"t = log_{base}({x_str}). Raise both sides to base {base}: {base}^t = {base}^(log_{base}({x_str})). Log and base cancel: {base}^t = {x_str}. Since {x_str} = {t_expr}, t = {t_num}.",
        "memo_marks": [f"1 mark for {base}^t = {x_str}", f"1 mark for t = {t_num}"],
        "answer_book_layout": [
            f"t = log_{base}({x_str})",
            f"{base}^t = {base}^(log_{base}({x_str}))",
            f"{base}^t = {x_str}",
            f"{base}^t = {t_expr}",
            f"Final Answer: t = {t_num}",
        ],
        **POS,
    }


def frac_variant(base_str, x_str, t_num):
    return {
        "variant_question": f"Find t if ({x_str}; t) lies on f(x) = log_{{{base_str}}}(x).",
        "expected": f"t = {t_num}",
        "demonstration": f"t = log_{{{base_str}}}({x_str}). Raise both sides to base {base_str}: ({base_str})^t = ({base_str})^(log_{{{base_str}}}({x_str})). Log and base cancel: ({base_str})^t = {x_str}. Since {x_str} = ({base_str})^({t_num}), t = {t_num}.",
        "memo_marks": [f"1 mark for ({base_str})^t = {x_str}", f"1 mark for t = {t_num}"],
        "answer_book_layout": [
            f"t = log_{{{base_str}}}({x_str})",
            f"({base_str})^t = ({base_str})^(log_{{{base_str}}}({x_str}))",
            f"({base_str})^t = {x_str}",
            f"({base_str})^t = ({base_str})^({t_num})",
            f"Final Answer: t = {t_num}",
        ],
        **FRAC,
    }


variants = [
    # Positive bases (20)
    pos_variant(2, "8", 3, "2^3"),
    pos_variant(2, "16", 4, "2^4"),
    pos_variant(2, "32", 5, "2^5"),
    pos_variant(2, "1/2", -1, "2^(-1)"),
    pos_variant(2, "1/4", -2, "2^(-2)"),
    pos_variant(3, "9", 2, "3^2"),
    pos_variant(3, "27", 3, "3^3"),
    pos_variant(3, "81", 4, "3^4"),
    pos_variant(3, "1/3", -1, "3^(-1)"),
    pos_variant(3, "1/9", -2, "3^(-2)"),
    pos_variant(5, "25", 2, "5^2"),
    pos_variant(5, "125", 3, "5^3"),
    pos_variant(5, "1/5", -1, "5^(-1)"),
    pos_variant(5, "1/25", -2, "5^(-2)"),
    pos_variant(4, "16", 2, "4^2"),
    pos_variant(4, "64", 3, "4^3"),
    pos_variant(4, "1/4", -1, "4^(-1)"),
    pos_variant(10, "100", 2, "10^2"),
    pos_variant(10, "1000", 3, "10^3"),
    pos_variant(10, "1/10", -1, "10^(-1)"),
    # Fraction bases (10)
    frac_variant("1/2", "2", -1),
    frac_variant("1/2", "4", -2),
    frac_variant("1/2", "8", -3),
    frac_variant("1/2", "1/2", 1),
    frac_variant("1/2", "1/4", 2),
    frac_variant("1/3", "3", -1),
    frac_variant("1/3", "9", -2),
    frac_variant("1/3", "27", -3),
    frac_variant("1/3", "1/3", 1),
    frac_variant("1/3", "1/9", 2),
]

pool_path.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nWrote {len(variants)} clean variants to {pool_path.name}")

# Sanity check: every expected answer is a clean integer
bad = [v for v in variants if not any(v["expected"] == f"t = {n}" for n in [-3, -2, -1, 1, 2, 3, 4, 5])]
if bad:
    print(f"WARN: {len(bad)} variants have non-integer expected answers")
else:
    print("Sanity: all 30 answers are clean integers")
