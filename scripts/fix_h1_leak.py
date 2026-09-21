"""Stop the H1 default template from leaking the diagnosis explanation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

old = '''        if h == HintLevel.H1:
            return f"Think about the concept here. {d.explanation}"'''

new = '''        if h == HintLevel.H1:
            if d.error_type == ErrorType.UNKNOWN or not d.explanation:
                return "Think about the concept here. What rule or formula applies to this step?"
            return f"Think about the concept here. {d.explanation}"'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("H1 leak fixed")
else:
    print("H1 template not found. Inspect tutor_engine.py manually.")
