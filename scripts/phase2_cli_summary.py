"""Patch CLI: stay on skill until mastery, show session summary, dashboard command."""
from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

if "def show_session_summary" in src:
    print("Already patched")
    raise SystemExit(0)

# ============================================================
# 1. Add helpers before main()
# ============================================================
HELPERS = '''

def show_session_summary(store, learner_id, session_id, skill_id, seen_attempts):
    """Print a proper session summary."""
    print()
    print("=" * 60)
    print("Session summary")
    print("=" * 60)
    print(f"  Learner: {learner_id}")
    print(f"  Skill:   {skill_id}")
    print(f"  Attempts this session: {len(seen_attempts)}")
    correct = sum(1 for e in seen_attempts if e == "none")
    print(f"  Correct: {correct}")
    print(f"  Wrong:   {len(seen_attempts) - correct}")
    print()
    m = store.get_mastery(learner_id, skill_id)
    print(f"  Mastery state: {m['mastery_state']}")
    print(f"  Sittings passed: {m['sittings_passed']}")
    if m["mastery_state"] == "near_mastery":
        print()
        print("  You need ONE more passing sitting (3 of 4 correct)")
        print("  within 14 days to reach mastery.")
    elif m["mastery_state"] == "practising":
        print()
        print("  Keep practising. A passing sitting is 3 correct out of 4")
        print("  attempts on the same skill in a single session.")
    print("=" * 60)


def show_learner_dashboard(store, learner_id):
    """Show all skills and their mastery state."""
    import sqlite3
    print()
    print("=" * 60)
    print(f"Dashboard — {learner_id}")
    print("=" * 60)
    rows = store.conn.execute(
        "SELECT skill_id, mastery_state, sittings_passed, last_sitting_at "
        "FROM mastery WHERE learner_id = ? ORDER BY mastery_state, skill_id",
        (learner_id,),
    ).fetchall()
    if not rows:
        print("  (no mastery records yet)")
    else:
        print(f"  {'Skill':<38s} {'State':<14s} Sittings")
        print("  " + "-" * 58)
        for r in rows:
            print(f"  {r['skill_id']:<38s} {r['mastery_state']:<14s} {r['sittings_passed']}")
    print()
    n_sess = store.conn.execute(
        "SELECT COUNT(*) FROM session WHERE learner_id = ?", (learner_id,)
    ).fetchone()[0]
    n_att = store.conn.execute(
        "SELECT COUNT(*) FROM attempt WHERE learner_id = ?", (learner_id,)
    ).fetchone()[0]
    print(f"  Total sessions: {n_sess}")
    print(f"  Total attempts: {n_att}")
    print("=" * 60)


'''

anchor = "def main() -> None:"
if anchor in src:
    src = src.replace(anchor, HELPERS + "\n" + anchor, 1)
    print("Inserted helpers")
else:
    print("WARN: main() not found")

# ============================================================
# 2. Replace the post-correct prompt with a keep-going loop
# ============================================================
old_block = '''        if action.diagnosis.error_type.value == "none":
            print("\\nCorrect for this demo item. Session can end, or keep practising.")
            more = input("Another attempt on same problem? [y/N]: ").strip().lower()
            if more != "y":
                break

        # The session never ends because the learner is struggling.
        # Only quit or correct answer ends it.'''

new_block = '''        # Track attempts for the session summary
        try:
            session_attempts
        except NameError:
            session_attempts = []
        session_attempts.append(action.diagnosis.error_type.value)

        if action.diagnosis.error_type.value == "none":
            print()
            print("=" * 60)
            print("Correct.")
            print("=" * 60)
            n = len(session_attempts)
            c = sum(1 for e in session_attempts if e == "none")
            print(f"  This session: {c}/{n} correct on {item['skill_id']}")
            print()
            print("  [Enter]   next question on the same skill")
            print("  s         show session summary")
            print("  d         dashboard (all skills)")
            print("  q         end session")
            choice = input("  > ").strip().lower()

            if choice in ("q", "quit", "exit"):
                break

            if choice in ("s", "summary"):
                show_session_summary(store, learner_id, session_id, item["skill_id"], session_attempts)
                again = input("\\n  Continue? [Y/n]: ").strip().lower()
                if again == "n":
                    break
                continue

            if choice in ("d", "dashboard"):
                show_learner_dashboard(store, learner_id)
                again = input("\\n  Continue? [Y/n]: ").strip().lower()
                if again == "n":
                    break
                continue

            # Default: load another question on the same skill
            from src.tutor.question_loader import load_corpus
            all_problems = load_corpus()
            same_skill = [p for p in all_problems if p.skill_id == item["skill_id"]]
            if len(same_skill) > 1:
                # Pick a different one than the current
                import random as _r
                options = [p for p in same_skill if p.problem_id != problem.problem_id]
                if options:
                    new_problem = _r.choice(options)
                    problem = new_problem
                    print()
                    print("-" * 60)
                    print(format_topic_line(new_problem))
                    print("Problem: " + new_problem.prompt)
                    _new_diag = _diagram_path_for(new_problem)
                    if _new_diag is not None:
                        print("Diagram page: " + str(_new_diag))
                        _open_diagram(new_problem)
                    print("-" * 60)
                    state = LearnerState(
                        learner_id=learner_id,
                        skill_id=item["skill_id"],
                        current_session_id=session_id,
                    )
                    print()
                    print("Commands:  quit  |  answer  (ask for more help)  |  just type your attempt")
                    print("-" * 60)
                    continue

            # No other questions on this skill — end
            print("(No more questions on this skill. Ending session.)")
            break'''

if old_block in src:
    src = src.replace(old_block, new_block, 1)
    print("Replaced post-correct prompt")
else:
    print("WARN: post-correct block not found — showing snippet")
    idx = src.find('Another attempt on same problem')
    if idx > 0:
        print(src[max(0, idx-200):idx+250])

# ============================================================
# 3. Wrap the end of main() so summary always runs
# ============================================================
old_close = '''    summary = logger.close()

    # Close the store session and print mastery.
    store.end_session(session_id)'''

new_close = '''    # Session summary
    try:
        show_session_summary(store, learner_id, session_id, item["skill_id"], session_attempts)
    except Exception:
        pass

    summary = logger.close()

    # Close the store session and print mastery.
    store.end_session(session_id)'''

if old_close in src:
    src = src.replace(old_close, new_close, 1)
    print("Wired session summary at end")
else:
    print("WARN: end-of-session block not found")

# ============================================================
# 4. Initialize session_attempts at start of main()
# ============================================================
old_init = '''    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = "cli_" + stamp'''

new_init = '''    session_attempts = []

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = "cli_" + stamp'''

if old_init in src:
    src = src.replace(old_init, new_init, 1)
    print("Initialized session_attempts")
else:
    print("WARN: session init block not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("CLI written")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)