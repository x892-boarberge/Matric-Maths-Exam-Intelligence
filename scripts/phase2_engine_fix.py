"""Precise patch: WorkingSubmission handling at start of step()."""
from pathlib import Path
import ast

P = Path("src/tutor/tutor_engine.py")
src = P.read_text(encoding="utf-8-sig")

# ---------------------------------------------------------------
# 1. Add WorkingSubmission to the schemas import block
# ---------------------------------------------------------------
old_import = """from .schemas import (
    LearnerState,
    Problem,
    TutorAction,
    ActionType,
    HintLevel,
    ErrorType,
    MasteryState,
    ProvenanceKind,
    InterventionSelection,
    EventType,
    DiagnosisResult,
)"""

new_import = """from .schemas import (
    LearnerState,
    Problem,
    TutorAction,
    ActionType,
    HintLevel,
    ErrorType,
    MasteryState,
    ProvenanceKind,
    InterventionSelection,
    EventType,
    DiagnosisResult,
    WorkingSubmission,
)"""

if "WorkingSubmission" not in src.split("from .schemas import")[1][:500]:
    if old_import in src:
        src = src.replace(old_import, new_import, 1)
        print("Added WorkingSubmission to imports")
    else:
        print("WARN: import block format differs")
else:
    print("WorkingSubmission already imported")

# ---------------------------------------------------------------
# 2. Change signature to accept str OR WorkingSubmission
# ---------------------------------------------------------------
old_sig = """        learner_response: str,
        explicit_solution_request: bool = False,
    ) -> TutorAction:"""

new_sig = """        learner_response,
        explicit_solution_request: bool = False,
    ) -> TutorAction:"""

if "learner_response," in src and "learner_response: str," in src:
    src = src.replace(old_sig, new_sig, 1)
    print("Widened signature (removed str type hint)")
else:
    print("WARN: signature anchor not found")

# ---------------------------------------------------------------
# 3. Insert handling after event_id line
# ---------------------------------------------------------------
ANCHOR = '''        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
'''

INSERT = '''        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        # -------- Phase 2: accept WorkingSubmission or str --------
        if isinstance(learner_response, WorkingSubmission):
            submission = learner_response
            learner_state.session_events.append({
                "kind": "working_submitted",
                "step_count": len(submission.steps),
                "steps": submission.step_texts(),
                "source": submission.source,
            })
            learner_response = submission.last_line()
        # -------- end Phase 2 --------
'''

if "Phase 2: accept WorkingSubmission" not in src:
    if ANCHOR in src:
        src = src.replace(ANCHOR, INSERT, 1)
        print("Inserted WorkingSubmission handling")
    else:
        print("WARN: event_id anchor not found")
else:
    print("Phase 2 handling already present")

try:
    ast.parse(src)
    print("Syntax OK")
    P.write_text(src, encoding="utf-8")
    print("Engine written")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)