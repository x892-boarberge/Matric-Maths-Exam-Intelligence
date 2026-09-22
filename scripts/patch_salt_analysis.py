"""Add third-person analysis phrases to the forbidden list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALT = ROOT / "src" / "tutor" / "salt_check.py"
src = SALT.read_text(encoding="utf-8")

if '"the learner"' not in src:
    old = '''    r"\\bmisconception_id\\b",
]'''
    new = '''    r"\\bmisconception_id\\b",
    # Third-person analysis of the learner
    r"\\bthe learner\\b",
    r"\\bthe student\\b",
    r"\\bthey seem\\b",
    r"\\bi can see that\\b",
    r"\\bit seems\\b",
    r"\\bchallenging situation\\b",
    r"\\bfueling the\\b",
    r"\\bhostility\\b",
]'''
    if old in src:
        src = src.replace(old, new, 1)
        SALT.write_text(src, encoding="utf-8")
        print("Salt check: third-person analysis now forbidden")
    else:
        print("WARNING - forbidden list block not found")
else:
    print("Third-person phrases already in forbidden list")
