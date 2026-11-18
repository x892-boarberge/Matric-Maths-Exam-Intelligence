import shutil
from pathlib import Path
from datetime import datetime

file = Path("src/tutor/diagnosis.py")
backup = file.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
shutil.copy(file, backup)
print(f"Backup: {backup}")

src = file.read_text(encoding="utf-8")

# Find the function header
header = "def _fn_log_fraction_base_positive(nr, expected, *args):"
if header not in src:
    print("FAIL: function header not found")
    raise SystemExit(1)

# Find the end of the function (next def at column 0, or end of file)
start = src.find(header)
next_def = src.find("\ndef ", start + 1)
if next_def == -1:
    next_def = len(src)
func_body = src[start:next_def]

print("\n=== Current function body ===")
print(func_body)
print("=== End current body ===\n")

# Check if guard already exists
if "len(l) <= len(e)" in func_body:
    print("Guard already present. Nothing to do.")
    raise SystemExit(0)

# Insert guard after the "if e[0] >= 0" line
marker = "if e[0] >= 0:"
if marker not in func_body:
    print("FAIL: marker 'if e[0] >= 0:' not found in function")
    raise SystemExit(1)

# Find the return line after the marker
lines = func_body.split("\n")
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and "if e[0] >= 0:" in line:
        # Next line should be the return False
        if i + 1 < len(lines) and "return False" in lines[i + 1]:
            new_lines.append(lines[i + 1])  # keep the return
            # Add guard after
            new_lines.append("    if len(l) <= len(e):")
            new_lines.append("        return False")
            inserted = True
            # Skip the original next line (already added)
            lines[i + 1] = None
        else:
            print(f"WARN: expected 'return False' after marker, found: {lines[i+1] if i+1 < len(lines) else 'EOF'}")

new_func_body = "\n".join(l for l in new_lines if l is not None)

if not inserted:
    print("FAIL: could not insert guard")
    raise SystemExit(1)

new_src = src[:start] + new_func_body + src[next_def:]
file.write_text(new_src, encoding="utf-8")
print("\nGuard inserted after 'if e[0] >= 0: return False'")
print(f"New file size: {file.stat().st_size} bytes")
