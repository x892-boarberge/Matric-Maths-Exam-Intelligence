"""Batch-test the grader against every pool's expected answer.
Diagnostic only — no writes, no modifications.
"""
import sys
from pathlib import Path
# Ensure project root is on sys.path so `import src.tutor...` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json, re
from src.tutor.math_grader import grade

POOL_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "tutor" / "variant_pools"

def test_variant(expected):
    expected_str = str(expected).strip()
    m = re.match(r"^([a-zA-Z])\s*=\s*(.+)$", expected_str)
    if m:
        var, val = m.group(1), m.group(2)
    else:
        var, val = "x", expected_str
    
    forms = [
        ("bare",         expected_str),
        ("var_eq",       f"{var} = {val}"),
        ("multiline",    f"working\n{var} = {val}"),
        ("multiline_bare", f"working\n{val}"),
    ]
    results = {}
    for name, text in forms:
        try:
            r = grade(text, expected_str)
            results[name] = (r.kind.value == "match", r.matcher)
        except Exception as e:
            results[name] = (False, f"EXC:{type(e).__name__}")
    return results

def main():
    header = f"{'Pool':12} {'N':>4} {'bare':>8} {'var_eq':>8} {'multiline':>10} {'multi_bare':>11}  sample_failures"
    print(header)
    print("=" * len(header))
    
    grand = {"bare": [0,0], "var_eq": [0,0], "multiline": [0,0], "multiline_bare": [0,0]}
    failing_pools = []
    total_tested = 0
    
    for pool_file in sorted(POOL_DIR.glob("*_pool.json")):
        pool_name = pool_file.stem.replace("_pool", "")
        try:
            data = json.loads(pool_file.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        
        per_form = {k: [0,0] for k in grand}
        sample_fails = []
        
        for v in data:
            expected = v.get("expected")
            if not expected:
                continue
            total_tested += 1
            res = test_variant(expected)
            for form in per_form:
                passed, matcher = res[form]
                per_form[form][0] += int(passed)
                per_form[form][1] += 1
                grand[form][0] += int(passed)
                grand[form][1] += 1
            
            if not res["multiline"][0] and len(sample_fails) < 2:
                q = str(v.get("variant_question",""))[:70]
                sample_fails.append(f"{q}... expected={expected!r}")
        
        n = per_form["bare"][1]
        if n == 0:
            continue
        
        bare_pct = 100 * per_form["bare"][0] / n
        ml_pct = 100 * per_form["multiline"][0] / n
        flag = " [!]" if (bare_pct < 50 or ml_pct < 50) else ""
        if flag:
            failing_pools.append(pool_name)
        
        def fmt(pair): return f"{pair[0]}/{pair[1]}"
        print(f"{pool_name:12} {n:>4} {fmt(per_form['bare']):>8} {fmt(per_form['var_eq']):>8} {fmt(per_form['multiline']):>10} {fmt(per_form['multiline_bare']):>11}{flag}")
        for s in sample_fails:
            print(f"             -> {s}")
    
    print("=" * len(header))
    print("\nGRAND TOTALS:")
    for form in ("bare", "var_eq", "multiline", "multiline_bare"):
        p, t = grand[form]
        pct = 100 * p / t if t else 0
        print(f"  {form:16} {p:>4}/{t:<4}  ({pct:5.1f}%)")
    print(f"\nTotal variants tested: {total_tested}")
    print(f"Failing pools ({len(failing_pools)}): {', '.join(failing_pools) if failing_pools else 'none'}")

if __name__ == "__main__":
    main()
