from pathlib import Path
lines = Path("scripts/cli_tutor.py").read_text(encoding="utf-8").splitlines()
# Find the drill call
for i, l in enumerate(lines):
    if "run_drill" in l or "Drill finished" in l:
        # Show 20 lines around
        start = max(0, i - 10)
        end = min(len(lines), i + 20)
        print(f"=== context around line {i+1} ===")
        for j in range(start, end):
            print(f"{j+1:4d}: {lines[j]}")
        print()