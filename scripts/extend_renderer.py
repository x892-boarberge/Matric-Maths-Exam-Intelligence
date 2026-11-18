"""Extend render_diagrams.py — handle exponential form + flag ambiguous notation."""
from pathlib import Path
import shutil, subprocess
from datetime import datetime

f = Path("scripts/render_diagrams.py")
bak = f.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
shutil.copy(f, bak)
src = f.read_text(encoding="utf-8")

# Replace _parse_log_variant with a version that handles exponential form
old_fn_start = "def _parse_log_variant(text):"
old_fn_end = "    return None\n"

# Find the block
start = src.find(old_fn_start)
if start == -1:
    print("FAIL: _parse_log_variant not found")
    raise SystemExit(1)
end = src.find(old_fn_end, start)
if end == -1:
    print("FAIL: function end marker not found")
    raise SystemExit(1)
end += len(old_fn_end)

new_fn = '''def _parse_log_variant(text):
    """Extract base and marked point from log-curve or exponential-form variant."""
    # Form 1: "Find t if (8; t) lies on f(x) = log_2(x)."
    m = re.search(r"\\(([0-9./]+);\\s*([a-z])\\)\\s*lies on f\\(x\\)\\s*=\\s*log_\\{?([0-9/]+)\\}?\\(x\\)", text)
    if m:
        return Fraction(m.group(3)), Fraction(m.group(1)), m.group(2), None
    # Form 2: "The point (25; k) lies on f(x) = log_5(x). Determine k."
    m = re.search(r"point\\s*\\(([0-9./]+);\\s*([a-z])\\)\\s*lies on f\\(x\\)\\s*=\\s*log_\\{?([0-9/]+)\\}?\\(x\\)", text)
    if m:
        return Fraction(m.group(3)), Fraction(m.group(1)), m.group(2), None
    # Form 3: "Calculate p if log_2(8) = p."
    m = re.search(r"log_\\{?([0-9/]+)\\}?\\(([0-9./]+)\\)\\s*=\\s*([a-z])", text)
    if m:
        return Fraction(m.group(1)), Fraction(m.group(2)), m.group(3), None
    # Form 4: "If base^var = arg, write down var in log form and hence find var."
    # Detect ambiguous 1/N^var notation first
    ambiguous = re.search(r"\\bIf\\s+1/(\\d+)\\^([a-z])\\s*=", text)
    if ambiguous:
        # Treat as (1/N)^var — most likely intent
        base = Fraction(1, int(ambiguous.group(1)))
        var = ambiguous.group(2)
        m_arg = re.search(r"=" + r"\\s*(\\d+(?:/\\d+)?)", text)
        if m_arg:
            note = "AMBIGUOUS_NOTATION: '1/N^var' should be '(1/N)^var' — regenerate with parentheses"
            return base, Fraction(m_arg.group(1)), var, note
    # Clean exponential form "base^var = arg"
    m = re.search(r"(?:If|Given|Calculate)\\s*\\(?(\\d+(?:/\\d+)?)\\)?\\^([a-z])\\s*=\\s*(\\d+(?:/\\d+)?)", text)
    if m:
        return Fraction(m.group(1)), Fraction(m.group(3)), m.group(2), None
    return None
'''

src = src[:start] + new_fn + src[end:]

# Update call site to accept 4-tuple
old_call = '''        parsed = _parse_log_variant(v["variant_question"])
        if not parsed:
            skipped += 1
            continue
        base, x_marked, var_name = parsed'''
new_call = '''        parsed = _parse_log_variant(v["variant_question"])
        if not parsed:
            skipped += 1
            continue
        base, x_marked, var_name, parse_note = parsed
        if parse_note:
            v["diagram_note"] = parse_note'''

if old_call not in src:
    print("FAIL: call site not found")
    raise SystemExit(1)
src = src.replace(old_call, new_call, 1)

f.write_text(src, encoding="utf-8")
print(f"Patched {f}")

r = subprocess.run(["py", "-m", "py_compile", str(f)], capture_output=True)
if r.returncode == 0:
    print("PASS: compiles")
else:
    print(f"FAIL: {r.stderr.decode()[:400]}")
