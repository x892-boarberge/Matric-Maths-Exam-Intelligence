import json, random, shutil
from pathlib import Path
from datetime import datetime
from fractions import Fraction

SHAPE_DIR = Path("data/processed/tutor/shape_specs")
POOL_DIR = Path("data/processed/tutor/variant_pools")
SHAPE_DIR.mkdir(parents=True, exist_ok=True)

def _fstr(f):
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

def _disp(b):
    return f"{{{b}}}" if "/" in str(b) else str(b)

# ============ SPECS ============

SPECS = {
"functions.log.x_intercept": {
  "shape_id": "functions.log.x_intercept",
  "mental_move": "x-intercept means y=0, so log_b(x)=0, so x=1 (any valid base)",
  "valid_bases": ["2","3","4","5","10","1/2","1/3"],
  "valid_answers": ["(1; 0)"],
  "answer_form": "coordinate",
  "marks_range": [1],
  "valid_phrasings": [
    "Write down the coordinates of A, the x-intercept of f(x) = log_{base}(x).",
    "Determine where f(x) = log_{base}(x) cuts the x-axis.",
    "Find the x-intercept of the graph of f(x) = log_{base}(x).",
    "The graph of f(x) = log_{base}(x) is drawn. Write down the coordinates of its x-intercept."
  ],
  "diagram": "always",
  "fatal_errors": ["Sets x=0 instead of y=0", "Writes (0;1) — confuses intercepts", "Says no x-intercept (thinks log never crosses)"]
},
"functions.log.inverse_equation": {
  "shape_id": "functions.log.inverse_equation",
  "mental_move": "swap x and y, then convert: y=log_b(x) → x=log_b(y) → y=b^x",
  "valid_bases": ["2","3","4","5","10","1/2","1/3"],
  "answer_form": "expression",
  "marks_range": [2],
  "valid_phrasings": [
    "Determine the equation of f⁻¹, the inverse of f(x) = log_{base}(x), in the form y = ...",
    "Write down the equation of f⁻¹ in the form y = ...",
    "Find the equation of the inverse of f(x) = log_{base}(x)."
  ],
  "diagram": "always",
  "fatal_errors": ["Stops after swapping (x = log_b(y))", "Leaves answer in log form", "Gets base wrong"]
},
"functions.log.inverse_asymptote": {
  "shape_id": "functions.log.inverse_asymptote",
  "mental_move": "inverse of log is exponential; horizontal asymptote of b^x is y=0",
  "valid_bases": ["2","3","4","5","10","1/2","1/3"],
  "valid_answers": ["y = 0"],
  "answer_form": "expression",
  "marks_range": [1],
  "valid_phrasings": [
    "Write down the equation of the asymptote of f⁻¹.",
    "Determine the equation of the horizontal asymptote of the inverse function.",
    "Find the equation of the asymptote of the graph of f⁻¹."
  ],
  "diagram": "always",
  "fatal_errors": ["Writes x=0 (that's f's asymptote)", "Writes y=x (confuses with axis of symmetry)", "Says 'none'"]
},
"functions.log.inverse_graph": {
  "shape_id": "functions.log.inverse_graph",
  "mental_move": "draw the exponential curve that is the reflection of the log across y=x",
  "valid_bases": ["2","3","1/2","1/3"],
  "answer_form": "drawing",
  "marks_range": [3, 4],
  "valid_phrasings": [
    "Draw the graph of f⁻¹ on the set of axes provided. Clearly indicate the intercepts with the axes, ONE other point, and the asymptotes.",
    "Sketch the inverse of f(x) = log_{base}(x) on the same set of axes."
  ],
  "diagram": "always",
  "fatal_errors": ["Redraws the log", "Misses the (0;1) y-intercept", "Forgets the y=0 asymptote"]
},
"functions.log.inverse_translation": {
  "shape_id": "functions.log.inverse_translation",
  "mental_move": "translate right means f⁻¹(x-n); bound the range using h(threshold) and asymptote",
  "valid_bases_frac": ["1/2","1/3","1/4","1/5"],
  "answer_form": "inequality",
  "marks_range": [2],
  "valid_phrasings": [
    "h is obtained when f⁻¹ is translated {n} units to the right. Determine the y-values of h where x > {threshold}.",
    "The graph of h is the graph of f⁻¹ translated {n} units to the right. Find the range of h for x > {threshold}."
  ],
  "diagram": "always",
  "fatal_errors": ["Translates left not right", "Uses f not f⁻¹", "Gives single value not range"]
}
}

for shape_id, spec in SPECS.items():
    p = SHAPE_DIR / f"{shape_id}.json"
    p.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Spec written: {p.name}")


# ============ GENERATORS ============

def gen_x_intercept(spec):
    out = []
    combos = [(b, p) for b in spec["valid_bases"] for p in spec["valid_phrasings"]]
    random.shuffle(combos)
    for base, phrasing in combos[:30]:
        q = phrasing.format(base=base)
        b = _disp(base)
        out.append({
            "variant_question": q, "expected": "(1; 0)",
            "demonstration": f"f(x) = log_{b}(x). x-intercept means y = 0: log_{b}(x) = 0. Convert: {b}^0 = x. Since {b}^0 = 1, x = 1. Answer: (1; 0).",
            "memo_marks": ["1 mark for (1; 0)"],
            "fast_path": "The x-intercept of ANY log function is (1; 0). Log of 1 is always 0, regardless of base.",
            "fatal_error": "DBE says: Candidates set x=0 and find the y-intercept instead, or write (0;1) which is backwards.",
            "answer_book_layout": [f"f(x) = log_{b}(x), y = 0", f"log_{b}(x) = 0", f"{b}^0 = x", "x = 1", "Final Answer: (1; 0)"],
            "hack": "The x-intercept of any log function is (1; 0). Log of 1 is always 0 — no matter the base.",
            "trap": "Don't confuse x-intercept (y=0) with y-intercept (x=0). Log functions don't have a y-intercept (x=0 not in domain).",
            "presentation": "State clearly that y = 0 at the x-intercept. Show log_b(1) = 0.",
            "diagram": "required", "diagram_hint": "log_curve_with_x_intercept_marked"
        })
    return out

def gen_inverse_equation(spec):
    out = []
    answer_map = {"2":"y = 2^x","3":"y = 3^x","4":"y = 4^x","5":"y = 5^x","10":"y = 10^x",
                  "1/2":"y = (1/2)^x  (equivalently y = 2^(-x))",
                  "1/3":"y = (1/3)^x  (equivalently y = 3^(-x))"}
    combos = [(b, p) for b in spec["valid_bases"] for p in spec["valid_phrasings"]]
    random.shuffle(combos)
    for base, phrasing in combos[:30]:
        b = _disp(base)
        q = phrasing.format(base=base)
        out.append({
            "variant_question": q, "expected": answer_map[base],
            "demonstration": f"f(x) = log_{b}(x). Let y = log_{b}(x), swap x and y: x = log_{b}(y). Convert to exponential: y = {b}^x.",
            "memo_marks": ["1 mark for swapping x and y", f"1 mark for y = {b}^x"],
            "fast_path": "Inverse of log_b(x) is b^x. Base stays, the log just goes away.",
            "fatal_error": "DBE says: Candidates swap x and y but leave it as x = log_b(y) — that's the setup, not the answer. You must convert.",
            "answer_book_layout": [f"y = log_{b}(x)", "Swap x and y:", f"x = log_{b}(y)", f"Convert: y = {b}^x", f"Final Answer: f⁻¹(x) = {b}^x"],
            "hack": "Swap and convert. Inverse of log_b is b^x. Same base — the log just disappears.",
            "trap": "Don't stop after the swap. The answer needs y = ... form.",
            "presentation": "Show the swap, then the conversion. Both lines earn marks.",
            "diagram": "required", "diagram_hint": "log_and_inverse_symmetry_across_y_equals_x"
        })
    return out

def gen_inverse_asymptote(spec):
    out = []
    combos = [(b, p) for b in spec["valid_bases"] for p in spec["valid_phrasings"]]
    random.shuffle(combos)
    for base, phrasing in combos[:30]:
        b = _disp(base)
        q = phrasing.format(base=base)
        out.append({
            "variant_question": q, "expected": "y = 0",
            "demonstration": f"f(x) = log_{b}(x) has vertical asymptote x = 0. Its inverse f⁻¹(x) = {b}^x has horizontal asymptote y = 0.",
            "memo_marks": ["1 mark for y = 0"],
            "fast_path": "Inverse of log has horizontal asymptote y = 0. Log itself has vertical x = 0 — inverse swaps them.",
            "fatal_error": "DBE says: Candidates write x = 0 (that's f's asymptote). The inverse has y = 0.",
            "answer_book_layout": [f"f(x) = log_{b}(x) has vertical asymptote x = 0", f"f⁻¹(x) = {b}^x has horizontal asymptote y = 0", "Final Answer: y = 0"],
            "hack": "Log: vertical asymptote x=0. Inverse: horizontal asymptote y=0. Reflection swaps them.",
            "trap": "Don't write x = 0. That's f's asymptote. f⁻¹'s is y = 0.",
            "presentation": "State as y = 0. Axis matters.",
            "diagram": "required", "diagram_hint": "log_and_inverse_with_asymptotes_marked"
        })
    return out

def gen_inverse_graph(spec):
    out = []
    pts = {"2":("(1; 2)","(-1; 1/2)"), "3":("(1; 3)","(-1; 1/3)"),
           "1/2":("(1; 1/2)","(-1; 2)"), "1/3":("(1; 1/3)","(-1; 3)")}
    for i in range(30):
        base = spec["valid_bases"][i % len(spec["valid_bases"])]
        b = _disp(base)
        p1, p2 = pts[base]
        phrasing = spec["valid_phrasings"][i % len(spec["valid_phrasings"])]
        q = phrasing.format(base=base)
        out.append({
            "variant_question": q,
            "expected": f"Practice — draw f⁻¹(x) = {b}^x showing (0;1), horizontal asymptote y=0, and one other marked point (e.g. {p1} or {p2}).",
            "demonstration": f"f(x) = log_{b}(x). Inverse: f⁻¹(x) = {b}^x. Draw exponential through (0; 1). Horizontal asymptote y = 0. Mark one other point — {p1} or {p2}.",
            "memo_marks": ["1 mark for exponential curve", "1 mark for y-intercept (0;1)", "1 mark for one other point", "1 mark for asymptote y=0"],
            "fast_path": "Inverse of log is exponential. Always through (0;1). Asymptote y = 0.",
            "fatal_error": "DBE says: Candidates draw the log again. The inverse must be reflected across y = x.",
            "answer_book_layout": ["Mark (0; 1)", f"Draw exponential curve through (0; 1) and {p1}", "Dashed line at y = 0", f"Label f⁻¹(x) = {b}^x"],
            "hack": "Draw exponential. Through (0;1). Asymptote y=0.",
            "trap": "Don't draw the log. That's the same graph. Reflect across y=x.",
            "presentation": "Mark (0;1), one other point, and the asymptote.",
            "practice_only": True,
            "diagram": "required", "diagram_hint": "blank_axes_for_drawing"
        })
    return out

def gen_inverse_translation(spec):
    out = []
    configs = []
    for base in spec["valid_bases_frac"]:
        b = 1 / Fraction(base)
        for n in [3, 4, 5, 6]:
            for k in [3, 4]:
                if n > k:
                    try:
                        bound = int(b) ** (n - k)
                        if bound in [2, 3, 4, 5, 9, 16, 25]:
                            configs.append((base, n, k, bound))
                    except Exception:
                        pass
    random.shuffle(configs)
    for base, n, k, bound in configs[:30]:
        b = _disp(base)
        phrasing = random.choice(spec["valid_phrasings"])
        q = phrasing.format(n=n, threshold=k)
        out.append({
            "variant_question": f"f(x) = log_{b}(x) has inverse f⁻¹(x) = ({base})^x. " + q,
            "expected": f"0 < y < {bound}",
            "demonstration": f"f⁻¹(x) = ({base})^x. Translate {n} right: h(x) = ({base})^(x-{n}). For x > {k}: h({k}) = ({base})^({k}-{n}) = ({base})^({k-n}) = {bound}. As x → ∞, h(x) → 0. Answer: 0 < y < {bound}.",
            "memo_marks": [f"1 mark for h(x) = ({base})^(x-{n})", f"1 mark for 0 < y < {bound}"],
            "fast_path": f"Right translation: subtract inside. Top of range = h({k}). Bottom = 0 (asymptote).",
            "fatal_error": "DBE says: Candidates translate left (f⁻¹(x + n)) or forget the x-range restriction.",
            "answer_book_layout": [f"f⁻¹(x) = ({base})^x", f"h(x) = ({base})^(x-{n})", f"h({k}) = ({base})^({k-n}) = {bound}", "As x → ∞, h(x) → 0", f"Final Answer: 0 < y < {bound}"],
            "hack": "Right translation = f⁻¹(x - n). Top of range = h(threshold). Bottom = asymptote (0).",
            "trap": "Don't translate left. Right means subtract inside: f⁻¹(x - n).",
            "presentation": "Show translated equation first, then evaluate h at x = threshold for the bound.",
            "diagram": "required", "diagram_hint": "log_and_translated_inverse_graphed"
        })
    return out

DISPATCH = {
    "4.2": ("functions.log.x_intercept", gen_x_intercept),
    "4.3": ("functions.log.inverse_equation", gen_inverse_equation),
    "4.4": ("functions.log.inverse_asymptote", gen_inverse_asymptote),
    "4.5": ("functions.log.inverse_graph", gen_inverse_graph),
    "4.6": ("functions.log.inverse_translation", gen_inverse_translation),
}

random.seed(42)
for subq, (shape_id, fn) in DISPATCH.items():
    spec = SPECS[shape_id]
    variants = fn(spec)
    pool_path = POOL_DIR / f"{subq}_pool.json"
    if pool_path.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(pool_path, pool_path.with_suffix(f".json.bak_{ts}"))
    pool_path.write_text(json.dumps(variants, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{subq} ({shape_id}): {len(variants)} variants -> {pool_path.name}")
