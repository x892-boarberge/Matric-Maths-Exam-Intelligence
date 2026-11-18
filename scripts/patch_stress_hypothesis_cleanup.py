"""patch_stress_hypothesis_cleanup.py — make cleanup() schema-safe."""
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "stress_test_hypothesis.py"
src = P.read_text(encoding="utf-8")

old = '''def cleanup():
    conn = sqlite3.connect(HYP_DB)
    try:
        conn.execute("DELETE FROM hypothesis WHERE created_by = ?", (TEST_TAG,))
        conn.commit()
    finally:
        conn.close()'''

new = '''def cleanup():
    conn = sqlite3.connect(HYP_DB)
    try:
        try:
            conn.execute("DELETE FROM hypothesis WHERE created_by = ?", (TEST_TAG,))
            conn.commit()
        except sqlite3.OperationalError:
            pass  # table doesn't exist yet; nothing to clean
    finally:
        conn.close()'''

if new in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)
if old not in src:
    print("FAIL: original cleanup() not found")
    sys.exit(1)

src = src.replace(old, new, 1)
P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
