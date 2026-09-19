"""
Gold set regression test for Mapping v2.

Verifies that the refactored pipeline reproduces the frozen result:
macro-F1 >= 0.95 on the 2025 P1 gold set (30 comparable rows).

If this test fails, the refactor changed behaviour and must be reverted.
"""
import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mapping.signatures import load_signatures
from src.mapping.structural import load_struct_rules
from src.mapping.lexicon import load_lexicon
from src.mapping.matcher import map_v2_final


GOLD_PATH  = ROOT / "data" / "processed" / "gold_sets" / "gold_2025_p1_labelled.csv"
MAP_2025   = ROOT / "data" / "processed" / "mapped" / "2025" / "question_topic_map_2025_v2.csv"
V1_V2_PATH = ROOT / "data" / "processed" / "taxonomy" / "v1_to_v2_topic_map.csv"

F1_THRESHOLD = 0.95


def norm_key(q, s):
    return f"{str(q).replace('.0','').strip()}|{str(s).replace('.0','').strip()}"


def norm_label(s):
    return str(s).replace("\xa0", " ").strip()


def test_gold_f1():
    sig_df = load_signatures()
    struct_rules = load_struct_rules()
    token_map = load_lexicon()

    gold = pd.read_csv(GOLD_PATH)
    mapped = pd.read_csv(MAP_2025)
    p1 = mapped[mapped["paper"] == "P1"].copy()

    # Re-map every row with the refactored pipeline
    p1["topic_v2_refactored"] = [
        map_v2_final(text, "P1", sig_df, token_map, struct_rules)["topic_id"]
        if isinstance(text, str) else None
        for text in p1["question_text"]
    ]

    # Build keys
    gold["_key"] = gold.apply(lambda r: norm_key(r["question_number"], r["subquestion"]), axis=1)
    p1["_key"] = p1.apply(lambda r: norm_key(r["question_number"], r["subquestion"]), axis=1)

    # Translate gold labels to v2
    v1_v2 = pd.read_csv(V1_V2_PATH)
    lookup = {norm_label(k): str(v).strip()
              for k, v in zip(v1_v2["v1_label"], v1_v2["v2_topic_id"])}
    gold["topic_gold_v2"] = gold["topic_gold"].apply(lambda x: lookup.get(norm_label(x)))

    # Join
    joined = gold[["_key", "topic_gold_v2"]].merge(
        p1[["_key", "topic_v2_refactored"]],
        on="_key", how="left",
    )
    valid = joined.dropna(subset=["topic_gold_v2", "topic_v2_refactored"])

    acc = accuracy_score(valid["topic_gold_v2"], valid["topic_v2_refactored"])
    f1 = f1_score(valid["topic_gold_v2"], valid["topic_v2_refactored"],
                  average="macro", zero_division=0)

    print(f"\nGold F1 after refactor: {f1:.3f}  (threshold {F1_THRESHOLD})")
    print(f"Comparable: {len(valid)}/49")
    print(f"Accuracy: {acc:.3f}")

    assert f1 >= F1_THRESHOLD, (
        f"Gold F1 dropped to {f1:.3f}. Refactor changed behaviour. Revert."
    )