"""Replace _is_correct with the graceful matcher in diagnosis.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAG = ROOT / "src" / "tutor" / "diagnosis.py"
src = DIAG.read_text(encoding="utf-8")

# Add import
if "answer_matcher" not in src:
    src = src.replace(
        "import re\n",
        "import re\nfrom .answer_matcher import is_correct as _graceful_is_correct\n",
        1,
    )

# Find _is_correct function and make it delegate
old_pattern = 'def _is_correct(response: str, expected: str) -> bool:'
if old_pattern in src:
    # Find the whole function body. Use a simple replace of the first return.
    import re as _re
    # Replace the body: keep signature, add delegation at top
    lines = src.split("\n")
    new_lines = []
    in_fn = False
    replaced = False
    for line in lines:
        if line.strip().startswith("def _is_correct("):
            in_fn = True
            new_lines.append(line)
            new_lines.append("    return _graceful_is_correct(response, expected)")
            continue
        if in_fn:
            # Skip the old body (until a blank line followed by non-indented)
            if line and not line.startswith(" ") and not line.startswith("\t"):
                in_fn = False
                new_lines.append(line)
            else:
                # Skip old body lines
                continue
        else:
            new_lines.append(line)
    src = "\n".join(new_lines)

DIAG.write_text(src, encoding="utf-8")
print("diagnosis.py patched")
