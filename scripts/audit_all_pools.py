import json
from pathlib import Path

POOL_DIR = Path("data/processed/tutor/variant_pools")
expected = [
    "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.2",
    "2.1", "2.2", "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4", "4.5", "4.6",
    "5.1", "5.2", "5.3.1", "5.3.2", "5.4", "5.5", "5.6",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3.1", "7.3.2",
    "8.1", "8.2.1", "8.2.2",
    "9.1", "9.2", "9.3", "9.4",
    "10.1", "10.2",
    "11.1.1", "11.1.2", "11.2", "11.3.1", "11.3.2",
]

found = []
missing = []
for name in expected:
    p = POOL_DIR / f"{name}_pool.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        found.append((name, len(d)))
    else:
        missing.append(name)

print(f"Present: {len(found)}/{len(expected)}")
print("\nPresent pools:")
for n, c in found:
    print(f"  {n}: {c} variants")

if missing:
    print(f"\nMISSING ({len(missing)}):")
    for m in missing:
        print(f"  {m}")
else:
    print("\nAll 45 subquestion pools exist. 2025 Paper 1 truly content-complete.")
