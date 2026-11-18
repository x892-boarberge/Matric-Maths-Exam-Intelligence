"""Fix: variant loop join + honest grade print."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

# Fix 1: newline join (matches main loop, matches math_grader expectations)
p1_old = '_var_text = " ".join(_var_lines)'
p1_new = '_var_text = "\\n".join(_var_lines)'
if p1_old not in src:
    print("FATAL: Patch 1 anchor not found.")
    sys.exit(1)
if src.count(p1_old) != 1:
    print(f"FATAL: Patch 1 anchor count = {src.count(p1_old)} (expected 1)")
    sys.exit(1)
src = src.replace(p1_old, p1_new, 1)
print("Patch 1 applied: newline join")

# Fix 2: honest grade print in variant loop
p2_old = '''                        print()
                        print("  grade:  no_match")
                        print()'''
p2_new = '''                        print()
                        print(f"  grade:  {_gv.kind.value}  ({_gv.matcher})")
                        print()'''
if p2_old not in src:
    print("FATAL: Patch 2 anchor not found.")
    sys.exit(1)
if src.count(p2_old) != 1:
    print(f"FATAL: Patch 2 anchor count = {src.count(p2_old)} (expected 1)")
    sys.exit(1)
src = src.replace(p2_old, p2_new, 1)
print("Patch 2 applied: honest grade print")

target.write_text(src, encoding="utf-8")
print(f"File written: {target}")
