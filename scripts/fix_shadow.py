"""Fix: remove the local import that shadows the module-level one."""
from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

old = "            from src.tutor.question_loader import load_corpus\n            all_problems = load_corpus()"
new = "            all_problems = load_corpus()"

if old in src:
    src = src.replace(old, new, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Removed shadowing import")
else:
    print("WARN: anchor not found — searching")
    idx = src.find("from src.tutor.question_loader import load_corpus")
    if idx > 0:
        print(src[max(0, idx-100):idx+150])