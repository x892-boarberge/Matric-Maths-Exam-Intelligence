from pathlib import Path
import shutil, subprocess
from datetime import datetime

f = Path("src/tutor/diagnosis.py")
bak = f.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
shutil.copy(f, bak)
print(f"Backup: {bak}")

src = f.read_text(encoding="utf-8")

# Find the start of the broken block
markers = [
    "# SEQUENCES \u2014 TWO ADDITIONAL DBE PATTERNS",
    'SEQ_TEACHINGS["M_SEQ_TERM_VS_VALUE"]',
]
cut_idx = -1
for m in markers:
    idx = src.find(m)
    if idx != -1:
        cut_idx = idx
        break

if cut_idx == -1:
    print("No broken block found — checking compile...")
    r = subprocess.run(["py", "-m", "py_compile", str(f)], capture_output=True)
    print("PASS" if r.returncode == 0 else f"FAIL: {r.stderr.decode()[:300]}")
    raise SystemExit(0)

# Include the preceding "\n\n\n" before the block start
pre = src.rfind("\n\n\n", 0, cut_idx)
start = pre + 1 if pre != -1 else cut_idx

new_content = src[:start].rstrip() + "\n"
f.write_text(new_content, encoding="utf-8")
print(f"Removed {len(src) - len(new_content)} chars")
print(f"New size: {len(new_content)} bytes")

r = subprocess.run(["py", "-m", "py_compile", str(f)], capture_output=True)
if r.returncode == 0:
    print("PASS: file compiles clean")
else:
    print("STILL FAILING:")
    print(r.stderr.decode()[:800])
