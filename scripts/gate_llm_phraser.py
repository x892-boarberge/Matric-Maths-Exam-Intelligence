"""Gate the LLM phraser so it only runs on real maths attempts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# Import the gate
if "llm_gate" not in src:
    src = src.replace(
        "from . import llm_phraser\n",
        "from . import llm_phraser\nfrom . import llm_gate\n",
        1,
    )
    print("llm_gate imported")

# Replace the phraser call with the gated version.
# The old block tries the LLM on every turn. The new block only tries
# when should_call_llm() returns True.
old = '''        # Try the LLM phraser first. If it fails or the salt check
        # rejects its output, fall back to the deterministic renderer.
        message = None
        if self.use_llm_phraser:
            phrased = llm_phraser.phrase_response(ctx)
            if phrased:
                message = phrased
                ctx["llm_used"] = True
        if message is None:
            message = self.phrase_renderer(ctx)
            ctx["llm_used"] = False
'''

new = '''        # Try the LLM phraser only when the gate says the LLM adds value.
        # Categorical states (celebration, hostile, help-seeking, meta,
        # language, silence, answer-demand, off-topic) use the pool
        # directly. Only genuine maths attempts go to the LLM.
        message = None
        if self.use_llm_phraser and llm_gate.should_call_llm(
            diseng.kind.value, is_real_attempt
        ):
            phrased = llm_phraser.phrase_response(ctx)
            if phrased:
                message = phrased
                ctx["llm_used"] = True
        if message is None:
            message = self.phrase_renderer(ctx)
            ctx["llm_used"] = False
'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("Phraser gated on maths attempts only")
elif "llm_gate.should_call_llm" in src:
    print("Gate already applied")
else:
    print("WARNING - phraser block not found. Inspect tutor_engine.py manually.")
