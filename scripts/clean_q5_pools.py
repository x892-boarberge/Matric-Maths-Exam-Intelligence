import json, re, shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def clean_math_text(s):
    if not isinstance(s, str):
        return s
    # x - -N → x + N
    s = re.sub(r"\+\s*-(\d+)", r"- \1", s)   # "+ -9" → "- 9"
    s = re.sub(r"-\s*-(\d+)", r"+ \1", s)   # "- -1" → "+ 1"
    # 1x² → x²  (only when coefficient is exactly 1)
    s = re.sub(r"\b1x\^", "x^", s)
    # -1x² → -x²  (when coefficient is -1)
    s = re.sub(r"-1x\^", "-x^", s)
    # x - (negative parenthesis form) - keep but clean
    s = re.sub(r"\^2 \+ -(\d+)", r"^2 - \1", s)
    return s

def clean_recursive(obj):
    if isinstance(obj, str):
        return clean_math_text(obj)
    if isinstance(obj, list):
        return [clean_recursive(x) for x in obj]
    if isinstance(obj, dict):
        return {k: clean_recursive(v) for k, v in obj.items()}
    return obj

for name in ["5.1", "5.2", "5.3.2", "5.4", "5.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    d = clean_recursive(d)
    shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{name}: cleaned")

# Pad 5.4 to 30 with one more verified config
p = POOL_DIR / "5.4_pool.json"
d = json.loads(p.read_text(encoding="utf-8-sig"))
if len(d) < 30:
    # Add one clean config: turning point (4, 9), point (5, 5), a = -4
    # Check: 5 - 9 = -4, (5-4)^2 = 1, a = -4 ✓
    # y = -4(x-4)^2 + 9 = -4(x^2 - 8x + 16) + 9 = -4x^2 + 32x - 55
    extra = {
        "variant_question": "The turning point of f is P(4; 9). The graph also passes through D(5; 5). Show that the equation of f is y = -4x^2 + 32x - 55.",
        "expected": "y = -4x^2 + 32x - 55",
        "demonstration": "Form: y = a(x - h)^2 + k with (h, k) = (4, 9). So y = a(x - 4)^2 + 9. Use D(5, 5): 5 = a(5 - 4)^2 + 9 → 5 - 9 = a(1) → a = -4. Expand: y = -4(x^2 - 8x + 16) + 9 = -4x^2 + 32x - 64 + 9 = -4x^2 + 32x - 55.",
        "memo_marks": ["1 mark for a(x-h)^2 + k form", "1 mark for substitution of D(5; 5)", "1 mark for expanding to y = -4x^2 + 32x - 55"],
        "fast_path": "Turning point → use y = a(x-h)^2 + k. Plug in the other point to find a. Expand.",
        "fatal_error": "DBE says: Candidates use y = ax^2 + bx + c directly and set up 3 simultaneous equations without using the turning point. This wastes time and invites arithmetic errors.",
        "answer_book_layout": ["y = a(x - 4)^2 + 9", "5 = a(5 - 4)^2 + 9", "a = -4", "y = -4(x - 4)^2 + 9", "y = -4x^2 + 32x - 55"],
        "hack": "Turning point is the shortcut. Form y = a(x-h)^2 + k uses it immediately. Then one substitution finds a.",
        "trap": "Remember to expand at the end. The question asks for the form with x² and x terms, not the vertex form.",
        "presentation": "Show the vertex form, the substitution, and the expansion. The expansion is the final mark.",
        "diagram": "required",
        "diagram_hint": "parabola_with_turning_point_and_one_more_point",
    }
    d.append(extra)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"5.4: padded to {len(d)} variants")

print("\n=== FINAL VERIFY ===")
for name in ["5.1", "5.2", "5.3.1", "5.3.2", "5.4", "5.5", "5.6"]:
    p = POOL_DIR / f"{name}_pool.json"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    print(f"\n{name}_pool.json: {len(d)} variants")
    for v in d[:2]:
        print(f"  Q: {v['variant_question'][:85]}")
        print(f"     Expected: {v['expected']}")
