"""
Priority v2 with real difficulty.

Combines four signals:
  exposure      (question count in 12-year corpus)
  difficulty    (from n06 diagnostic v2)
  persistence   (years present in corpus)
  design_weight (CAPS mark allocation)

Outputs data/processed/analysis_v2/priority_v2.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "processed" / "mapped"
DIAG = ROOT / "data" / "processed" / "diagnostics"
ANALYSIS = ROOT / "data" / "processed" / "analysis_v2"

ALL_YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020,
             2021, 2022, 2023, 2024, 2025]

WEIGHTS = {
    "exposure": 0.30,
    "difficulty": 0.40,
    "persistence": 0.20,
    "design_weight": 0.10,
}

DESIGN_MARKS = {
    "ALG": 25, "SEQ": 25, "FIN": 15, "FUNC": 35, "CALC": 35, "PROB": 15,
    "STAT": 20, "AGEO": 40, "TRIG": 40, "EUCL": 50,
}


def load_corpus():
    frames = []
    for year in ALL_YEARS:
        p = MAP / str(year) / ("question_topic_map_" + str(year) + "_v2.csv")
        if p.exists():
            df = pd.read_csv(p)
            df["year"] = year
            frames.append(df)
    return pd.concat(frames, ignore_index=True, sort=False)


def main():
    corpus = load_corpus()
    corpus = corpus[corpus["topic_v2"].notna()].copy()

    # Exposure
    exp = corpus.groupby("topic_v2").agg(
        n_questions=("subquestion", "count"),
        total_marks=("marks", "sum"),
    ).reset_index()
    exp["total_marks"] = exp["total_marks"].fillna(0)

    # Persistence
    pers = corpus.groupby("topic_v2")["year"].nunique().reset_index()
    pers.columns = ["topic_v2", "years_present"]
    pers["persistence_norm"] = pers["years_present"] / len(ALL_YEARS)

    # Design weight
    exp["design_marks"] = exp["topic_v2"].map(DESIGN_MARKS).fillna(0)

    # Load real difficulty
    diff = pd.read_csv(ANALYSIS / "difficulty_v2.csv")
    diff = diff[["topic_v2", "difficulty_norm", "mean_performance"]]

    # Combine
    df = exp.merge(pers, on="topic_v2", how="left").merge(diff, on="topic_v2", how="left")
    df["difficulty_norm"] = df["difficulty_norm"].fillna(0.5)

    # Normalise exposure and design to [0, 1]
    def norm(series):
        lo, hi = series.min(), series.max()
        if hi == lo:
            return series * 0 + 0.5
        return (series - lo) / (hi - lo)

    df["exposure_norm"] = norm(df["n_questions"]).round(4)
    df["design_norm"] = norm(df["design_marks"]).round(4)

    # Priority score
    df["priority_score"] = (
        WEIGHTS["exposure"] * df["exposure_norm"]
        + WEIGHTS["difficulty"] * df["difficulty_norm"]
        + WEIGHTS["persistence"] * df["persistence_norm"]
        + WEIGHTS["design_weight"] * df["design_norm"]
    ).round(4)

    df = df.sort_values("priority_score", ascending=False).reset_index(drop=True)

    out = ANALYSIS / "priority_v2.csv"
    df.to_csv(out, index=False)

    print("Wrote: " + str(out))
    print()
    print("Weights: " + str(WEIGHTS))
    print()
    cols = ["topic_v2", "n_questions", "mean_performance",
            "difficulty_norm", "exposure_norm", "persistence_norm",
            "design_norm", "priority_score"]
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
