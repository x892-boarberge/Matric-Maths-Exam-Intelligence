"""Replace main() with a topic loop — menu returns to topic picker, quit exits."""
from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

# Locate main() and the if __name__ block
start = src.find("def main(")
if start < 0:
    print("main() not found")
    raise SystemExit(1)

end = src.find('if __name__', start)
if end < 0:
    end = len(src)

NEW_MAIN = '''def main() -> None:
    # ---- Setup once: learner id and store persist across topics ----
    learner_id = input("\\nEnter learner id (or press Enter for 'cli_user'): ").strip()
    if not learner_id:
        learner_id = "cli_user"

    store_path = ROOT / "data" / "learner_store" / "learners.db"
    store = open_store(store_path)
    store.load_learner(learner_id)
    print("Learner:", learner_id, "| store:", store_path)

    # ============================================================
    # Topic loop — learner can jump between topics freely
    # ============================================================
    while True:
        item = pick_problem()
        # pick_problem() exits the process on Q, so item is either "__corpus__" or a dict

        if item == "__corpus__":
            problem = pick_navigated_problem(load_corpus())
            if problem is None:
                # User chose Back/Quit inside navigation — go back to the main menu
                continue
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

        # ---- Fresh session for this topic ----
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session_id = "cli_" + stamp
        store.start_session(learner_id, item["skill_id"])

        log_dir = ROOT / "data" / "processed" / "tutor" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / (session_id + ".jsonl")

        logger = SessionLogger(session_id, log_path)
        logger.emit(
            EventType.SESSION_STARTED,
            {"mode": "cli", "skill_id": item["skill_id"]},
        )

        problem = item.get("_preloaded_problem") or Problem(
            problem_id="CLI1",
            skill_id=item["skill_id"],
            topic=item["topic"],
            topic_v2=v1_to_v2(item["topic"]),
            subtopic=item["subtopic"],
            structure_type=item["structure_type"],
            prompt=item["prompt"],
            expected_answer=item["expected"],
        )

        state = LearnerState(
            learner_id=learner_id,
            skill_id=item["skill_id"],
            current_session_id=session_id,
        )

        engine = TutorEngine(session_logger=logger, learner_store=store, session_id=session_id)

        logger.emit(
            EventType.PROBLEM_PRESENTED,
            {
                "problem_id": problem.problem_id,
                "skill_id": problem.skill_id,
                "topic": problem.topic,
                "topic_v2": problem.topic_v2,
                "prompt": problem.prompt,
            },
        )

        print("\\n" + "-" * 60)
        print(format_topic_line(problem))
        print("Problem: " + problem.prompt)

        _diagram = _diagram_path_for(problem)
        if _diagram is not None:
            print("Diagram page: " + str(_diagram))
            _opened = _open_diagram(problem)
            if _opened is not None:
                print("(opened in your image viewer - type \\"diagram\\" to reopen)")
            else:
                print("(open the image manually to see the diagram)")
        print("-" * 60)
        print("Commands:  quit  |  answer (ask for more help)  |  just type your attempt")
        print("Note: " + item["hint_correct"])
        print("-" * 60)

        # ---- Drill mode? ----
        print()
        print("  Start a drill on this skill?")
        print("    d  → drill (5 questions, mastery tracked)")
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

            summary = logger.close()
            store.end_session(session_id)

            print("\\n" + "=" * 60)
            print("Session log: " + str(log_path))
            print("SESSION_ENDED: " + str(summary))
            print("=" * 60)

            exit_reason = result.get("exit_reason", "completed")

            if exit_reason == "quit":
                break
            if exit_reason == "menu":
                # back to topic picker
                continue

            # completed / learner_end — offer next choice
            print()
            again = input("  Pick another topic? [Y/n]: ").strip().lower()
            if again == "n":
                break
            continue

        # ---- Legacy single-attempt loop ----
        while True:
            submission = collect_working()
            if submission is None:
                break

            action = engine.step(
                state,
                problem,
                submission,
                explicit_solution_request=False,
            )

            print("\\n  diagnosis:    " + action.diagnosis.error_type.value, end="")
            if action.diagnosis.misconception_id:
                print(" [" + action.diagnosis.misconception_id + "]", end="")
            print()
            print(
                "  intervention: " + action.intervention.intervention_pattern
                + " [" + action.intervention.provenance.value + "] "
                + str(action.intervention.n08_intervention_id or "")
            )
            print("  hint level:   " + (action.hint_level.value if action.hint_level else "-"))
            print("  action:       " + action.action.value)
            print("  tutor:        " + action.tutor_message)

            if action.diagnosis.error_type.value == "none":
                print()
                print("=" * 60)
                print("Correct.")
                print("=" * 60)
                print("  [Enter]  pick another topic")
                print("  q        end the tutor session")
                choice = input("  > ").strip().lower()
                if choice in ("q", "quit", "exit"):
                    break
                break  # fall through to topic loop

        summary = logger.close()
        store.end_session(session_id)

        print("\\n" + "=" * 60)
        print("Session log: " + str(log_path))
        print("SESSION_ENDED: " + str(summary))
        print("=" * 60)

        # After legacy attempt — offer next topic
        again = input("  Pick another topic? [Y/n]: ").strip().lower()
        if again == "n":
            break
        continue

    # ---- Clean shutdown ----
    store.close()
    print("\\nTutor session ended. See you next time.")


'''

src = src[:start] + NEW_MAIN + src[end:]

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("main() replaced — topic loop wired")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)