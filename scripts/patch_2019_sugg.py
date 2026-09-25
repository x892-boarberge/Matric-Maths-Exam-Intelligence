"""Fix 2019 suggestions splitter — paragraph-based, not bullet-based."""
import re
from pathlib import Path

P = Path("scripts/parse_diagnostic_v8.py")
src = P.read_text(encoding="utf-8")

old = '''def split_paras_2019_suggestions(block):
    """2019 suggestions: use standard (a) splitter — they're normal."""
    pat = re.compile(r"\\(([a-z])\\)\\s+(.+?)(?=\\([a-z]\\)\\s+|\\Z)", re.DOTALL)
    out = []
    for letter, raw in pat.findall(block):
        cleaned, raw_len, clean_len = clean(raw)
        if len(cleaned) < 40:
            continue
        out.append((letter, cleaned, raw_len, clean_len))
    return out'''

new = '''def split_paras_2019_suggestions(block):
    """2019 suggestions: paragraph-based (same scrambling as errors)."""
    # Strip scrambled bullets
    block = re.sub(r"\\([a-z]\\)\\s*\\n?", " ", block)
    block = re.sub(r"[ \\t]+", " ", block)
    # Split on sentence boundaries where a new paragraph likely begins
    # Paragraph starts: "More ...", "Skills ...", "Teachers ...", "Learners ...",
    # "Emphasis ...", "When ...", "Regular ...", "Ensure ...", "Correct ...", "As ..."
    starts = re.compile(
        r"(?<=\\.\\s)(?=(?:More|Skills|Teachers|Learners|Emphasis|When|Regular|Ensure|"
        r"Correct|As|Given|In|Learner|Writing|The|Problem|It|Formal|At|Time|Learners|"
        r"Provide|Frequent|Attention|Greater|Continuous|Sufficient|Learners)\\s)",
    )
    parts = starts.split(block)
    out = []
    for raw in parts:
        cleaned, raw_len, clean_len = clean(raw)
        if len(cleaned) < 60:
            continue
        out.append(("?", cleaned, raw_len, clean_len))
    return out'''

if old in src:
    src = src.replace(old, new, 1)
    P.write_text(src, encoding="utf-8")
    print("Patched 2019 suggestions splitter")
else:
    print("WARN anchor not found")

# Also update the OUT path to v9
src = Path("scripts/parse_diagnostic_v8.py").read_text(encoding="utf-8")
src = src.replace('diagnostic_errors_v8.csv', 'diagnostic_errors_v9.csv', 1)
Path("scripts/parse_diagnostic_v9.py").write_text(src, encoding="utf-8")
print("Wrote v9 as scripts/parse_diagnostic_v9.py")