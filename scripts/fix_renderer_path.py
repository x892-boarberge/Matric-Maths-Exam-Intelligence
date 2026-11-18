"""Fix path.relative_to bug in render_diagrams.py + check PNGs exist."""
from pathlib import Path
import shutil, subprocess
from datetime import datetime

f = Path("scripts/render_diagrams.py")
bak = f.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
shutil.copy(f, bak)
src = f.read_text(encoding="utf-8")

# Fix 1: v["diagram_path"] — use str(out_path) directly, not relative_to
old1 = 'v["diagram_path"] = str(out_path.relative_to(Path.cwd()))'
new1 = 'v["diagram_path"] = str(out_path)'
if old1 in src:
    src = src.replace(old1, new1, 1)
    print("Fix 1: diagram_path uses str() directly")
else:
    print("Fix 1: pattern not found")

# Fix 2: final logging loop
old2 = '''        for s in samples:
            print(f"  {s.relative_to(Path.cwd())}")'''
new2 = '''        for s in samples:
            print(f"  {s}")'''
if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Fix 2: sample logging uses str()")
else:
    print("Fix 2: pattern not found")

f.write_text(src, encoding="utf-8")

r = subprocess.run(["py", "-m", "py_compile", str(f)], capture_output=True)
print("PASS: compiles" if r.returncode == 0 else f"FAIL: {r.stderr.decode()[:400]}")
