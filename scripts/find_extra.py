from pathlib import Path

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
lines = src.splitlines()
for i, l in enumerate(lines):
    if "EXTRA_WRITTEN_ANALOGUES" in l:
        print(f"Line {i+1}: {l!r}")
        for j in range(i+1, min(i+10, len(lines))):
            print(f"Line {j+1}: {lines[j]!r}")
            if "}" in lines[j] and "}" not in lines[j][:lines[j].find("}")]:
                break
        print()