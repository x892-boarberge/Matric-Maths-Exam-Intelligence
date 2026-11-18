"""Diagnose the diagram display path. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, '.')

cli = Path("scripts/cli_tutor.py")
src = cli.read_text(encoding="utf-8")
lines = src.split("\n")

print("=== DIAGRAM DISPLAY DIAGNOSTIC ===\n")

# 1. Does os.startfile (or subprocess) exist?
print("1. Display-open calls in cli_tutor.py:")
hits = []
for i, ln in enumerate(lines, 1):
    if any(k in ln for k in ["startfile", "subprocess.Popen", "subprocess.run", "xdg-open", "open "]):
        hits.append((i, ln.strip()))
if hits:
    for i, ln in hits:
        print(f"   {i}: {ln}")
else:
    print("   NONE — cli_tutor.py has no code that opens an image")

# 2. Where is "opened in your viewer" printed?
print("\n2. Where 'opened in your viewer' is printed:")
for i, ln in enumerate(lines, 1):
    if "opened in your viewer" in ln or "Paper image" in ln:
        print(f"   {i}: {ln.strip()}")

# 3. Context around that print — 8 lines before, 5 after
print("\n3. Context around the diagram print:")
for i, ln in enumerate(lines, 1):
    if "Paper image" in ln:
        start = max(0, i - 9)
        end = min(len(lines), i + 6)
        for j in range(start, end):
            marker = ">>>" if j == i - 1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j]}")
        break

# 4. Does the transcript's file actually exist?
target = Path("data/processed/diagrams/pages/2025_P1_p05.png")
print(f"\n4. File exists check:")
print(f"   Path: {target}")
print(f"   Exists: {target.exists()}")
if target.exists():
    size_kb = target.stat().st_size / 1024
    print(f"   Size: {size_kb:.1f} KB")

# 5. How many page PNGs are there total?
pages = list(Path("data/processed/diagrams/pages").glob("*.png"))
print(f"\n5. Diagram pages on disk: {len(pages)} PNGs")
if pages:
    print(f"   Sample: {[p.name for p in pages[:5]]}")

# 6. Are these full pages or per-question crops?
print(f"\n6. Files per question (some are shared):")
by_q = {}
for p in pages:
    # Try to parse P1_Q4.1 style names
    parts = p.stem.split("_")
    if len(parts) >= 3:
        key = "_".join(parts[:3])
        by_q.setdefault(key, []).append(p.name)
for k, v in list(by_q.items())[:8]:
    print(f"   {k}: {v}")
