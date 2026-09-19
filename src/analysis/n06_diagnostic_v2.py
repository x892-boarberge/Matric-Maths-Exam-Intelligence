"""
N06 Diagnostic Difficulty v2.

Produces three separate columns per topic_v2:
  - difficulty_norm         : from average performance (the hard number)
  - error_pressure_norm     : from error text (the soft signal)
  - severe_pressure_norm    : from severe language

They are NOT blended. Consumers pick the right signal for their purpose.
  N07 priority  -> difficulty_norm
  N08 design    -> error_pressure_norm, severe_pressure_norm
  Tutor layer   -> both, with different uses
"""
from pathlib import Path
from collections import Counter
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / "data" / "processed" / "diagnostics"
TAX = ROOT / "data" / "processed" / "taxonomy"
MAP = ROOT / "data" / "processed" / "mapped"
OUT = ROOT / "data" / "processed" / "analysis_v2"
OUT.mkdir(parents=True, exist_ok=True)

ALL_YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020,
             2021, 2022, 2023, 2024, 2025]

SEVERE_WORDS = ["severe", "very poor", "extremely weak", "major",
                "fundamental", "widespread", "unable to", "could not",
                "serious", "lack of"]


def load_mapped_corpus():
    frames = []
    for year in ALL_YEARS:
        p = MAP / str(year) / ("question_topic_map_" + str(year) + "_v2.csv")
        if p.exists():
            df = pd.read_csv(p)
            df["year"] = year
            frames.append(df)
    return pd.concat(frames, ignore_index=True, sort=False)


def build_question_to_topic(corpus):
    valid = corpus[corpus["topic_v2"].notna()].copy()
    lookup = {}
    for key, group in valid.groupby(["year", "paper", "question_number"]):
        votes = Counter(group["topic_v2"])
        lookup[key] = votes.most_common(1)[0][0]
    return lookup


def is_severe(text):
    if not isinstance(text, str):
        return False
    low = text.lower()
    return any(w in low for w in SEVERE_WORDS)


def main():
    corpus = load_mapped_corpus()
    q_to_topic = build_question_to_topic(corpus)

    # --- Performance data (12 years) ---
    perf = pd.read_csv(DIAG / "performance_all_years.csv")
    perf["topic_v2"] = perf.apply(
        lambda r: q_to_topic.get((r["year"], r["paper"], r["question_number"])),
        axis=1,
    )
    matched = perf["topic_v2"].notna().sum()
    print("Performance rows: " + str(len(perf)) + ", matched to topic: " + str(matched))
    print()

    perf_agg = perf.dropna(subset=["topic_v2", "avg_performance_pct"]).groupby("topic_v2").agg(
        n_questions=("avg_performance_pct", "count"),
        mean_performance=("avg_performance_pct", "mean"),
        min_performance=("avg_performance_pct", "min"),
    ).reset_index()
    perf_agg["mean_performance"] = perf_agg["mean_performance"].round(2)
    perf_agg["min_performance"] = perf_agg["min_performance"].round(2)
    perf_agg["difficulty_norm"] = (1 - perf_agg["mean_performance"] / 100).round(4)

    # --- Error text (2023-2025) ---
    errors = pd.read_csv(DIAG / "diagnostic_errors_v1.csv")
    errors = errors[errors["topic"] != "Unmapped"].copy()

    v1_to_v2 = pd.read_csv(TAX / "v1_to_v2_topic_map.csv")
    translation = dict(zip(v1_to_v2["v1_label"], v1_to_v2["v2_topic_id"]))
    errors["topic_v2"] = errors["topic"].map(translation)
    errors = errors[errors["topic_v2"].notna()].copy()
    errors["severe"] = errors["error_text_raw"].apply(is_severe)

    err_agg = errors.groupby("topic_v2").agg(
        error_count=("error_text_raw", "count"),
        severe_count=("severe", "sum"),
    ).reset_index()

    # Normalise error counts to [0, 1]
    if err_agg["error_count"].max() > 0:
        err_agg["error_pressure_norm"] = (
            err_agg["error_count"] / err_agg["error_count"].max()
        ).round(4)
    else:
        err_agg["error_pressure_norm"] = 0.0
    if err_agg["severe_count"].max() > 0:
        err_agg["severe_pressure_norm"] = (
            err_agg["severe_count"] / err_agg["severe_count"].max()
        ).round(4)
    else:
        err_agg["severe_pressure_norm"] = 0.0

    # --- Combine without blending ---
    combined = perf_agg.merge(err_agg, on="topic_v2", how="outer").fillna(0)
    combined = combined.sort_values("difficulty_norm", ascending=False)

    out = OUT / "difficulty_v2.csv"
    combined.to_csv(out, index=False)

    print("Wrote: " + str(out))
    print()
    print(combined[[
        "topic_v2", "n_questions", "mean_performance",
        "difficulty_norm", "error_count", "error_pressure_norm"
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
