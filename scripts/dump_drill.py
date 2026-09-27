from pathlib import Path
src = Path("src/tutor/drill.py").read_text(encoding="utf-8")
print(f"Length: {len(src)} chars")
print("=" * 70)
print(src)