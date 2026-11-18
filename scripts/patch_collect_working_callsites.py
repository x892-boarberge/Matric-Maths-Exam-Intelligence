"""patch_collect_working_callsites.py — pass context to both call sites."""
import re
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

if src.count('collect_working(\n            store') >= 1 and \
   src.count('collect_working(\n            store') == src.count("submission = collect_working()") + \
                                                src.count('collect_working(\n            store'):
    # crude idempotency check — count already-patched
    pass

# Check if already patched
if "collect_working(store, learner_id, session_id" in src or \
   "skill_id=getattr(problem" in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)

patched_count = 0

# Call site 1 — Legacy single-attempt loop (line ~624)
ctx1_old = '''        # ---- Legacy single-attempt loop ----
        while True:
            submission = collect_working()
            if submission is None:
                break'''

ctx1_new = '''        # ---- Legacy single-attempt loop ----
        while True:
            submission = collect_working(
                store, learner_id, session_id,
                skill_id=getattr(problem, "skill_id", ""),
                question_id=getattr(problem, "problem_id", ""),
            )
            if submission is None:
                break'''

if ctx1_old in src:
    src = src.replace(ctx1_old, ctx1_new, 1)
    patched_count += 1
    print("  patched call site 1 (Legacy loop, ~line 624)")
else:
    print("  SKIP call site 1 — anchor not found (may already be patched or different)")

# Call site 2 — _run_single_anchor max_attempts loop (line ~772)
ctx2_old = '''    while attempts < max_attempts:
        attempts += 1
        submission = collect_working()
        if submission is None:
            return'''

ctx2_new = '''    while attempts < max_attempts:
        attempts += 1
        submission = collect_working(
            store, learner_id, session_id,
            skill_id=getattr(problem, "skill_id", ""),
            question_id=getattr(problem, "problem_id", ""),
        )
        if submission is None:
            return'''

if ctx2_old in src:
    src = src.replace(ctx2_old, ctx2_new, 1)
    patched_count += 1
    print("  patched call site 2 (_run_single_anchor, ~line 772)")
else:
    print("  SKIP call site 2 — anchor not found (may already be patched or different)")

if patched_count == 0:
    print("No call sites patched.")
    sys.exit(1)

P.write_text(src, encoding="utf-8")
print(f"\nPatched {patched_count} call site(s) in {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
