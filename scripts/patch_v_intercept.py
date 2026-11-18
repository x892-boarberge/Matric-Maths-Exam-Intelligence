"""Fix v-intercept: skip grading when learner pressed 'v' before answering.
Simpler patch — no regex, direct line inspection."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# v-intercept fix" in src:
    print("FATAL: patch appears already applied")
    sys.exit(1)

lines = src.split("\n")
target_idx = None
for i, ln in enumerate(lines):
    # Match the _var_text join line, accounting for indentation
    if "_var_text" in ln and "join(_var_lines)" in ln and "=" in ln:
        target_idx = i
        break

if target_idx is None:
    print("FATAL: could not find '_var_text = ...join(_var_lines)' line")
    sys.exit(1)

target_line = lines[target_idx]
print(f"Found at line {target_idx + 1}:")
print(f"  {repr(target_line)}")

# Measure indentation
indent_len = len(target_line) - len(target_line.lstrip())
indent = " " * indent_len
print(f"  Indent: {indent_len} spaces")

# Build the patch
patch_lines = [
    f'{indent}# v-intercept fix: skip grading when learner pressed "v" before answering',
    f'{indent}if not _var_lines:',
    f'{indent}    continue',
]
# Insert 3 lines before the target line
new_lines = lines[:target_idx] + patch_lines + lines[target_idx:]

src_new = "\n".join(new_lines)
target.write_text(src_new, encoding="utf-8")
print(f"Patch applied: 3 lines inserted before line {target_idx + 1}")
