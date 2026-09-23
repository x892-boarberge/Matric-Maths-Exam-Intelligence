"""Pass action_type into llm_gate.should_call_llm."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# Pattern A: two-arg call (current broken state)
old_a = """        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt
        ):"""

new = """        _action_value = action_type.value if action_type else None
        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt, _action_value
        ):"""

# Pattern B: single-line two-arg call
old_b = "if self.use_llm_phraser and llm_gate.should_call_llm(diseng.kind.value, is_real_attempt):"
new_b = """_action_value = action_type.value if action_type else None
        if self.use_llm_phraser and llm_gate.should_call_llm(diseng.kind.value, is_real_attempt, _action_value):"""

if old_a in src:
    src = src.replace(old_a, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("OK: patched multi-line should_call_llm (action_type now passed)")
elif old_b in src:
    src = src.replace(old_b, new_b, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("OK: patched single-line should_call_llm (action_type now passed)")
elif "_action_value" in src and "should_call_llm(" in src:
    print("OK: already patched")
else:
    print("FAIL: should_call_llm call site not found — paste the block around should_call_llm from tutor_engine.py")
