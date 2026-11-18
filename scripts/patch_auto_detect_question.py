"""patch_auto_detect_question.py — auto-detect natural questions in collect_working."""
import re
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

if "def _looks_like_natural_question" in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)

# Step 1: insert helper function before 'def collect_working'
helper = '''def _looks_like_natural_question(text):
    """Conservative heuristic: is this a learner question, not a math attempt?

    Only returns True if ALL are true:
      - line ends with '?'
      - line contains no '=' sign
      - line has >= 2 words

    This catches 'why does the sign flip?' but leaves 'x = 5?', '5?', and
    'solve for x' as math attempts. Errs on the side of math when uncertain.
    """
    t = (text or "").strip()
    if not t:
        return False
    if not t.endswith("?"):
        return False
    if "=" in t:
        return False
    return len(t.split()) >= 2


def collect_working('''

anchor = 'def collect_working('
if anchor not in src:
    print("FAIL: 'def collect_working(' not found")
    sys.exit(1)
src = src.replace(anchor, helper, 1)

# Step 2: expand the ? channel condition to include auto-detect
old_cond = '        if stripped.startswith("?") or low.startswith("/ask"):'
new_cond = ('        if (stripped.startswith("?") or low.startswith("/ask")\n'
            '                or _looks_like_natural_question(stripped)):')

if old_cond not in src:
    print("FAIL: '?' channel condition not found — line may be different")
    print("Looking for:", repr(old_cond))
    sys.exit(1)
src = src.replace(old_cond, new_cond, 1)

# Step 3: also update the help text to remove the '?' requirement
old_help = 'print("  - Type \'?<question>\' to ask Tanaka a question")'
new_help = 'print("  - Type any question ending in ? to ask Tanaka")'
if old_help in src:
    src = src.replace(old_help, new_help, 1)

P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
