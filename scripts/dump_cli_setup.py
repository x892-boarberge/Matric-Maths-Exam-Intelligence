from pathlib import Path
lines = Path("scripts/cli_tutor.py").read_text(encoding="utf-8").splitlines()
# Show lines 370-440 to see how main() sets up learner + store
for i in range(370, min(441, len(lines))):
    print(f"{i+1:4d}: {lines[i]}")