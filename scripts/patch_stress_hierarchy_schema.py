"""patch_stress_hierarchy_schema.py — move ensure_schema before populate."""
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "stress_test_hierarchy.py"
src = P.read_text(encoding="utf-8")

old = '''    conn = _create_temp_db(temp_db)
    print("Building hierarchy + 1000 learners ...")
    _populate_hierarchy(conn)

    original_db = cohort_nodes.DB
    cohort_nodes.DB = temp_db

    try:
        ensure_schema(conn)
'''

new = '''    conn = _create_temp_db(temp_db)
    ensure_schema(conn)
    print("Building hierarchy + 1000 learners ...")
    _populate_hierarchy(conn)

    original_db = cohort_nodes.DB
    cohort_nodes.DB = temp_db

    try:
'''

if new in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)
if old not in src:
    print("FAIL: expected block not found")
    print("Looking for:")
    print(old[:100])
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
