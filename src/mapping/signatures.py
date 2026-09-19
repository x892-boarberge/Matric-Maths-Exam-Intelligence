"""
Signature matching for Mapping v2.

A signature is a substring pattern paired with a topic_id. When the
pattern appears (case-insensitive) in the question text, that signature
votes for its topic.

Public functions:
    load_signatures()          -> DataFrame
    match_signatures(text, ...) -> list of matching dicts
    pick_best_signature(matches) -> single best dict or None

Ranking (used by pick_best_signature):
    1. usage_rule: PRIMARY > SECONDARY > FALLBACK
    2. confidence: high > medium > low
    3. signature_id: alphabetical (for determinism)
"""
from pathlib import Path
import pandas as pd

FROZEN_DIR = Path(__file__).parent / "frozen"

CONF_RANK = {"high": 3, "medium": 2, "low": 1}
USAGE_RANK = {"PRIMARY": 3, "SECONDARY": 2, "FALLBACK": 1}

REQUIRED_COLUMNS = {"topic_id", "signature_id", "pattern", "confidence", "usage_rule"}


def load_signatures(path: Path | None = None) -> pd.DataFrame:
    """
    Load the frozen signature list.

    If `path` is None, loads from `src/mapping/frozen/signatures_v2.csv`.
    Raises ValueError if required columns are missing.
    """
    path = path or (FROZEN_DIR / "signatures_v2.csv")
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Signatures file missing columns: {missing}")
    return df


def match_signatures(text, sig_df: pd.DataFrame, usage_filter: set | None = None):
    """
    Return every signature whose pattern appears in `text`.

    Args:
        text:           the question text to search
        sig_df:         the loaded signature DataFrame
        usage_filter:   if set, only include signatures whose usage_rule is
                        in this set (e.g. {"PRIMARY", "SECONDARY"})

    Returns:
        A list of dicts with keys:
            topic_id, signature_id, confidence, usage_rule, pattern
    """
    if not isinstance(text, str) or not text.strip():
        return []

    text_lower = text.lower()
    matches = []

    for _, row in sig_df.iterrows():
        if usage_filter and row["usage_rule"] not in usage_filter:
            continue
        pattern = str(row["pattern"]).lower()
        if pattern and pattern in text_lower:
            matches.append({
                "topic_id":     row["topic_id"],
                "signature_id": row["signature_id"],
                "confidence":   row["confidence"],
                "usage_rule":   row["usage_rule"],
                "pattern":      row["pattern"],
            })

    return matches


def pick_best_signature(matches):
    """
    Return the single highest-ranked signature, or None.

    Ranking order (highest first):
        usage_rule PRIMARY > SECONDARY > FALLBACK
        confidence high > medium > low
        signature_id alphabetical (deterministic tie-break)
    """
    if not matches:
        return None

    ranked = sorted(
        matches,
        key=lambda m: (
            USAGE_RANK.get(m["usage_rule"], 0),
            CONF_RANK.get(m["confidence"], 0),
            str(m["signature_id"]),
        ),
        reverse=True,
    )
    return ranked[0]