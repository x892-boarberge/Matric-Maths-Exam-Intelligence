"""patch_collect_working_minimal.py — minimal: signature + ? channel only."""
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

if "?<question>" in src and "capture_question" in src:
    print("Already patched.")
    sys.exit(0)

# 1. Signature
old_sig = 'def collect_working():'
new_sig = ('def collect_working(store=None, learner_id=None, session_id=None,\n'
           '                    skill_id=None, question_id=None):')
if old_sig not in src:
    print("FAIL: collect_working() signature not found")
    sys.exit(1)
src = src.replace(old_sig, new_sig, 1)

# 2. Insert ? channel after the "low = stripped.lower()" line
old_anchor = '''        low = stripped.lower()

        if low in ("q", "quit", "exit"):'''
new_anchor = '''        low = stripped.lower()

        # Question channel (? or /ask) - does NOT count as a working line
        if stripped.startswith("?") or low.startswith("/ask"):
            if store is not None and learner_id:
                try:
                    from src.tutor.conversation import capture_question
                    conv = capture_question(
                        store, learner_id, session_id or "",
                        skill_id=skill_id or "",
                        question_id=question_id or "",
                        question_text=stripped,
                    )
                    if conv and conv.get("answer_text"):
                        print()
                        print(f"  Tanaka: {conv['answer_text']}")
                        print()
                    else:
                        print()
                        print("  Tanaka: Noted. Let's keep going.")
                        print()
                except Exception as _e:
                    print(f"  [question capture failed: {_e}]")
            else:
                print()
                print("  Tanaka: Noted. Let's keep going.")
                print()
            continue

        if low in ("q", "quit", "exit"):'''

if old_anchor not in src:
    print("FAIL: anchor after 'low = stripped.lower()' not found")
    sys.exit(1)
src = src.replace(old_anchor, new_anchor, 1)

# 3. Update the help prompt (optional, cosmetic)
src = src.replace(
    'print("  - Type \'q\' to quit")',
    'print("  - Type \'?<question>\' to ask Tanaka a question")\n    print("  - Type \'q\' to quit")',
    1,
)

P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
else:
    print("py_compile: FAIL")
    print(r.stderr.decode())
    sys.exit(1)
