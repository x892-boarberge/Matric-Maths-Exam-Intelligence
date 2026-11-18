"""Fix diagram display: honest open status + explorer.exe fallback."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# diagram-display fix" in src:
    print("FATAL: patch appears already applied")
    sys.exit(1)

# Patch 1 — _open_diagram: add explorer.exe fallback
p1_old = '''def _open_diagram(problem):
    path = _diagram_path_for(problem)
    if path is None:
        return None
    try:
        _os.startfile(str(path))
        return path
    except Exception:
        return None'''

p1_new = '''def _open_diagram(problem):
    # diagram-display fix: try startfile, then explorer.exe fallback.
    # Return value is HONEST — caller must check it before claiming "opened".
    path = _diagram_path_for(problem)
    if path is None:
        return None
    try:
        _os.startfile(str(path))
        return path
    except Exception:
        pass
    try:
        import subprocess
        subprocess.run(["explorer.exe", str(path.resolve())], check=False, timeout=3)
        return path
    except Exception:
        return None'''

if p1_old not in src:
    print("FATAL: Patch 1 anchor (_open_diagram body) not found")
    sys.exit(1)
if src.count(p1_old) != 1:
    print(f"FATAL: Patch 1 anchor count = {src.count(p1_old)} (expected 1)")
    sys.exit(1)
src = src.replace(p1_old, p1_new, 1)
print("Patch 1 applied: explorer.exe fallback added")

# Patch 2 — caller: check return value, honest message, name the full-page friction
p2_old = '''    if diagram_path:
        print("  Paper image: " + str(diagram_path))
        _open_diagram(group[0])
        print("  (opened in your viewer — the paper stays open)")
    else:
        print("  (no paper image for this question)")'''

p2_new = '''    if diagram_path:
        print("  Paper image: " + str(diagram_path))
        _opened = _open_diagram(group[0])
        if _opened:
            print("  (attempted to open — full page scan, Q" + qnum + " is on it)")
        else:
            print("  (open the path above — full page scan, Q" + qnum + " is on it)")
    else:
        print("  (no paper image for this question)")'''

if p2_old not in src:
    print("FATAL: Patch 2 anchor (caller block) not found")
    sys.exit(1)
if src.count(p2_old) != 1:
    print(f"FATAL: Patch 2 anchor count = {src.count(p2_old)} (expected 1)")
    sys.exit(1)
src = src.replace(p2_old, p2_new, 1)
print("Patch 2 applied: honest message + Q-num guidance")

target.write_text(src, encoding="utf-8")
print(f"\nBoth patches written to: {target}")
