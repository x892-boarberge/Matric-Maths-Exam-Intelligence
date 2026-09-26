from pathlib import Path

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
idx = src.find("TEMPLATES = {")
# Find matching closing brace
brace = src.find("{", idx)
depth = 0
for i in range(brace, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

# Show last 500 chars of the dict
block = src[idx:end+1]
print("Last 500 chars of TEMPLATES:")
print(repr(block[-500:]))
print()
print("Total dict length:", len(block))