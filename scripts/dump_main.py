from pathlib import Path
lines = Path("scripts/cli_tutor.py").read_text(encoding="utf-8").splitlines()
# Find main()
start = None
for i, l in enumerate(lines):
    if l.startswith("def main("):
        start = i
        break
if start is None:
    print("main() not found")
else:
    for i in range(start, min(start + 240, len(lines))):
        print(f"{i+1:4d}: {lines[i]}")