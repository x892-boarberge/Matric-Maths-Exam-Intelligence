"""Rewrite _light_normalise and add the near-miss renderer branch."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MATCHER = ROOT / "src" / "tutor" / "answer_matcher.py"
ENGINE  = ROOT / "src" / "tutor" / "tutor_engine.py"

# ---------- 1. Rewrite _light_normalise ----------
m_src = MATCHER.read_text(encoding="utf-8")

new_light = '''def _light_normalise(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = s.replace("\\u2265", ">=").replace("\\u2264", "<=").replace("\\u2260", "!=")
    s = s.replace("\\u00d7", "*").replace("\\u00b7", "*").replace("\\u22c5", "*")
    s = s.replace("\\u2212", "-").replace("\\u2013", "-").replace("\\u2014", "-")
    s = s.replace("**", "^")
    s = re.sub(r"\\s+", " ", s)
    s = re.sub(r"\\b0r\\b", "or", s)
    s = re.sub(r"\\b0 r\\b", "or", s)
    s = re.sub(r"[.,;!?]+\\s*$", "", s)
    return s'''

pattern = re.compile(
    r"def _light_normalise\(s: str\) -> str:.*?\n    return s\n",
    re.DOTALL,
)
if pattern.search(m_src):
    # Use a lambda so Python does not interpret backslashes in new_light
    # as regex replacement escapes.
    m_src = pattern.sub(lambda _m: new_light + "\n", m_src, count=1)
    MATCHER.write_text(m_src, encoding="utf-8")
    print("_light_normalise rewritten")
else:
    print("WARNING - _light_normalise block not matched")

# ---------- 2. Add near-miss renderer branch ----------
e_src = ENGINE.read_text(encoding="utf-8")

if "I read your answer as" in e_src:
    print("Renderer already has near-miss branch")
else:
    old = '''        if a == ActionType.ACKNOWLEDGE_CORRECT:
            return "Good — that step is correct. Let\'s keep going."'''

    new = '''        # Near-miss clarification
        if getattr(d, "rule_id", None) == "D_NEAR_MISS":
            learner = ctx.get("learner_response", "")
            expected = ctx["problem"].expected_answer
            return ("I read your answer as \'" + str(learner) + "\'. "
                    "That looks close to the target. Did you mean " + str(expected) + "?")

        if a == ActionType.ACKNOWLEDGE_CORRECT:
            return "Good — that step is correct. Let\'s keep going."'''

    if old in e_src:
        e_src = e_src.replace(old, new, 1)
        ENGINE.write_text(e_src, encoding="utf-8")
        print("Near-miss renderer branch added")
    else:
        print("WARNING - ACKNOWLEDGE_CORRECT block not found")

print("done")
