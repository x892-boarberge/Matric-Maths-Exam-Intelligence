import json
data = json.load(open("data/processed/tutor/variant_pools/4.1_pool.json", encoding="utf-8-sig"))
for i, v in enumerate(data, 1):
    q = v.get("variant_question", "")
    if "log_2(1/8)" in q or "log2(1/8)" in q:
        print(f"v{i}: {q[:100]}")
        print(f"  expected = {v.get('expected')!r}")
        print(f"  expected_answer = {v.get('expected_answer')!r}")
        print(f"  full keys: {list(v.keys())}")
        break
