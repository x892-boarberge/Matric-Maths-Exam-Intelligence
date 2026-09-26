from pathlib import Path

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
idx = src.find("TEMPLATES = {")
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

# Show last 400 chars
print(repr(src[max(idx, end-400):end+1]))