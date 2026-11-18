"""patch_aggressive_question_detect.py — first-word question detection."""
import re
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

# Replace the existing _looks_like_natural_question with a more aggressive version
pat = re.compile(
    r"def _looks_like_natural_question\(text\):.*?(?=\ndef )",
    re.DOTALL,
)

NEW = '''def _looks_like_natural_question(text):
    """Heuristic: is this a learner question, not a math attempt?

    Catches three shapes:
      1. Ends with '?' and has >=2 words
      2. First word is a question word AND has >=3 words (no '=' anywhere)
      3. Contains 'why/how/what' anywhere AND has >=3 words (no '=' anywhere)

    Never matches if the line contains '=' (almost certainly math).
    Conservative on the side of math when uncertain.
    """
    t = (text or "").strip()
    if not t:
        return False
    if "=" in t:
        return False
    words = t.split()
    if not words:
        return False
    low = t.lower()

    if t.endswith("?") and len(words) >= 2:
        return True

    qwords = {"why", "how", "what", "when", "where", "which", "who",
              "can", "could", "would", "should", "is", "are", "does", "do"}
    if words[0].lower() in qwords and len(words) >= 3:
        return True

    if len(words) >= 3:
        for w in ("why", "how", "what"):
            if (" " + w + " ") in (" " + low + " "):
                return True

    return False


'''

new_src, n = pat.subn(NEW, src, count=1)
if n == 0:
    print("FAIL: _looks_like_natural_question pattern not matched")
    sys.exit(1)

P.write_text(new_src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
