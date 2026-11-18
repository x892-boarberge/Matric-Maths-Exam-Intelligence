"""Patch render_diagrams.py — cast Fraction inputs before numpy."""
from pathlib import Path

f = Path("scripts/render_diagrams.py")
src = f.read_text(encoding="utf-8")

# Fix 1: cast x_marked to float inside render_log_curve
old1 = '''def render_log_curve(base, x_marked, var_name, out_path):
    """DBE-exact log curve: f(x) = log_base(x), point (x_marked; y), x-intercept A at (1,0)."""
    base_f = float(base)
    if base_f <= 0 or base_f == 1:
        return False
    
    y_marked = np.log(x_marked) / np.log(base_f)'''

new1 = '''def render_log_curve(base, x_marked, var_name, out_path):
    """DBE-exact log curve: f(x) = log_base(x), point (x_marked; y), x-intercept A at (1,0)."""
    base_f = float(base)
    x_f = float(x_marked)
    if base_f <= 0 or base_f == 1 or x_f <= 0:
        return False
    
    y_marked = float(np.log(x_f) / np.log(base_f))'''

if old1 not in src:
    print("FAIL: render_log_curve signature not found")
    raise SystemExit(1)
src = src.replace(old1, new1, 1)

# Fix 2: all downstream uses of x_marked → x_f (they were assuming it was numeric)
src = src.replace(
    'x_max = max(float(x_marked) * 1.8, 5)',
    'x_max = max(x_f * 1.8, 5)'
)
src = src.replace(
    'ax.plot(float(x_marked), y_marked, "ko", markersize=DBE_STYLE["point_size"])',
    'ax.plot(x_f, y_marked, "ko", markersize=DBE_STYLE["point_size"])'
)
src = src.replace(
    'ax.annotate(f"({int(x_marked) if x_marked == int(x_marked) else x_marked:g}; {var_name})",\n                xy=(float(x_marked), y_marked),\n                xytext=(float(x_marked) + 0.15, y_marked + y_off),',
    'x_disp = int(x_f) if x_f == int(x_f) else x_f\n    ax.annotate(f"({x_disp:g}; {var_name})",\n                xy=(x_f, y_marked),\n                xytext=(x_f + 0.15, y_marked + y_off),'
)

# Fix 3: return parsed Fractions as-is (they get cast inside render_log_curve now)
f.write_text(src, encoding="utf-8")
print(f"Patched {f}")
print(f"Size: {len(src)} bytes")

# Compile
import subprocess
r = subprocess.run(["py", "-m", "py_compile", str(f)], capture_output=True)
print("PASS: compiles" if r.returncode == 0 else f"FAIL: {r.stderr.decode()[:400]}")
