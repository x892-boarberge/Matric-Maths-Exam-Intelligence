"""patch_variant_question_channel.py — add ? channel to variant practice loop."""
import re
import subprocess
import sys
from pathlib import Path

P = Path("scripts") / "cli_tutor.py"
src = P.read_text(encoding="utf-8")

# Check if already patched
if "# variant question channel" in src:
    print("Already patched.")
    sys.exit(0)

# Find the variant loop's input call. From earlier grep:
#   Line 1042: _ln = input("  Line " + str(len(_var_lines)+1) + ": ").strip()
old = '                        _ln = input("  Line " + str(len(_var_lines)+1) + ": ").strip()'

if old not in src:
    # Try alternate whitespace
    pat = re.compile(
        r'(\s+)_ln = input\("  Line " \+ str\(len\(_var_lines\)\+1\) \+ ": "\)\.strip\(\)',
        re.MULTILINE,
    )
    m = pat.search(src)
    if not m:
        print("FAIL: variant loop input line not found")
        sys.exit(1)
    indent = m.group(1)
else:
    indent = " " * 24

# Build the replacement with question channel inserted after the input line
replacement = (
    f'{indent}_ln = input("  Line " + str(len(_var_lines)+1) + ": ").strip()\n'
    f'{indent}# variant question channel\n'
    f'{indent}if _ln and (_ln.startswith("?") or _ln.lower().startswith("/ask")\n'
    f'{indent}            or _looks_like_natural_question(_ln)):\n'
    f'{indent}    try:\n'
    f'{indent}        from src.tutor.conversation import capture_question\n'
    f'{indent}        _vconv = capture_question(\n'
    f'{indent}            store, learner_id, session_id,\n'
    f'{indent}            skill_id=getattr(problem, "skill_id", ""),\n'
    f'{indent}            question_id=getattr(problem, "problem_id", ""),\n'
    f'{indent}            question_text=_ln,\n'
    f'{indent}        )\n'
    f'{indent}        if _vconv and _vconv.get("answer_text"):\n'
    f'{indent}            print()\n'
    f'{indent}            print(f"  Tanaka: {{_vconv[\'answer_text\']}}")\n'
    f'{indent}            print()\n'
    f'{indent}        else:\n'
    f'{indent}            print()\n'
    f'{indent}            print("  Tanaka: Noted. Let\'s keep going.")\n'
    f'{indent}            print()\n'
    f'{indent}    except Exception as _e:\n'
    f'{indent}        print(f"  [question capture failed: {{_e}}]")\n'
    f'{indent}    continue'
)

if old in src:
    src = src.replace(old, replacement, 1)
else:
    src = pat.sub(replacement, src, count=1)

P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
