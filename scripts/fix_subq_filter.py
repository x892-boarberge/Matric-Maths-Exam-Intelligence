"""Fix: filter subquestion references from decimals and fractions."""
from pathlib import Path
import ast

P = Path("scripts/fingerprint_per_topic_v3.py")
src = P.read_text(encoding="utf-8-sig")

# Add subquestion filters
old = 'MARKS_RE = re.compile(r"\\(\\d+\\)")'
new = '''MARKS_RE = re.compile(r"\\(\\d+\\)")
# Subquestion references: 1.1, 6.3, 11.2, 11.12, Q1.1, Q11.3 — filter these
SUBQ_LINE_START_RE = re.compile(r"^\\s*\\d+(\\.\\d+){1,3}\\s", re.MULTILINE)
SUBQ_INLINE_RE = re.compile(r"\\bQ\\s?\\d+(\\.\\d+){1,3}\\b")
# Subquestion ranges like "1.1 to 1.3" or "Q1.1.1-1.1.4"
SUBQ_RANGE_RE = re.compile(r"\\b\\d+(\\.\\d+){1,3}\\s*[-–]\\s*\\d+(\\.\\d+){1,3}\\b")'''

if old in src:
    src = src.replace(old, new, 1)
    print("Added filter regexes")
else:
    print("WARN: anchor not found — searching")
    idx = src.find("MARKS_RE")
    print(repr(src[idx:idx+100]))

# Apply the filters to block text before extraction
old2 = '''        block = MARKS_RE.sub(" ", block)
        block = re.sub(r"Copyright reserved.*", " ", block)
        block = re.sub(r"Please turn over.*", " ", block)
        block = re.sub(r"DBE/November\\s+\\d+", " ", block, flags=re.IGNORECASE)'''

new2 = '''        block = MARKS_RE.sub(" ", block)
        block = SUBQ_LINE_START_RE.sub(" ", block)
        block = SUBQ_INLINE_RE.sub(" ", block)
        block = SUBQ_RANGE_RE.sub(" ", block)
        block = re.sub(r"Copyright reserved.*", " ", block)
        block = re.sub(r"Please turn over.*", " ", block)
        block = re.sub(r"DBE/November\\s+\\d+", " ", block, flags=re.IGNORECASE)'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Applied subquestion filters to block")
else:
    print("WARN: block anchor not found")

# Also filter trailing decimals that are ONLY subquestion refs (small int + small decimal)
old3 = '''            elif num:
                if "." in num:
                    by_topic[topic]["decimals"].append(num)
                else:
                    by_topic[topic]["ints"].append(num)'''

new3 = '''            elif num:
                if "." in num:
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

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Added decimal guard")
else:
    print("WARN: decimal block not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)