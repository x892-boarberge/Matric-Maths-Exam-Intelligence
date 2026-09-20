"""Add corpus menu option to cli_tutor.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "cli_tutor.py"
src = CLI.read_text(encoding="utf-8")

# Import the loader
if "question_loader" not in src:
    src = src.replace(
        "from src.tutor.mapping_adapter import v1_to_v2\n",
        "from src.tutor.mapping_adapter import v1_to_v2\nfrom src.tutor.question_loader import load_gold_2025\n",
        1,
    )
    print("added loader import")

# Add option P to the menu function
old_menu = '''    for i, p in enumerate(PROBLEMS, 1):
        print(f"  {i}. {p['topic']} — {p['subtopic']}")
    print("  Q. Quit")
    while True:
        choice = input("\\nChoose problem [1-5]: ").strip().lower()
        if choice in ("q", "quit", "exit"):
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(PROBLEMS):
            return PROBLEMS[int(choice) - 1]
        print("Enter a number 1-5, or Q to quit.")'''

new_menu = '''    print()
    print("  P. Practise from 2025 real corpus")
    print("  Q. Quit")
    for i, p in enumerate(PROBLEMS, 1):
        print(f"  {i}. {p['topic']} — {p['subtopic']}")
    while True:
        choice = input("\\nChoose [1-5, P, Q]: ").strip().lower()
        if choice in ("q", "quit", "exit"):
            sys.exit(0)
        if choice == "p":
            return "__corpus__"
        if choice.isdigit() and 1 <= int(choice) <= len(PROBLEMS):
            return PROBLEMS[int(choice) - 1]
        print("Enter 1-5, P, or Q.")'''

if new_menu not in src:
    src = src.replace(old_menu, new_menu, 1)
    print("menu updated")

# Handle the corpus branch
if "__corpus__" not in src:
    src = src.replace(
        "def main() -> None:\n    item = pick_problem()\n",
        '''def pick_corpus_problem():
    problems = load_gold_2025()
    if not problems:
        print("No corpus questions with memo answers found.")
        sys.exit(1)
    print()
    print("2025 real NSC questions (with memo answers):")
    for i, p in enumerate(problems, 1):
        label = p.prompt[:60].replace("\\n", " ")
        print(f"  {i}. [{p.topic_v2}] {p.skill_id}")
        print(f"     {label}...")
    while True:
        choice = input("\\nChoose question [1-" + str(len(problems)) + "]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(problems):
            return problems[int(choice) - 1]
        print("Enter a number.")


def main() -> None:
    item = pick_problem()
    if item == "__corpus__":
        problem = pick_corpus_problem()
        item = {
            "skill_id": problem.skill_id,
            "topic": problem.topic,
            "subtopic": problem.subtopic,
            "structure_type": problem.structure_type,
            "prompt": problem.prompt,
            "expected": problem.expected_answer,
            "hint_correct": "Answer as you would in the exam.",
            "_preloaded_problem": problem,
        }
''',
        1,
    )
    print("main() updated for corpus branch")

# Use preloaded Problem if present
if "_preloaded_problem" not in src.split("def main")[-1].split("while True:")[0]:
    pass

if "_preloaded_problem" in src and "problem = Problem(" in src:
    # Replace hardcoded construction with conditional
    src = src.replace(
        '''    problem = Problem(
        problem_id="CLI1",
        skill_id=item["skill_id"],
        topic=item["topic"],
        topic_v2=v1_to_v2(item["topic"]),
        subtopic=item["subtopic"],
        structure_type=item["structure_type"],
        prompt=item["prompt"],
        expected_answer=item["expected"],
    )''',
        '''    problem = item.get("_preloaded_problem") or Problem(
        problem_id="CLI1",
        skill_id=item["skill_id"],
        topic=item["topic"],
        topic_v2=v1_to_v2(item["topic"]),
        subtopic=item["subtopic"],
        structure_type=item["structure_type"],
        prompt=item["prompt"],
        expected_answer=item["expected"],
    )''',
        1,
    )
    print("Problem construction updated")

CLI.write_text(src, encoding="utf-8")
print("cli_tutor.py patched")
