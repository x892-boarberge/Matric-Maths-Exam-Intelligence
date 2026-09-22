"""Wire the LLM phraser into the engine as the first-choice renderer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# 1. Import the phraser
if "llm_phraser" not in src:
    src = src.replace(
        "from . import misconception_hints\n",
        "from . import misconception_hints\nfrom . import llm_phraser\n",
        1,
    )
    print("llm_phraser imported")

# 2. Replace the message = self.phrase_renderer(ctx) line
old = "        message = self.phrase_renderer(ctx)\n"
new = '''        # Try the LLM phraser first. If it fails or the salt check
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

if old in src and "use_llm_phraser" not in src:
    src = src.replace(old, new, 1)
    print("Renderer line replaced with phraser-first logic")

# 3. Add use_llm_phraser to __init__
old_init = '''    def __init__(
        self,
        phrase_renderer: Optional[Callable[[Dict[str, Any]], str]] = None,
        session_logger: Optional[SessionLogger] = None,
    ):
        self.phrase_renderer = phrase_renderer or self._default_renderer
        self.logger = session_logger'''

new_init = '''    def __init__(
        self,
        phrase_renderer: Optional[Callable[[Dict[str, Any]], str]] = None,
        session_logger: Optional[SessionLogger] = None,
        use_llm_phraser: bool = True,
    ):
        self.phrase_renderer = phrase_renderer or self._default_renderer
        self.logger = session_logger
        self.use_llm_phraser = use_llm_phraser'''

if old_init in src:
    src = src.replace(old_init, new_init, 1)
    print("__init__ patched with use_llm_phraser flag")
else:
    print("WARNING - __init__ block not found")

# 4. Add specific_hint to the ctx build
old_ctx = '''            "learner_response": learner_response,
            "engine_rule": engine_rule,
        }'''
new_ctx = '''            "learner_response": learner_response,
            "engine_rule": engine_rule,
            "specific_hint": (
                misconception_hints.get_hint(diag.misconception_id, hint_level.value)
                if diag.misconception_id and hint_level else None
            ),
        }'''
if old_ctx in src and "specific_hint" not in src:
    src = src.replace(old_ctx, new_ctx, 1)
    print("ctx now carries the specific hint")

ENGINE.write_text(src, encoding="utf-8")
print("patch complete")
