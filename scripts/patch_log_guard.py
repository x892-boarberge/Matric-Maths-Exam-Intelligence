"""Fix v26 OSError: add math safety checks for inf/nan."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# v26 math guard" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# Add safety checks to render_log
old_log = '''def render_log(base, x_marked, var_name, out_path):
    # aesthetic fix: smoother curve near asymptote, no artificial clipping mask
    base_f = float(base); x_f = float(x_marked)
    if base_f <= 0 or base_f == 1 or x_f <= 0: return False
    y_marked = float(np.log(x_f) / np.log(base_f))'''

new_log = '''def render_log(base, x_marked, var_name, out_path):
    # aesthetic fix: smoother curve near asymptote, no artificial clipping mask
    base_f = float(base); x_f = float(x_marked)
    if base_f <= 0 or base_f == 1 or x_f <= 0: return False
    y_marked = float(np.log(x_f) / np.log(base_f))
    
    # v26 math guard: prevent matplotlib crash on inf/nan
    if not np.isfinite(x_f) or not np.isfinite(y_marked):
        return False'''

if old_log not in src:
    print("FATAL: render_log anchor not found")
    sys.exit(1)
src = src.replace(old_log, new_log, 1)

target.write_text(src, encoding="utf-8")
print("Math guard applied to render_log")
