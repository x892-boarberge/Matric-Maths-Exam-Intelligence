"""Wire the misconception hint library into the renderer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# Add import
if "misconception_hints" not in src:
    src = src.replace(
        "from . import analogue_library\n",
        "from . import analogue_library\nfrom . import misconception_hints\n",
        1,
    )
    print("hint library imported")

# Replace the H1/H2/H3 renderer block
old = '''        if h == HintLevel.H0:
            return "What are you being asked to find in this step?"
        if h == HintLevel.H1:
            if d.error_type == ErrorType.UNKNOWN or not d.explanation:
                return "Think about the concept here. What rule or formula applies to this step?"
            return f"Think about the concept here. {d.explanation}"
        if h == HintLevel.H2:
            return "Try identifying the operation you need before computing."
        if h == HintLevel.H3:
            return "Here is one step to try. Complete the rest yourself."'''

new = '''        if h == HintLevel.H0:
            return "What are you being asked to find in this step?"
        if h == HintLevel.H1:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H1")
                if specific:
                    return specific
            return "Think about the concept here. What rule or formula applies to this step?"
        if h == HintLevel.H2:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H2")
                if specific:
                    return specific
            return "Try identifying the operation you need before computing."
        if h == HintLevel.H3:
            if d.misconception_id:
                specific = misconception_hints.get_hint(d.misconception_id, "H3")
                if specific:
                    return specific
            return "Here is one step to try. Complete the rest yourself."'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("renderer updated to use hint library")
else:
    print("WARNING - renderer block not found")
