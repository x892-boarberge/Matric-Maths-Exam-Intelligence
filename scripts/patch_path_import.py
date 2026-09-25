"""Add Path import to diagnosis.py."""
from pathlib import Path
import ast

P = Path("src/tutor/diagnosis.py")
src = P.read_text(encoding="utf-8-sig")

old = '''from __future__ import annotations

import re
from .answer_matcher import is_correct as _graceful_is_correct'''

new = '''from __future__ import annotations

import re
from pathlib import Path
from .answer_matcher import is_correct as _graceful_is_correct'''

if old in src and "from pathlib import Path" not in src:
    src = src.replace(old, new, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Added 'from pathlib import Path'")
else:
    print("WARN: anchor not found or already imported")