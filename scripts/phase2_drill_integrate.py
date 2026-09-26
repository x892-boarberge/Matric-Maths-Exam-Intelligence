"""Patch CLI to use drill engine after picking a question."""
from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

if "from src.tutor.drill import run as run_drill" in src:
    print("Already patched")
    raise SystemExit(0)

# Add import
old_import = "from src.tutor.question_loader import load_corpus"
new_import = "from src.tutor.question_loader import load_corpus\nfrom src.tutor.drill import run as run_drill"

if old_import in src:
    src = src.replace(old_import, new_import, 1)
    print("Added drill import")
else:
    print("WARN: import anchor not found")

# After the presentation block, offer drill mode
# Find the input loop start
old_loop_start = '''    print("Commands:  quit  |  answer  (ask for more help)  |  just type your attempt")
    print("Note: " + item["hint_correct"])
    print("-" * 60)

    while True:'''

new_loop_start = '''    print("Commands:  quit  |  answer  (ask for more help)  |  just type your attempt")
    print("Note: " + item["hint_correct"])
    print("-" * 60)

    # --- Drill mode: offer it up front ---
    print()
    print("  Start a drill on this skill?")
    print("    d  → drill (4 questions, mastery tracked)")
    print("    Enter → single attempt (legacy)")
    mode = input("  > ").strip().lower()

    if mode in ("d", "drill"):
        result = run_drill(
            engine=engine,
            store=store,
            learner_id=learner_id,
            session_id=session_id,
            anchor=problem,
            logger=logger,
        )
        print()
        print("  Drill finished:", result)
        # Skip legacy loop
        summary = logger.close()
        store.end_session(session_id)
        print("\\n" + "=" * 60)
        print("Session log: " + str(log_path))
        print("SESSION_ENDED: " + str(summary))
        print("=" * 60)
        return

    while True:'''

if old_loop_start in src:
    src = src.replace(old_loop_start, new_loop_start, 1)
    print("Inserted drill mode prompt")
else:
    print("WARN: input loop anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("CLI patched")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)