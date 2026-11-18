"""Diagnose + patch the v-intercept gap at the variant loop.

Finds 'Getting a new variant' in cli_tutor.py, prints surrounding context,
then applies a targeted 'continue' patch if the shape is what we expect.
"""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}\n")

src = target.read_text(encoding="utf-8")
lines = src.split("\n")

# Find the "Getting a new variant" line
hits = [i for i, ln in enumerate(lines) if "Getting a new variant" in ln]
if not hits:
    print("FATAL: 'Getting a new variant' not found in cli_tutor.py")
    sys.exit(1)

print(f"Found {len(hits)} occurrence(s) of 'Getting a new variant'")
print("=" * 70)

# Print context for each occurrence
for h in hits:
    start = max(0, h - 15)
    end = min(len(lines), h + 10)
    print(f"\n--- Context around line {h+1} ---")
    for i in range(start, end):
        marker = ">>>" if i == h else "   "
        print(f"{marker} {i+1:4d}: {lines[i]}")
    print()

# Assess the shape — is there a 'continue' within 8 lines after the print?
print("=" * 70)
print("Diagnosis:")
for h in hits:
    window = lines[h+1:h+10]
    has_continue = any(ln.strip() == "continue" for ln in window)
    has_grading  = any("_vg(" in ln or "_grade(" in ln or "_gv =" in ln for ln in window)
    print(f"  Line {h+1}: continue within 9 lines = {has_continue}, grading within 9 lines = {has_grading}")

# Refuse to auto-patch — write the context to a file so we can decide together
context_out = Path("scripts/_v_intercept_context.txt")
context_out.write_text("\n".join(
    f"{i+1:4d}: {lines[i]}" for i in range(max(0, hits[0]-15), min(len(lines), hits[0]+15))
), encoding="utf-8")
print(f"\nContext written to: {context_out}")
print("Paste that file so I can write the exact anchor patch.")
