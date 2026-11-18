import json, random, shutil
from pathlib import Path
from datetime import datetime
from fractions import Fraction

SHAPE_DIR = Path("data/processed/tutor/shape_specs")
POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def write_json(p, data):
    Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def fmt(b):
    return f"{{{b}}}" if "/" in str(b) else str(b)

# ===== FIX A: Regenerate 4.1 =====
spec_41 = read_json(SHAPE_DIR / "functions.log.find_unknown.json")

def power_of(base, exp):
    try:
        return Fraction(base) ** exp
    except (ValueError, ZeroDivisionError):
        return None

triples = []
for base in spec_41["valid_bases"]:
    for ans in spec_41["valid_answers"]:
        arg = power_of(base, ans)
        if arg is None:
            continue
        arg_str = str(arg.numerator) if arg.denominator == 1 else f"{arg.numerator}/{arg.denominator}"
        if arg_str in spec_41["valid_arguments"]:
            triples.append((base, arg_str, ans))

print(f"4.1: {len(triples)} valid triples")
random.seed(42)
random.shuffle(triples)
variants_41 = []
for base, x_str, ans in triples[:30]:
    b = fmt(base)
    var = random.choice(spec_41["valid_variable_names"])
    phrasing = random.choice(spec_41["valid_phrasings"])
    q = phrasing.format(x=x_str, var=var, base=base)
    if "/" in base:
        demo = f"{var} = log_{{{base}}}({x_str}). Raise both sides to base {base}: ({base})^{var} = ({base})^(log_{{{base}}}({x_str})). Log and base cancel: ({base})^{var} = {x_str}. Since {x_str} = ({base})^({ans}), {var} = {ans}."
    else:
        demo = f"{var} = log_{base}({x_str}). Raise both sides to base {base}: {base}^{var} = {base}^(log_{base}({x_str})). Log and base cancel: {base}^{var} = {x_str}. Since {x_str} = {base}^{ans}, {var} = {ans}."
    variants_41.append({
        "variant_question": q, "expected": f"{var} = {ans}", "demonstration": demo,
        "memo_marks": [f"1 mark for {b}^{var} = {x_str}", f"1 mark for {var} = {ans}"],
        "fast_path": "Raise both sides to the base. The log cancels the base, so whatever was inside comes out alone.",
        "fatal_error": "DBE says: Candidates stay in log form and guess. Raise both sides to the base, cancel, solve the exponential.",
        "answer_book_layout": [f"{var} = log_{b}({x_str})", "Raise both sides to the base", "Log and base cancel", f"Final Answer: {var} = {ans}"],
        "hack": "A log and its base are a team. Raise both sides to the base, they cancel.",
        "trap": "Don't stay in log form. Convert first, solve.",
        "presentation": "Show the base-raise explicitly.",
        "diagram": "required", "diagram_hint": "log_curve_with_marked_point",
    })

path_41 = POOL_DIR / "4.1_pool.json"
if path_41.exists():
    shutil.copy(path_41, path_41.with_suffix(f".json.bak_{ts}"))
write_json(path_41, variants_41)
print(f"4.1: {len(variants_41)} variants written")

# ===== FIX B: 4.4 with distinct phrasings =====
spec_44_path = SHAPE_DIR / "functions.log.inverse_asymptote.json"
spec_44 = read_json(spec_44_path)
spec_44["valid_phrasings"] = [
    "For f(x) = log_{base}(x), write down the equation of the asymptote of f-inverse.",
    "The function f(x) = log_{base}(x) is given. Determine the equation of the horizontal asymptote of the inverse function.",
    "Given f(x) = log_{base}(x), find the equation of the asymptote of the graph of f-inverse.",
    "For the function f(x) = log_{base}(x), write down the asymptote of f-inverse.",
]
write_json(spec_44_path, spec_44)
print(f"4.4 spec: {len(spec_44['valid_phrasings'])} phrasings")

combos_44 = [(b, p) for b in spec_44["valid_bases"] for p in spec_44["valid_phrasings"]]
random.shuffle(combos_44)
variants_44 = []
for base, phrasing in combos_44[:28]:
    b = fmt(base)
    q = phrasing.format(base=base)
    variants_44.append({
        "variant_question": q, "expected": "y = 0",
        "demonstration": f"f(x) = log_{b}(x) has vertical asymptote x = 0. Its inverse f-inverse(x) = {b}^x has horizontal asymptote y = 0.",
        "memo_marks": ["1 mark for y = 0"],
        "fast_path": "Inverse of log has horizontal asymptote y = 0. Log has vertical x = 0 — reflection swaps them.",
        "fatal_error": "DBE says: Candidates write x = 0 (that's f's asymptote). The inverse has y = 0.",
        "answer_book_layout": [f"f(x) = log_{b}(x): vertical asymptote x = 0", f"f-inverse(x) = {b}^x: horizontal asymptote y = 0", "Final Answer: y = 0"],
        "hack": "Log: x = 0. Inverse: y = 0. Reflection swaps them.",
        "trap": "Don't write x = 0.",
        "presentation": "State as y = 0. Axis matters.",
        "diagram": "required", "diagram_hint": "log_and_inverse_with_asymptotes_marked",
    })

path_44 = POOL_DIR / "4.4_pool.json"
if path_44.exists():
    shutil.copy(path_44, path_44.with_suffix(f".json.bak_{ts}"))
write_json(path_44, variants_44)
print(f"4.4: {len(variants_44)} variants written")

# ===== FIX C: Clean formatting in 4.5, 4.6 =====
for name in ["4.5", "4.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = read_json(p)
    for v in d:
        for field in ["variant_question", "demonstration"]:
            if field in v and isinstance(v[field], str):
                v[field] = v[field].replace("{1/2}", "(1/2)").replace("{1/3}", "(1/3)").replace("{1/4}", "(1/4)").replace("{1/5}", "(1/5)")
                v[field] = v[field].replace("log_(1/", "log_{1/")
    write_json(p, d)
    print(f"{name}: cleaned formatting")

print("\n=== FINAL VERIFY ===")
for name in ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = read_json(p)
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:3]:
        print(f"  Q: {v['variant_question'][:75]}")
        print(f"     Expected: {v['expected']}")
