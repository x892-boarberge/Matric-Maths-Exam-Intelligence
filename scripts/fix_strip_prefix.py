"""Add the missing _strip_prefix helper."""
from pathlib import Path
import ast

P = Path("src/tutor/math_grader.py")
src = P.read_text(encoding="utf-8-sig")

if "def _strip_prefix" in src:
    print("Already defined")
    raise SystemExit(0)

# Find _strip_label and insert _strip_prefix right before it
anchor = "def _strip_label(s: str) -> str:"

helper = '''def _strip_prefix(s: str) -> str:
    """Strip a leading 'x = ' style prefix from a single value."""
    if not s:
        return s
    s = s.strip()
    m = re.match(r"^[a-zA-Z]\\s*=\\s*(.+)$", s)
    if m:
        return m.group(1).strip()
    return s


'''

if anchor in src:
    src = src.replace(anchor, helper + anchor, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Added _strip_prefix")
    print("Syntax OK")
else:
    print("WARN: _strip_label anchor not found")