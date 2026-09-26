"""Engine accepts WorkingSubmission or str (backward compatible)."""
from pathlib import Path
import ast

P = Path("src/tutor/tutor_engine.py")
src = P.read_text(encoding="utf-8-sig")

if "WorkingSubmission" in src and "isinstance(learner_response" in src:
    print("Engine already patched")
    raise SystemExit(0)

# Import WorkingSubmission
old_import = "from .schemas import ("
if old_import in src and "WorkingSubmission" not in src.split("from .schemas import")[1][:500]:
    # Find the import block end
    idx = src.find(old_import)
    end = src.find(")", idx)
    block = src[idx:end]
    if "WorkingSubmission" not in block:
        new_block = block.replace("LearnerState", "LearnerState, WorkingSubmission", 1) if "LearnerState" in block else block
        # Fallback: append before close paren
        if "WorkingSubmission" not in new_block:
            new_block = block.rstrip() + ",\n    WorkingSubmission"
        src = src[:idx] + new_block + src[end:]
        print("Added WorkingSubmission to imports")
else:
    # Simple fallback
    if "from .schemas import" not in src:
        print("WARN: schemas import not found")
    else:
        print("Import already has WorkingSubmission (or couldn't check)")

# Patch the step() method signature and top
old_sig_variants = [
    "    def step(self, state, problem, learner_response, explicit_solution_request=False):",
    "    def step(self, state: LearnerState, problem: Problem, learner_response: str, explicit_solution_request: bool = False",
]

INSERT = '''

        # -------- Phase 2: accept WorkingSubmission or str --------
        try:
            from .schemas import WorkingSubmission as _WS
            if isinstance(learner_response, _WS):
                submission = learner_response
                # Record the full working in session events
                state.session_events.append({
                    "kind": "working_submitted",
                    "step_count": len(submission.steps),
                    "steps": submission.step_texts(),
                    "source": submission.source,
                })
                # Use the last line as the answer for now (Phase 3 will use all steps)
                learner_response = submission.last_line()
        except ImportError:
            pass
        # -------- end Phase 2 --------
'''

# Find "def step(" and inject after the docstring or after the first line
idx = src.find("def step(")
if idx < 0:
    print("WARN: def step() not found")
else:
    # Find end of signature line (the colon)
    sig_end = src.find(":", idx)
    # Find the next non-empty, non-docstring line to anchor on
    # Insert right after the first statement inside the method body
    body_start = src.find("\n", sig_end) + 1
    # Skip to the first real code line (skip blank lines and docstring)
    while body_start < len(src) and src[body_start] in " \t\n":
        body_start += 1
    
    # Anchor on the first line that reads "now = " or similar
    # Instead, just insert at body_start with proper indentation
    src = src[:body_start] + INSERT + src[body_start:]
    print("Inserted WorkingSubmission handling at start of step()")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Engine patched")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)