"""Wire v2 topic_id through CLI and engine. Adds topic_v2 field."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# --- Patch 1: schemas.py ---
p = ROOT / "src" / "tutor" / "schemas.py"
src = p.read_text(encoding="utf-8")
if "topic_v2" not in src:
    src = src.replace(
        "    expected_answer: str\n",
        "    expected_answer: str\n    topic_v2: Optional[str] = None\n",
        1,
    )
    p.write_text(src, encoding="utf-8")
    print("schemas.py patched: added topic_v2 to Problem")
else:
    print("schemas.py already has topic_v2")

# --- Patch 2: tutor_engine.py ---
p = ROOT / "src" / "tutor" / "tutor_engine.py"
src = p.read_text(encoding="utf-8")
if '"topic_v2"' not in src:
    src = src.replace(
        '"problem_id": problem.problem_id,\n',
        '"problem_id": problem.problem_id,\n                    "topic_v2": problem.topic_v2,\n',
        1,
    )
    p.write_text(src, encoding="utf-8")
    print("tutor_engine.py patched: logs topic_v2 in LEARNER_ATTEMPTED")
else:
    print("tutor_engine.py already logs topic_v2")

# --- Patch 3: cli_tutor.py ---
p = ROOT / "scripts" / "cli_tutor.py"
src = p.read_text(encoding="utf-8")

# Import adapter
if "mapping_adapter" not in src:
    src = src.replace(
        "from src.tutor.n08_loader import get_library\n",
        "from src.tutor.n08_loader import get_library\nfrom src.tutor.mapping_adapter import v1_to_v2\n",
        1,
    )
    print("cli_tutor.py: added adapter import")

# Problem construction
src = re.sub(
    r'(problem = Problem\(\s*\n\s*problem_id="CLI1",\s*\n\s*skill_id=item\["skill_id"\],\s*\n\s*topic=item\["topic"\],\n)',
    r'\1        topic_v2=v1_to_v2(item["topic"]),\n',
    src,
)
if 'topic_v2=v1_to_v2(item["topic"])' in src:
    print("cli_tutor.py: wired topic_v2 into Problem")
else:
    print("cli_tutor.py: WARNING - Problem construction not patched, check manually")

# PROBLEM_PRESENTED payload
src = src.replace(
    '"topic": problem.topic,\n            "prompt": problem.prompt,',
    '"topic": problem.topic,\n            "topic_v2": problem.topic_v2,\n            "prompt": problem.prompt,',
    1,
)
if 'topic_v2": problem.topic_v2' in src:
    print("cli_tutor.py: logs topic_v2 in PROBLEM_PRESENTED")

# Header print
src = src.replace(
    'print(f"Topic: {problem.topic} / {problem.subtopic}")',
    'print(f"Topic: {problem.topic} ({problem.topic_v2}) / {problem.subtopic}")',
    1,
)
if '(problem.topic_v2)' in src:
    print("cli_tutor.py: displays topic_v2 in header")

p.write_text(src, encoding="utf-8")

print()
print("Patch complete.")
