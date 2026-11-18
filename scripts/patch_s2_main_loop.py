"""S2: Fix main loop sign-flip detection and add log voice lines."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if 'getattr(g, "matcher", "") == "single_value_mismatch"' in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# 1. Update sign-flip condition
old_cond = 'if misconception and ("SIGN_ERROR" in misconception or "SIGN_FLIP" in misconception):'
new_cond = 'if misconception and ("SIGN_ERROR" in misconception or "SIGN_FLIP" in misconception or getattr(g, "matcher", "") == "single_value_mismatch"):'
if old_cond not in src:
    print("FATAL: sign-flip condition anchor not found")
    sys.exit(1)
src = src.replace(old_cond, new_cond, 1)
print("Patch 1 applied: main loop sign-flip detection extended")

# 2. Add M_LOG_BASE_INVERTED voice line (before the generic else)
old_else = '''                elif misconception == "M_UNITS_IN_ANSWER":
                    print("  Tanaka: Your numbers are right, but you've attached units. In 'solve for x' questions, leave off the units — write just the number. The examiner marks you down for it.")
                else:'''
new_else = '''                elif misconception == "M_UNITS_IN_ANSWER":
                    print("  Tanaka: Your numbers are right, but you've attached units. In 'solve for x' questions, leave off the units — write just the number. The examiner marks you down for it.")
                elif misconception == "M_LOG_BASE_INVERTED":
                    print("  Tanaka: Check your base. The base of the log and the base in the exponent must match. If you invert the base, you must flip the sign of the answer.")
                else:'''
if old_else not in src:
    print("FATAL: voice map anchor not found")
    sys.exit(1)
src = src.replace(old_else, new_else, 1)
print("Patch 2 applied: M_LOG_BASE_INVERTED voice line added")

target.write_text(src, encoding="utf-8")
print("S2 patch applied.")
