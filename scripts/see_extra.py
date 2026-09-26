from pathlib import Path

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
idx = src.find("EXTRA_WRITTEN_ANALOGUES = {")
print(f"EXTRA starts at char {idx}")

# Show first 300 chars
print()
print("First 300 chars:")
print(src[idx:idx+300])
print()

# Show last 400 chars before TEMPLATES
templ = src.find("TEMPLATES = {")
if templ > 0:
    print("Last 400 chars before TEMPLATES:")
    print(src[templ-400:templ])