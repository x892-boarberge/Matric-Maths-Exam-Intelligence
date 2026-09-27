"""One-shot patcher: fix session_id join between CLI and learner_store."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "src" / "tutor" / "learner_store.py"
CLI = ROOT / "scripts" / "cli_tutor.py"

# ---- Edit 1: learner_store.py — start_session accepts session_id ----
old_store = '''    def start_session(self, learner_id: str, skill_id: str) -> str:
        session_id = "sess_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO session (session_id, learner_id, started_at, skill_id) "
            "VALUES (?, ?, ?, ?)",
            (session_id, learner_id, _now(), skill_id)
        )
        self.conn.commit()
        return session_id
'''

new_store = '''    def start_session(self, learner_id: str, skill_id: str,
                      session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = "sess_" + uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO session (session_id, learner_id, started_at, skill_id) "
            "VALUES (?, ?, ?, ?)",
            (session_id, learner_id, _now(), skill_id)
        )
        self.conn.commit()
        return session_id
'''

text = STORE.read_text(encoding="utf-8")
if new_store in text:
    print("[skip] learner_store.py already patched")
elif old_store in text:
    STORE.write_text(text.replace(old_store, new_store, 1), encoding="utf-8")
    print("[ok]  learner_store.py patched")
else:
    print("[FAIL] learner_store.py: old block not found — check indentation matches")
    raise SystemExit(1)

# ---- Edit 2: cli_tutor.py — pass session_id into start_session ----
old_cli = 'store.start_session(learner_id, item["skill_id"])'
new_cli = 'store.start_session(learner_id, item["skill_id"], session_id=session_id)'

text = CLI.read_text(encoding="utf-8")
if new_cli in text:
    print("[skip] cli_tutor.py already patched")
elif old_cli in text:
    CLI.write_text(text.replace(old_cli, new_cli, 1), encoding="utf-8")
    print("[ok]  cli_tutor.py patched")
else:
    print("[FAIL] cli_tutor.py: call site not found")
    raise SystemExit(1)

print()
print("Done. Verify with: Get-Content src\\tutor\\learner_store.py | Select-String 'def start_session' -Context 0,10")
