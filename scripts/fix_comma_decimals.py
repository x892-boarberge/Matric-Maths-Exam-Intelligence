"""Revert filter, add comma-decimal support."""
from pathlib import Path
import ast

P = Path("scripts/fingerprint_per_topic_v3.py")
src = P.read_text(encoding="utf-8-sig")

# --- FIX 1: revert the over-aggressive decimal guard ---
old_guard = '''                if "." in num:
                    # Extra guard: skip if looks like subquestion ref
                    # (integer part 1-12, decimal part 1-5, no leading zero)
                    m_sub = re.match(r"^(\\d+)\\.(\\d+)$", num)
                    if m_sub:
                        ip, dp = m_sub.groups()
                        if 1 <= int(ip) <= 20 and 1 <= int(dp) <= 9:
                            continue  # likely subquestion ref, skip
                    by_topic[topic]["decimals"].append(num)
                else:
                    by_topic[topic]["ints"].append(num)'''

new_guard = '''                if "." in num:
                    by_topic[topic]["decimals"].append(num)
                else:
                    by_topic[topic]["ints"].append(num)'''

if old_guard in src:
    src = src.replace(old_guard, new_guard, 1)
    print("Reverted decimal guard")
else:
    print("WARN: guard not found")

# --- FIX 2: add comma-decimal normalisation BEFORE token extraction ---
old_clean = '''        block = MARKS_RE.sub(" ", block)
        block = SUBQ_LINE_START_RE.sub(" ", block)
        block = SUBQ_INLINE_RE.sub(" ", block)
        block = SUBQ_RANGE_RE.sub(" ", block)
        block = re.sub(r"Copyright reserved.*", " ", block)
        block = re.sub(r"Please turn over.*", " ", block)
        block = re.sub(r"DBE/November\\s+\\d+", " ", block, flags=re.IGNORECASE)'''

new_clean = '''        # Convert SA comma-decimals to point-decimals
        # R58 230,94 → 58230.94 ; 0,26 → 0.26
        # Pattern: digits + comma + digits (where comma is between digits)
        block = re.sub(r"(?<=\\d),(?=\\d)", ".", block)
        # Remove space thousands separators inside money: 58 230 → 58230
        block = re.sub(r"(?<=\\d)\\s(?=\\d{3}\\b)", "", block)

        block = MARKS_RE.sub(" ", block)
        block = SUBQ_LINE_START_RE.sub(" ", block)
        block = SUBQ_INLINE_RE.sub(" ", block)
        block = SUBQ_RANGE_RE.sub(" ", block)
        block = re.sub(r"Copyright reserved.*", " ", block)
        block = re.sub(r"Please turn over.*", " ", block)
        block = re.sub(r"DBE/November\\s+\\d+", " ", block, flags=re.IGNORECASE)'''

if old_clean in src:
    src = src.replace(old_clean, new_clean, 1)
    print("Added comma-decimal and thousand-separator normalisation")
else:
    print("WARN: clean block not found")

ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Syntax OK")