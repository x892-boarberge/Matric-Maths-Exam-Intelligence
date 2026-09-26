from pathlib import Path
import re

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
idx = src.find("EXTRA_WRITTEN_ANALOGUES")
if idx < 0:
    print("Not found")
    raise SystemExit(0)

start = src.find("{", idx)
depth = 0
end = start
for i in range(start, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

block = src[start:end+1]
print("Block length:", len(block))
print()

# Find top-level keys (2nd level of nesting)
depth = 0
for i, ch in enumerate(block):
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
    elif ch == "\"" and depth == 1:
        # Try to match a key pattern
        m = re.match(r"\"([a-z_]+)\"\s*:", block[i:i+80])
        if m:
            print("  key:", m.group(1))