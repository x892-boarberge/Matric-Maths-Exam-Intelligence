"""patch_playbook_descent.py — descend into subquestions for real answer."""
import re
import subprocess
import sys
from pathlib import Path

P = Path("src") / "tutor" / "conversation.py"
src = P.read_text(encoding="utf-8")

pat = re.compile(
    r"def match_playbook_answer\(question_id, intent\):.*?(?=\ndef )",
    re.DOTALL,
)

NEW = '''def match_playbook_answer(question_id, intent):
    """Return (answer_text, answer_source). Source is 'playbook', 'deferred',
    or 'declined'.

    Playbook structure: top-level has question_id, foundation_text,
    acronym_strip, subquestions. subquestions is a dict keyed by "1.1.1" etc.
    Each subquestion has variant_question, demonstration, memo_marks,
    fast_path, fatal_error, answer_book_layout, hack, trap, presentation.
    """
    pb = _load_playbook(question_id)
    if not pb:
        return None, "deferred"

    # Homework / off-topic: log but decline explicitly
    if intent == "off_topic":
        return None, "declined"

    # Descend into subquestions if present
    content = pb
    if "subquestions" in pb and isinstance(pb["subquestions"], dict):
        sq_key = ""
        if "_Q" in question_id:
            sq_key = question_id.split("_Q")[-1]
        if sq_key and sq_key in pb["subquestions"]:
            content = pb["subquestions"][sq_key]

    def _get(key):
        v = content.get(key)
        if v is None and content is not pb:
            v = pb.get(key)
        return v

    if intent == "curiosity":
        answer = _get("fatal_error") or _get("fast_path") or _get("hack")
        if answer:
            return answer, "playbook"

    if intent == "frustration":
        fast = _get("fast_path")
        if fast:
            return f"Let's try the fast path: {fast}", "playbook"
        fatal = _get("fatal_error")
        if fatal:
            return f"Take a breath. The key thing here: {fatal}", "playbook"

    if intent == "alternative_method":
        demo = _get("demonstration")
        if demo:
            if isinstance(demo, list):
                demo = " ".join(str(d) for d in demo)
            return f"Here's the standard way: {demo}", "playbook"

    if intent == "question_about_work":
        fast = _get("fast_path")
        if fast:
            return fast, "playbook"

    # Fallback: fatal_error if present
    fatal = _get("fatal_error")
    if fatal:
        return fatal, "playbook"

    return None, "deferred"

'''

new_src, n = pat.subn(NEW, src, count=1)
if n == 0:
    print("FAIL: match_playbook_answer pattern not matched")
    sys.exit(1)

P.write_text(new_src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
else:
    print("py_compile: FAIL")
    print(r.stderr.decode())
    sys.exit(1)
