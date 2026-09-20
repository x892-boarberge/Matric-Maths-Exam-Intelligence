"""Fix the header line so it does not print FUNC (FUNC)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "cli_tutor.py"
src = CLI.read_text(encoding="utf-8")

old = '    print("Topic: " + str(problem.topic) + " (" + str(problem.topic_v2) + ") / " + str(problem.subtopic))'
new = '''    if problem.topic and problem.topic_v2 and problem.topic != problem.topic_v2:
        topic_display = str(problem.topic) + " (" + str(problem.topic_v2) + ")"
    else:
        topic_display = str(problem.topic or problem.topic_v2 or "")
    if problem.subtopic:
        topic_display = topic_display + " / " + str(problem.subtopic)
    print("Topic: " + topic_display)'''

if old in src:
    src = src.replace(old, new, 1)
    CLI.write_text(src, encoding="utf-8")
    print("Header dedup applied")
else:
    print("Header line not found — inspect cli_tutor.py manually")
