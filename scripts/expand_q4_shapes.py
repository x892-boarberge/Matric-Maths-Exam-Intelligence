import json, random, shutil
from pathlib import Path
from datetime import datetime
from fractions import Fraction

SHAPE_DIR = Path("data/processed/tutor/shape_specs")
POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def fmt_power(base_str):
    return f"({base_str})" if "/" in base_str else base_str

# ===== UPDATE 4.3 SPEC =====
p43_spec = SHAPE_DIR / "functions.log.inverse_equation.json"
s43 = json.loads(p43_spec.read_text(encoding="utf-8"))
new_phrasing_43 = [
    "Write down the equation of the graph that is the reflection of f in the line y = x, in the form y = ...",
    "Determine f-inverse(x) if f(x) = log_{base}(x).",
    "If f(x) = log_{base}(x), find f-inverse, the inverse function, in the form y = ...",
    "Write down f-inverse(x) given f(x) = log_{base}(x).",
]
for p in new_phrasing_43:
    if p not in s43["valid_phrasings"]:
        s43["valid_phrasings"].append(p)
p43_spec.write_text(json.dumps(s43, indent=2, ensure_ascii=False), encoding="utf-8")
combos_43 = len(s43["valid_phrasings"]) * len(s43["valid_bases"])
print(f"4.3 spec: {len(s43['valid_phrasings'])} phrasings x {len(s43['valid_bases'])} bases = {combos_43} max")

# ===== UPDATE 4.6 SPEC =====
p46_spec = SHAPE_DIR / "functions.log.inverse_translation.json"
s46 = json.loads(p46_spec.read_text(encoding="utf-8"))
new_phrasing_46 = [
    "The graph of h is the inverse of f, then translated {n} units right. Determine the range of h for x > {threshold}.",
    "f-inverse is translated {n} units horizontally right to give h. Find the y-values of h when x > {threshold}.",
]
for p in new_phrasing_46:
    if p not in s46["valid_phrasings"]:
        s46["valid_phrasings"].append(p)
p46_spec.write_text(json.dumps(s46, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"4.6 spec: {len(s46['valid_phrasings'])} phrasings")

# ===== REGENERATE 4.3 =====
random.seed(42)
answer_map = {
    "2": "y = 2^x", "3": "y = 3^x", "4": "y = 4^x", "5": "y = 5^x", "10": "y = 10^x",
    "1/2": "y = (1/2)^x  (equivalently y = 2^(-x))",
    "1/3": "y = (1/3)^x  (equivalently y = 3^(-x))",
}
variants_43 = []
combos = [(b, p) for b in s43["valid_bases"] for p in s43["valid_phrasings"]]
random.shuffle(combos)
for base, phrasing in combos[:30]:
    bp = fmt_power(base)
    q = phrasing.format(base=base)
    variants_43.append({
        "variant_question": q,
        "expected": answer_map[base],
        "demonstration": f"f(x) = log_{bp}(x). Let y = log_{bp}(x), swap x and y: x = log_{bp}(y). Convert to exponential: y = {bp}^x.",
        "memo_marks": ["1 mark for swapping x and y", f"1 mark for y = {bp}^x"],
        "fast_path": f"Inverse of log_b(x) is b^x. Base stays, the log goes away.",
        "fatal_error": "DBE says: Candidates swap x and y but leave it as x = log_b(y) - that is the setup, not the answer. You must convert to exponential form.",
        "answer_book_layout": [f"y = log_{bp}(x)", "Swap x and y:", f"x = log_{bp}(y)", f"Convert: y = {bp}^x", f"Final Answer: f-inverse(x) = {bp}^x"],
        "hack": "Swap and convert. Inverse of log_b is b^x. Same base, the log just goes away.",
        "trap": "Don't stop after the swap. Answer must be in y = ... form.",
        "presentation": "Show the swap, then the conversion. Both lines earn marks.",
        "diagram": "required",
        "diagram_hint": "log_and_inverse_symmetry_across_y_equals_x",
    })
path_43 = POOL_DIR / "4.3_pool.json"
if path_43.exists():
    shutil.copy(path_43, path_43.with_suffix(f".json.bak_{ts}"))
path_43.write_text(json.dumps(variants_43, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"4.3: {len(variants_43)} variants written")

# ===== REGENERATE 4.6 =====
valid_bounds = {2, 3, 4, 5, 6, 8, 9, 10, 16, 25, 27, 32, 64, 81, 100, 125}
configs = []
for base_str in s46["valid_bases_frac"]:
    b = 1 / Fraction(base_str)
    for n in range(3, 10):
        for k in range(3, 6):
            if n > k:
                try:
                    bound = int(b) ** (n - k)
                    if bound in valid_bounds:
                        configs.append((base_str, n, k, bound))
                except Exception:
                    pass
random.shuffle(configs)
variants_46 = []
for base_str, n, k, bound in configs[:30]:
    bp = fmt_power(base_str)
    phrasing = random.choice(s46["valid_phrasings"])
    q = phrasing.format(n=n, threshold=k, base=base_str)
    variants_46.append({
        "variant_question": f"f(x) = log_{bp}(x). " + q,
        "expected": f"0 < y < {bound}",
        "demonstration": f"f-inverse(x) = ({base_str})^x. Translate {n} right: h(x) = ({base_str})^(x-{n}). For x > {k}: h({k}) = ({base_str})^({k}-{n}) = ({base_str})^({k-n}) = {bound}. As x approaches infinity, h(x) approaches 0. Answer: 0 < y < {bound}.",
        "memo_marks": [f"1 mark for h(x) = ({base_str})^(x-{n})", f"1 mark for 0 < y < {bound}"],
        "fast_path": f"Right translation: subtract inside. Top of range = h({k}). Bottom = asymptote (0).",
        "fatal_error": "DBE says: Candidates translate left or forget the x-range restriction, giving a single value instead of a range.",
        "answer_book_layout": [f"f-inverse(x) = ({base_str})^x", f"h(x) = ({base_str})^(x-{n})", f"h({k}) = ({base_str})^({k-n}) = {bound}", "As x approaches infinity, h(x) approaches 0", f"Final Answer: 0 < y < {bound}"],
        "hack": "Right translation = f-inverse(x - n). Top of range = h(threshold). Bottom = asymptote (0).",
        "trap": "Don't translate left. Right means subtract inside.",
        "presentation": "Show translated equation first, then evaluate h at x = threshold for the bound.",
        "diagram": "required",
        "diagram_hint": "log_and_translated_inverse_graphed",
    })
path_46 = POOL_DIR / "4.6_pool.json"
if path_46.exists():
    shutil.copy(path_46, path_46.with_suffix(f".json.bak_{ts}"))
path_46.write_text(json.dumps(variants_46, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"4.6: {len(variants_46)} variants written")

# ===== VERIFY ALL 5 POOLS =====
print("\n=== VERIFY ALL Q4 POOLS ===")
for name in ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        print(f"\n{name}_pool.json: MISSING")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:3]:
        print(f"  Q: {v['variant_question'][:70]}")
        print(f"     Expected: {v['expected']}")
