"""Add WorkingStep + WorkingSubmission dataclasses to schemas.py."""
from pathlib import Path
import ast

P = Path("src/tutor/schemas.py")
src = P.read_text(encoding="utf-8-sig")

if "class WorkingStep" in src:
    print("Already present — skipping")
    raise SystemExit(0)

ANCHOR = "@dataclass\nclass DiagnosisResult:"

NEW = '''@dataclass
class WorkingStep:
    index: int
    raw_text: str
    source: str = "typed"          # "typed" | "photo" | "stylus"
    timestamp: Optional[float] = None
    confidence: Optional[float] = None
    corrections: int = 0           # crossings out (photo only)
    pause_ms: Optional[int] = None
    is_diagram_step: bool = False


@dataclass
class WorkingSubmission:
    steps: List[WorkingStep]
    source: str = "typed"
    final_answer: Optional[str] = None
    diagram: Optional[Dict[str, Any]] = None

    def last_line(self) -> str:
        return self.steps[-1].raw_text if self.steps else ""

    def joined(self) -> str:
        return "\\n".join(s.raw_text for s in self.steps)

    def step_texts(self):
        return [s.raw_text for s in self.steps]


@dataclass
class DiagnosisResult:'''

if ANCHOR in src:
    src = src.replace(ANCHOR, NEW, 1)
    try:
        ast.parse(src)
        P.write_text(src, encoding="utf-8")
        print("Added WorkingStep + WorkingSubmission")
    except SyntaxError as e:
        print("SYNTAX ERROR:", e)
else:
    print("WARN: anchor not found")