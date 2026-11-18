"""Fix q menu pass-through + v dispatch."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

# FIX 1 — subquestion handler: pass strings through before .steps
old_block = '''        if submission is None:
            return

        learner_lines = [s.raw_text for s in submission.steps]'''

new_block = '''        if submission is None:
            return None
        if isinstance(submission, str):
            # propagate MENU / QUIT / RETRY signals upward
            return submission

        learner_lines = [s.raw_text for s in submission.steps]'''

if old_block not in src:
    print("FATAL: subquestion handler anchor not found")
    sys.exit(1)
if src.count(old_block) != 1:
    print(f"FATAL: anchor count = {src.count(old_block)} (expected 1)")
    sys.exit(1)
src = src.replace(old_block, new_block, 1)
print("Fix 1 applied: subquestion handler passes string signals through")

# FIX 2 — v returns RETRY (which already triggers variant practice at dispatch)
old_v = '''        if low == "v":
            # universal refinement: allow variants on demand
            return "VARIANT"'''

new_v = '''        if low == "v":
            # universal refinement: return RETRY, which triggers variant practice
            # via the _variant_practice_this_subq flag at the dispatch level
            return "RETRY"'''

if old_v not in src:
    print("WARN: v-handler anchor not found (may already be retry)")
else:
    src = src.replace(old_v, new_v, 1)
    print("Fix 2 applied: v-handler returns RETRY")

target.write_text(src, encoding="utf-8")
print(f"File: {target}")
