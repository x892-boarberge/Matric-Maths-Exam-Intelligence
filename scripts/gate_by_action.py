"""Pass action_type to the gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

old = '''        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt
        ):'''

new = '''        _action_value = action_type.value if action_type else None
        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt, _action_value
        ):'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("action_type now passes through the gate")
elif "_action_value" in src:
    print("already patched")
else:
    print("WARNING - gate call block not found")
