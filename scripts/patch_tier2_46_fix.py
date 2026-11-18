"""Fix 4.6: use _frac parser for fraction bases."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "base_f = _frac(base); shift = _frac(shift_right)" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

old_func = '''def render_log_translated_inverse(base, shift_right, out_path):
    # Renders f(x) = log_b(x) and h(x) = log_b(x - shift_right) for 4.6
    base_f = float(base); shift = float(shift_right)'''

new_func = '''def render_log_translated_inverse(base, shift_right, out_path):
    # Renders f(x) = log_b(x) and h(x) = log_b(x - shift_right) for 4.6
    base_f = _frac(base); shift = _frac(shift_right)'''

if old_func not in src:
    print("FATAL: anchor not found")
    sys.exit(1)

src = src.replace(old_func, new_func, 1)
target.write_text(src, encoding="utf-8")
print("Patch applied: render_log_translated_inverse now uses _frac()")
