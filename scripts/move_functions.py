"""Move the 8 _v2 function definitions ABOVE the TEMPLATES dict."""
from pathlib import Path
import ast
import re

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# Find the appended block — starts with the marker comment
marker = "# Re-added generators (git checkout had reverted these)"
marker_pos = src.find(marker)
if marker_pos < 0:
    print("Marker not found")
    raise SystemExit(1)

# The block goes from the line before the marker to end of file
# Actually: the comment header includes a #=== line above it
line_start = src.rfind("\n", 0, marker_pos)
line_start = src.rfind("\n", 0, line_start)  # go back one more line for the =====

# From that point to end of file is our appended block
block = src[line_start:]
src = src[:line_start]

# Strip any trailing whitespace
src = src.rstrip() + "\n"

# Now insert this block BEFORE TEMPLATES
templ_idx = src.find("TEMPLATES = {")
if templ_idx < 0:
    print("TEMPLATES not found")
    raise SystemExit(1)

# Insert block before TEMPLATES
new_src = src[:templ_idx] + block.strip() + "\n\n\n" + src[templ_idx:]

try:
    ast.parse(new_src)
    P.write_text(new_src, encoding="utf-8")
    print("Moved 8 functions above TEMPLATES")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)