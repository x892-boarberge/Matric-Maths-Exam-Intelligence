"""Patch diagnosis.py to add the 69 trigger-based misconceptions as a second layer."""
from pathlib import Path
import ast

P = Path("src/tutor/diagnosis.py")
src = P.read_text(encoding="utf-8-sig")

# ---------------------------------------------------------------
# 1. Insert trigger library loader before the RuleFn declaration
# ---------------------------------------------------------------
ANCHOR_1 = "RuleFn = Callable[[str, str], bool]"

HELPERS = '''# ------------------------------------------------------------------
# N08 v2 — trigger-based fallback layer
# Loads 69 misconceptions from misconceptions_v2.csv.
# Fires only when skill-scoped rules miss, gated by topic.
# ------------------------------------------------------------------

_TRIGGER_LIBRARY = None


def _load_trigger_library():
    """Load the trigger regexes from misconceptions_v2.csv (cached)."""
    global _TRIGGER_LIBRARY
    if _TRIGGER_LIBRARY is not None:
        return _TRIGGER_LIBRARY

    import pandas as pd
    path = Path(__file__).resolve().parents[2] / "data" / "processed" / "tutor" / "misconceptions_v2.csv"
    if not path.exists():
        _TRIGGER_LIBRARY = []
        return _TRIGGER_LIBRARY

    try:
        df = pd.read_csv(path)
    except Exception:
        _TRIGGER_LIBRARY = []
        return _TRIGGER_LIBRARY

    rules = []
    for _, row in df.iterrows():
        try:
            pattern = re.compile(str(row["trigger_pattern"]), re.IGNORECASE)
        except re.error:
            continue
        rules.append({
            "mid": str(row["misconception_id"]).strip(),
            "topic": str(row["topic"]).strip(),
            "error_class": str(row["error_class"]).strip(),
            "description": str(row["description"]).strip(),
            "pattern": pattern,
            "severity": str(row["severity"]).strip(),
        })
    _TRIGGER_LIBRARY = rules
    return rules


_TOPIC_PREFIX = {
    "algebra.": "ALG",
    "sequences.": "SEQ",
    "functions.": "FUNC",
    "finance.": "FIN",
    "calculus.": "CALC",
    "probability.": "PROB",
    "trig.": "TRIG",
    "euclidean.": "EUCL",
    "analytical_geom.": "AGEO",
    "stats.": "STAT",
}


def _topic_from_skill(skill_id: str):
    if not skill_id:
        return None
    s = str(skill_id).lower()
    for prefix, code in _TOPIC_PREFIX.items():
        if s.startswith(prefix):
            return code
    return None


_CLASS_TO_ERROR_TYPE = {
    "procedural":   ErrorType.PROCEDURAL,
    "conceptual":   ErrorType.CONCEPTUAL,
    "notation":     ErrorType.REPRESENTATION,
    "presentation": ErrorType.PROCEDURAL,
    "reading":      ErrorType.STRATEGY,
    "arithmetic":   ErrorType.ARITHMETIC,
    "general":      ErrorType.UNKNOWN,
}


def _error_type_for_class(cls: str) -> ErrorType:
    return _CLASS_TO_ERROR_TYPE.get(str(cls).lower(), ErrorType.UNKNOWN)


'''

if ANCHOR_1 in src and "_load_trigger_library" not in src:
    src = src.replace(ANCHOR_1, HELPERS + ANCHOR_1, 1)
    print("Inserted trigger library helpers")
else:
    print("WARN: anchor 1 missing or already patched")


# ---------------------------------------------------------------
# 2. Insert fallback loop in diagnose() before final D_UNKNOWN return
# ---------------------------------------------------------------
ANCHOR_2 = '''    for mid, etype, expl, pred in RULES.get(skill_id, []):
        if pred(nr, expected_answer):
            return DiagnosisResult(
                error_type=etype,
                misconception_id=mid,
                confidence=0.85,
                rule_id=f"D_{mid}",
                explanation=expl,
            )'''

FALLBACK = ANCHOR_2 + '''

    # Layer 2 — trigger-based fallback (N08 v2)
    topic_hint = _topic_from_skill(skill_id)
    for rule in _load_trigger_library():
        if topic_hint and rule["topic"] not in (topic_hint, "GEN"):
            continue
        if rule["pattern"].search(nr):
            return DiagnosisResult(
                error_type=_error_type_for_class(rule["error_class"]),
                misconception_id=rule["mid"],
                confidence=0.65,
                rule_id=f"D_TRIGGER_{rule['mid']}",
                explanation=rule["description"],
            )'''

if ANCHOR_2 in src and "Layer 2 — trigger-based fallback" not in src:
    src = src.replace(ANCHOR_2, FALLBACK, 1)
    print("Inserted trigger fallback loop")
else:
    print("WARN: anchor 2 missing or already patched")


# ---------------------------------------------------------------
# 3. Update reachable_misconception_ids to include triggers
# ---------------------------------------------------------------
ANCHOR_3 = '''def reachable_misconception_ids() -> set[str]:
    ids = set()
    for rules in RULES.values():
        for mid, *_ in rules:
            ids.add(mid)
    return ids'''

NEW_3 = '''def reachable_misconception_ids() -> set[str]:
    ids = set()
    for rules in RULES.values():
        for mid, *_ in rules:
            ids.add(mid)
    for rule in _load_trigger_library():
        ids.add(rule["mid"])
    return ids'''

if ANCHOR_3 in src:
    src = src.replace(ANCHOR_3, NEW_3, 1)
    print("Updated reachable_misconception_ids")
else:
    print("WARN: anchor 3 missing")


# ---------------------------------------------------------------
# Verify syntax and write
# ---------------------------------------------------------------
try:
    ast.parse(src)
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)
    raise SystemExit(1)

P.write_text(src, encoding="utf-8")
print("diagnosis.py written")