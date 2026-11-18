"""Show the exact code for v-handler, q-handler, and elif chain."""
from pathlib import Path

src = Path("scripts/cli_tutor.py").read_text(encoding="utf-8")
lines = src.split("\n")

print("=" * 70)
print("V-HANDLER (main loop)")
print("=" * 70)
for i, ln in enumerate(lines, 1):
    if '"v"' in ln and ("==" in ln or ".lower()" in ln):
        start = max(0, i - 3)
        end = min(len(lines), i + 6)
        for j in range(start, end):
            marker = ">>>" if j == i - 1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j]}")
        print()
        break

print("=" * 70)
print("Q-HANDLER (main loop)")
print("=" * 70)
for i, ln in enumerate(lines, 1):
    if '"q"' in ln and ("==" in ln or ".lower()" in ln) and i < 1200:
        start = max(0, i - 3)
        end = min(len(lines), i + 6)
        for j in range(start, end):
            marker = ">>>" if j == i - 1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j]}")
        print()
        break

print("=" * 70)
print("ELIF CHAIN (search for M_INCOMPLETE_ROOTS)")
print("=" * 70)
for i, ln in enumerate(lines, 1):
    if "M_INCOMPLETE_ROOTS" in ln and "elif" in ln:
        start = max(0, i - 10)
        end = min(len(lines), i + 25)
        for j in range(start, end):
            marker = ">>>" if j == i - 1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j]}")
        print()
        break

print("=" * 70)
print("END")
print("=" * 70)
