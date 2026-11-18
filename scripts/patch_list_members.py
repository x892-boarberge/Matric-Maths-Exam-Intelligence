"""patch_list_members.py — make conn optional in list_members()."""
import subprocess
import sys
from pathlib import Path

P = Path("src") / "tutor" / "cohort_nodes.py"
src = P.read_text(encoding="utf-8")

old = '''def list_members(node_id, conn):
    return [r[0] for r in conn.execute(
        "SELECT learner_id FROM cohort_membership "
        "WHERE node_id = ? AND left_at IS NULL ORDER BY learner_id",
        (node_id,),
    ).fetchall()]'''

new = '''def list_members(node_id, conn=None):
    close_after = False
    if conn is None:
        conn = sqlite3.connect(DB)
        close_after = True
    try:
        return [r[0] for r in conn.execute(
            "SELECT learner_id FROM cohort_membership "
            "WHERE node_id = ? AND left_at IS NULL ORDER BY learner_id",
            (node_id,),
        ).fetchall()]
    finally:
        if close_after:
            conn.close()'''

if new in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)
if old not in src:
    print("FAIL: original list_members block not found")
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
