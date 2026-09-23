"""Add explicit no-over-revealing rule to the phraser prompt."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "tutor" / "llm_phraser.py"
src = P.read_text(encoding="utf-8")

old = '''NEVER: describe the learner, echo input, give the answer, use
"you must" / "you should" / "just" / "obvious" / "as an AI",
sound like a therapist, output labels like "learner:".'''

new = '''NEVER: describe the learner, echo input, give the answer, use
"you must" / "you should" / "just" / "obvious" / "as an AI",
sound like a therapist, output labels like "learner:".

CRITICAL: do NOT expand the hint into more steps than it contains.
If the hint says "Set x + 5 = 0", do not add "so x = -5".
If the hint says "differentiate the outer function", do not continue
into the inner function or the final derivative.
Rephrase only the text you were given. Do not add reasoning steps,
answers, or conclusions that were not in the hint.'''

if old in src:
    src = src.replace(old, new, 1)
    P.write_text(src, encoding="utf-8")
    print("Phraser prompt tightened")
else:
    print("WARNING - prompt block not found")
