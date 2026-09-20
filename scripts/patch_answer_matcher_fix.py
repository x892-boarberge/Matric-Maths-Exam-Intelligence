"""Fix the function normaliser double-wrap bug."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
src = MATCHER.read_text(encoding="utf-8")

old = '''def _normalise_functions(s: str) -> str:
    """
    sin theta / sintheta / sin(theta) all become sin(theta).
    Same for cos, tan, log, ln, sqrt, and arc* variants.
    """
    def repl(m):
        return m.group(1) + "(" + m.group(2) + ")"

    pattern = r"\\b(" + FUNC_PATTERN + r")\\s*([a-z0-9]+|\\([^)]+\\))"
    prev = None
    guard = 0
    while prev != s and guard < 5:
        prev = s
        s = re.sub(pattern, repl, s)
        guard += 1
    return s'''

new = '''def _normalise_functions(s: str) -> str:
    """
    sin theta / sintheta / sin(theta) all become sin(theta).
    Same for cos, tan, log, ln, sqrt, and arc* variants.
    """
    def repl(m):
        func = m.group(1)
        arg = m.group(2)
        # If arg is already parenthesised, do not double-wrap
        if arg.startswith("(") and arg.endswith(")"):
            return func + arg
        return func + "(" + arg + ")"

    pattern = r"\\b(" + FUNC_PATTERN + r")\\s*([a-z0-9]+|\\([^)]+\\))"
    prev = None
    guard = 0
    while prev != s and guard < 5:
        prev = s
        s = re.sub(pattern, repl, s)
        guard += 1
    return s'''

if old in src:
    src = src.replace(old, new, 1)
    MATCHER.write_text(src, encoding="utf-8")
    print("Function normaliser fixed")
else:
    print("Old function not found. Inspect answer_matcher.py manually.")
