"""Remove auto-end on struggle from cli_tutor.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "cli_tutor.py"
src = CLI.read_text(encoding="utf-8")

old = '''        if action.action.value == "FLAG_FOR_HUMAN":
            print("\\nEngine flagged for human support (repeated failure). Ending session.")
            break'''

new = '''        # The session never ends because the learner is struggling.
        # Only quit or correct answer ends it.'''

if old in src:
    src = src.replace(old, new, 1)
    CLI.write_text(src, encoding="utf-8")
    print("CLI no longer ends session on struggle")
else:
    print("CLI block not found. Showing the FLAG_FOR_HUMAN lines:")
    for i, line in enumerate(src.split("\\n")):
        if "FLAG_FOR_HUMAN" in line or "flagged for human" in line.lower():
            print(i, repr(line))
