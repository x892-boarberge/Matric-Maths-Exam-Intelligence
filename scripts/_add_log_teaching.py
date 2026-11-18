"""Content fix: add missing teaching for M_LOG_BASE_INVERTED."""
import sys
from pathlib import Path

target = Path("src/tutor/diagnosis.py")
backup = target.with_suffix(f".py.bak")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if '"M_LOG_BASE_INVERTED":' in src:
    print("FATAL: teaching already exists.")
    sys.exit(1)

# Find the TEACHINGS dict and inject a new entry
# We'll use the exact format from the M_INVERSE_ALWAYS_LOG entry
new_entry = '''"M_LOG_BASE_INVERTED": (
        "You inverted the base, but kept the positive exponent.\\n\\n"
        "  A log and its base are a team. If you invert the base (e.g., 1/3 instead of 3),\\n"
        "  you must also flip the sign of the answer.\\n\\n"
        "  Example: log_{1/3}(3) = -1, not 1.\\n"
        "  Because (1/3)^-1 = 3.\\n\\n"
        "  Check your working: did you flip the sign when you inverted the base?"
    ),
    '''

anchor = '"M_INVERSE_ALWAYS_LOG": ('
if anchor not in src:
    print("FATAL: TEACHINGS anchor not found")
    sys.exit(1)

src = src.replace(anchor, new_entry + anchor, 1)
target.write_text(src, encoding="utf-8")
print("Teaching added: M_LOG_BASE_INVERTED")
