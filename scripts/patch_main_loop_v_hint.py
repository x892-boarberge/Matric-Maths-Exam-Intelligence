"""patch_main_loop_v_hint.py — v at main loop prints a nudge."""
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

if "if low == \"v\":" in src and "Variants come after a failed attempt" in src:
    print("Already patched.")
    sys.exit(0)

old = '''        if low in ("q", "quit", "exit"):
            return None'''

new = '''        if low == "v":
            print()
            print("  Variants come after a failed attempt - try 'done' first.")
            print()
            continue

        if low in ("q", "quit", "exit"):
            return None'''

if old not in src:
    print("FAIL: 'q/quit/exit' anchor not found")
    sys.exit(1)

src = src.replace(old, new, 1)
P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
