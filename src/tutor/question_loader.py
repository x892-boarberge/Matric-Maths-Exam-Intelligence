"""
Load real NSC questions from the mapped corpus + memo answers.

Overrides: for rows where the mapped topic_v2 is wrong, or the OCR text
is degraded, or the subtopic is missing, a per-year override file
(question_overrides_YYYY.csv) supplies the correct values.

Inputs:
    data/processed/memo_answers/memo_answers_YYYY.csv
    data/processed/memo_answers/question_overrides_YYYY.csv  (optional)
    data/processed/mapped/YYYY/question_topic_map_YYYY_v2.csv
"""
from pathlib import Path
from typing import List, Optional
import pandas as pd

from .schemas import Problem


ROOT = Path(__file__).resolve().parents[2]
MAP_DIR = ROOT / "data" / "processed" / "mapped"
MEMO_DIR = ROOT / "data" / "processed" / "memo_answers"


def _normalise(v) -> str:
    if pd.isna(v):
        return ""
    return str(v).replace(".0", "").strip()


def load_memo_answers(year: int) -> pd.DataFrame:
    path = MEMO_DIR / ("memo_answers_" + str(year) + ".csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_overrides(year: int) -> pd.DataFrame:
    path = MEMO_DIR / ("question_overrides_" + str(year) + ".csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_year_questions(year: int, paper: Optional[str] = None) -> List[Problem]:
    memo = load_memo_answers(year)
    if len(memo) == 0:
        return []

    overrides = load_overrides(year)

    mapped = pd.read_csv(
        MAP_DIR / str(year) / ("question_topic_map_" + str(year) + "_v2.csv")
    )

    # Normalise keys
    mapped["_q"] = mapped["question_number"].apply(_normalise)
    mapped["_s"] = mapped["subquestion"].apply(_normalise)
    memo["_q"] = memo["question_number"].apply(_normalise)
    memo["_s"] = memo["subquestion"].apply(_normalise)

    if len(overrides) > 0:
        overrides["_q"] = overrides["question_number"].apply(_normalise)
        overrides["_s"] = overrides["subquestion"].apply(_normalise)

    if paper:
        memo = memo[memo["paper"] == paper]

    mapped_slim = mapped[["_q", "_s", "question_text", "topic_v2"]].rename(
        columns={"question_text": "question_text_mapped",
                 "topic_v2": "topic_v2_mapped"}
    )

    joined = memo.merge(mapped_slim, on=["_q", "_s"], how="inner")

    if len(overrides) > 0:
        joined = joined.merge(
            overrides[["paper", "_q", "_s", "correct_topic_v2",
                       "clean_prompt", "clean_subtopic"]],
            on=["paper", "_q", "_s"],
            how="left",
        )
    else:
        joined["correct_topic_v2"] = None
        joined["clean_prompt"] = None
        joined["clean_subtopic"] = None

    problems = []
    for _, row in joined.iterrows():
        topic_v2 = row["correct_topic_v2"] if pd.notna(row["correct_topic_v2"]) else row["topic_v2_mapped"]
        prompt = row["clean_prompt"] if pd.notna(row["clean_prompt"]) else str(row["question_text_mapped"])[:500]
        subtopic = row["clean_subtopic"] if pd.notna(row["clean_subtopic"]) else ""

        problems.append(Problem(
            problem_id=str(year) + "_" + str(row["paper"]) + "_Q" + str(row["_q"]) + "_" + str(row["_s"]),
            skill_id=row["skill_id"],
            topic=topic_v2,
            subtopic=subtopic,
            structure_type="routine_calculation",
            prompt=str(prompt)[:500],
            expected_answer=str(row["expected_answer"]),
            topic_v2=topic_v2,
        ))
    return problems


def load_gold_2025():
    return load_year_questions(2025)
