"""
Lexicon matching for Mapping v2.

The lexicon is a weighted token -> topic table built from co-occurrence
statistics over the 12-year corpus. Tokens carry a weight (raw count or
lift). Tokens below `min_lift` are ignored. Tokens in LEXICON_BLACKLIST
never vote.

A single question may contain tokens that vote for different topics.
The function `match_lexicon` returns the winning topic only if it beats
the runner-up by a clear margin.

Public functions:
    load_lexicon()                     -> dict token -> [{topic_id, weight}]
    match_lexicon(text, token_map)     -> list of (topic_id, weight), sorted
"""
from pathlib import Path
from collections import Counter
import re
import pandas as pd

FROZEN_DIR = Path(__file__).parent / "frozen"


# Generic exam words. These appear in every paper and carry no topic signal.
LEXICON_BLACKLIST = {
    "value", "values", "calculate", "determine", "show", "solve", "find",
    "given", "work", "answer", "question", "hence", "write", "state",
    "number", "numbers", "total", "time", "times", "amount", "using",
    "draw", "sketch", "explain", "describe", "above", "below", "following",
    "first", "second", "third", "without", "calculator",
    "correct", "two", "decimal", "places", "written", "ways",
    "year", "years", "month", "months", "day", "days",
    "period", "periods", "term", "terms",
    "rate", "growth", "increase", "decrease",
    "graph", "graphs", "point", "points", "line", "lines",
    "length", "area",
}


def load_lexicon(path: Path | None = None) -> dict:
    """
    Load frozen lexicon from CSV.

    CSV columns: token, topic_id, weight
    Returns: dict mapping token (str) -> list of {topic_id, weight}
    """
    path = path or (FROZEN_DIR / "lexicon_v2.csv")
    df = pd.read_csv(path)

    token_map: dict = {}
    for _, row in df.iterrows():
        token = str(row["token"]).strip().lower()
        if not token:
            continue
        token_map.setdefault(token, []).append({
            "topic_id": row["topic_id"],
            "weight":   float(row["weight"]),
        })
    return token_map


def match_lexicon(text, token_map: dict, min_lift: float = 2.5, top_n: int = 2):
    """
    Vote for topics using tokens found in `text`.

    Args:
        text:      the question text
        token_map: output of load_lexicon()
        min_lift:  minimum weight for a token to count as a vote
        top_n:     how many top topics to return

    Returns:
        List of (topic_id, total_weight) sorted descending.
        Empty list if no clear winner.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Normalise text: lowercase, keep alpha + space
    text_lower = re.sub(r"[^a-z\s]", " ", text.lower())
    tokens = set(text_lower.split())

    votes: Counter = Counter()
    for token in tokens:
        if token in LEXICON_BLACKLIST:
            continue
        for entry in token_map.get(token, []):
            if entry["weight"] >= min_lift:
                votes[entry["topic_id"]] += entry["weight"]

    ranked = votes.most_common(top_n)
    if not ranked:
        return []

    # Require a clear winner (1.5x the runner-up). Prevents ties.
    if len(ranked) > 1 and ranked[0][1] < 1.5 * ranked[1][1]:
        return []

    return ranked