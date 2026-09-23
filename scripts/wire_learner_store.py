"""
Wire the learner store into the tutor engine and CLI.

Three edits:
  1. TutorEngine.__init__ accepts learner_store and session_id.
  2. TutorEngine.step() saves every attempt and recomputes mastery.
  3. cli_tutor.py opens the store, prompts for a learner_id, and prints
     the mastery state at session end.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
CLI    = ROOT / "scripts" / "cli_tutor.py"

# ============================================================
# 1. Engine __init__ - accept learner_store and session_id
# ============================================================
eng = ENGINE.read_text(encoding="utf-8")

if "learner_store: Optional" in eng:
    print("Engine already accepts learner_store")
else:
    pattern = re.compile(
        r"(def __init__\(\s*self,.*?use_llm_phraser: bool = True,)\s*\n(\s*\):)",
        re.DOTALL,
    )
    if pattern.search(eng):
        replacement = (
            r"\1\n        learner_store=None,\n        session_id: Optional[str] = None,\n\2"
        )
        eng = pattern.sub(replacement, eng, count=1)

        # Add the assignments right after use_llm_phraser = ...
        eng = eng.replace(
            "        self.use_llm_phraser = use_llm_phraser\n",
            "        self.use_llm_phraser = use_llm_phraser\n"
            "        self.learner_store = learner_store\n"
            "        self.session_id = session_id\n",
            1,
        )
        ENGINE.write_text(eng, encoding="utf-8")
        print("Engine __init__ patched")
    else:
        print("WARNING - __init__ signature not matched")

# ============================================================
# 2. Engine step() - save attempt and recompute mastery
# ============================================================
eng = ENGINE.read_text(encoding="utf-8")

if "self.learner_store.save_attempt" in eng:
    print("Engine already saves attempts")
else:
    # Insert the persistence block right before `return TutorAction(`
    pattern = re.compile(
        r"(\n\s*return TutorAction\()",
    )
    persist = '''
        # Persist this attempt and update mastery
        if self.learner_store and self.session_id:
            try:
                self.learner_store.save_attempt(
                    session_id=self.session_id,
                    learner_id=learner_state.learner_id,
                    skill_id=problem.skill_id,
                    response=learner_response,
                    diagnosis_rule_id=diag.rule_id,
                    misconception_id=diag.misconception_id,
                    hint_level=(hint_level.value if hint_level else None),
                    error_type=diag.error_type.value,
                )
                new_mastery = self.learner_store.recompute_mastery(
                    learner_state.learner_id, problem.skill_id
                )
                try:
                    learner_state.mastery_state = MasteryState(new_mastery)
                except ValueError:
                    pass
            except Exception:
                # Persistence must never crash the tutor loop.
                pass

'''
    if pattern.search(eng):
        eng = pattern.sub(lambda _m: persist + _m.group(1).lstrip("\n"), eng, count=1)
        ENGINE.write_text(eng, encoding="utf-8")
        print("Engine step() now persists attempts")
    else:
        print("WARNING - return TutorAction block not found")

# ============================================================
# 3. CLI - open the store, prompt for learner_id, print mastery
# ============================================================
cli = CLI.read_text(encoding="utf-8")

if "learner_store" in cli:
    print("CLI already wired to the store")
else:
    # Add the import
    cli = cli.replace(
        "from src.tutor.question_loader import load_gold_2025\n",
        "from src.tutor.question_loader import load_gold_2025\n"
        "from src.tutor.learner_store import open_store\n"
        "from src.tutor.schemas import MasteryState\n",
        1,
    )

    # Prompt for learner_id and open the store, right before the
    # session_id is generated.
    old_session = '''    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = "cli_" + stamp'''

    new_session = '''    # Ask for a learner id so the session can be persisted.
    learner_id = input("\\nEnter learner id (or press Enter for 'cli_user'): ").strip()
    if not learner_id:
        learner_id = "cli_user"

    # Open the persistent learner store.
    store_path = ROOT / "data" / "learner_store" / "learners.db"
    store = open_store(store_path)
    store.load_learner(learner_id)
    print("Learner:", learner_id, "| store:", store_path)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = "cli_" + stamp
    # Register this session against the learner
    store.start_session(learner_id, item["skill_id"])'''

    if old_session in cli:
        cli = cli.replace(old_session, new_session, 1)
        print("CLI opens the store and prompts for learner_id")
    else:
        print("WARNING - CLI session block not found")

    # Update the LearnerState to use the entered learner_id.
    cli = cli.replace(
        'learner_id="cli_user"',
        "learner_id=learner_id",
        1,
    )

    # Pass the store and session_id to the engine.
    cli = cli.replace(
        "engine = TutorEngine(session_logger=logger)",
        "engine = TutorEngine(session_logger=logger, learner_store=store, session_id=session_id)",
        1,
    )

    # Print mastery at the end of the session, before the final banner.
    old_end = '''    summary = logger.close()
    print("\\n" + "=" * 60)
    print("Session log: " + str(log_path))
    print("SESSION_ENDED: " + str(summary))
    print("Events: " + str(len(read_events(log_path))))
    print("=" * 60)'''

    new_end = '''    summary = logger.close()

    # Close the store session and print mastery.
    store.end_session(session_id)
    try:
        m = store.get_mastery(learner_id, item["skill_id"])
        print("\\n" + "=" * 60)
        print("Mastery for", item["skill_id"] + ":", m["mastery_state"])
        print("Sittings passed:", m["sittings_passed"])
    except Exception:
        pass
    store.close()

    print("\\n" + "=" * 60)
    print("Session log: " + str(log_path))
    print("SESSION_ENDED: " + str(summary))
    print("Events: " + str(len(read_events(log_path))))
    print("=" * 60)'''

    if old_end in cli:
        cli = cli.replace(old_end, new_end, 1)
        print("CLI prints mastery at session end")
    else:
        print("WARNING - CLI end-of-session block not found")

    CLI.write_text(cli, encoding="utf-8")

print()
print("patch complete")
