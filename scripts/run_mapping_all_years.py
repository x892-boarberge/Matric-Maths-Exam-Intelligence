"""Run Mapping v2 across every year that has a v2 file."""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.mapping.signatures import load_signatures
from src.mapping.structural import load_struct_rules
from src.mapping.lexicon import load_lexicon
from src.mapping.matcher import map_v2_final

MAP_DIR = ROOT / "data" / "processed" / "mapped"

ALL_YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020,
             2021, 2022, 2023, 2024, 2025]


def map_year(year, sig_df, token_map, struct_rules):
    path = MAP_DIR / str(year) / ("question_topic_map_" + str(year) + "_v2.csv")
    if not path.exists():
        print(str(year) + ": file not found, skip")
        return 0

    df = pd.read_csv(path)
    rows = []
    for _, row in df.iterrows():
        text = row.get("question_text")
        paper = row.get("paper", "P1")
        pred = map_v2_final(text, paper, sig_df, token_map, struct_rules)
        new_row = row.to_dict()
        new_row["topic_v2"] = pred["topic_id"]
        new_row["mapping_method_v2"] = pred["method"]
        new_row["mapping_confidence_v2"] = pred["confidence"]
        new_row["signature_id_v2"] = pred["signature_id"]
        rows.append(new_row)

    pd.DataFrame(rows).to_csv(path, index=False)
    return len(rows)


def main():
    sig_df = load_signatures()
    struct_rules = load_struct_rules()
    token_map = load_lexicon()

    print("Loaded: " + str(len(sig_df)) + " signatures, "
          + str(len(struct_rules)) + " struct rules, "
          + str(len(token_map)) + " lexicon tokens")
    print()

    for year in ALL_YEARS:
        n = map_year(year, sig_df, token_map, struct_rules)
        if n:
            print(str(year) + ": " + str(n) + " rows re-mapped")


if __name__ == "__main__":
    main()
