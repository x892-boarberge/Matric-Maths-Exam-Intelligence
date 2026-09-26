from pathlib import Path

src = Path("src/tutor/analogue_generators.py").read_text(encoding="utf-8")
idx = src.find("def generate_all(")
print(src[idx:idx+1500])