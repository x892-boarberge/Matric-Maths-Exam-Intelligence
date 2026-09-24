"""
Load real NSC questions from mapped corpus + memo answers.
"""
from pathlib import Path
from typing import List, Optional, Tuple
import re
import pandas as pd
from .schemas import Problem


ROOT = Path(__file__).resolve().parents[2]
MAP_DIR = ROOT / "data" / "processed" / "mapped"
MEMO_DIR = ROOT / "data" / "processed" / "memo_answers"
_DIAGRAMS_PAGES_DIR = ROOT / "data" / "processed" / "diagrams" / "pages"


def _normalise(v) -> str:
    if pd.isna(v):
        return ""
    return str(v).replace(".0", "").strip()


def _clean_topic(v) -> str:
    if pd.isna(v) or v is None:
        return "UNMAPPED"
    s = str(v).strip()
    if s.lower() in ("nan", "none", ""):
        return "UNMAPPED"
    return s


def _clean_mapped_prompt(text, max_len=280):
    if not text or not isinstance(text, str):
        return ""
    s = str(text)
    boilerplate = [
        r"copyright reserved", r"please (turn|tum) over", r"nsc confidential",
        r"nsc/nss", r"dbe/november", r"mathematics[/\s]?p\d", r"wiskunde",
        r"bl[ao]ai om asseblief", r"grade 12", r"graad 12", r"basic education",
        r"department: basic education", r"senior certificate", r"national senior",
        r"marks/punte", r"these marking guidelines", r"hierdie nasienriglyne",
    ]
    kept = []
    for line in s.split("\n"):
        st = line.strip()
        if not st:
            continue
        if any(re.search(bp, st, re.IGNORECASE) for bp in boilerplate):
            continue
        if re.match(r"^\d+(\.\d+)*\.?\s*$", st):
            continue
        if re.match(r"^\[\d+\]?\s*$", st):
            continue
        kept.append(st)
    if not kept:
        return ""
    text = re.sub(r"\s+", " ", " ".join(kept)).strip()
    for pat, rep in [
        (r"\bof\s+/\b", "of f"), (r"\bf\s+/\s*\(", "f'("),
        (r"\bf\s*/\s*\(", "f("), (r"\bf\s*/\s*x", "f(x)"),
        (r"\bDetermine\s+f\s*/", "Determine f'"), (r"\bDy/", "dy/"),
        (r"\bTy\b", "T_91"), (r"\u2014", "-"), (r"\bem\b", "cm"),
    ]:
        text = re.sub(pat, rep, text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "..."
    return text


def _is_substantive(text, min_chars=30):
    if not text:
        return False
    t = str(text).strip()
    if len(t) < min_chars:
        return False
    if re.match(r"^\d+(\.\d+)*\.?$", t):
        return False
    return True


SKILL_SUBTOPIC_MAP = {
    "algebra.quadratic.solve": "Quadratic equations",
    "algebra.quadratic.inequality": "Quadratic inequalities",
    "algebra.quadratic.formula": "Quadratic formula",
    "algebra.surd.solve": "Surd equations",
    "algebra.exponential.solve": "Exponential equations",
    "algebra.exponential.proof": "Exponential proofs",
    "algebra.simultaneous.solve": "Simultaneous equations",
    "algebra.inequality": "Inequalities",
    "algebra.proof.integer": "Integer proofs",
    "sequences.ap.term": "Arithmetic sequences",
    "sequences.ap.difference": "Arithmetic sequences",
    "sequences.ap.sum": "Arithmetic series",
    "sequences.gp.term": "Geometric sequences",
    "sequences.gp.ratio": "Geometric sequences",
    "sequences.gp.sum": "Geometric series",
    "sequences.gp.sum_infinity": "Sum to infinity",
    "sequences.quadratic.term": "Quadratic sequences",
    "sequences.quadratic.general": "Quadratic sequences",
    "sequences.quadratic.n": "Quadratic sequences",
    "sequences.quadratic.difference": "Quadratic sequences",
    "sequences.quadratic.monotone": "Quadratic sequences",
    "functions.parabola.turning": "Parabola",
    "functions.parabola.range": "Parabola",
    "functions.parabola.intercept": "Parabola",
    "functions.parabola.intercepts": "Parabola",
    "functions.parabola.equation": "Parabola",
    "functions.parabola.tangent": "Parabola",
    "functions.parabola.parameter": "Parabola",
    "functions.hyperbola.domain": "Hyperbola",
    "functions.hyperbola.equation": "Hyperbola",
    "functions.hyperbola.intercept": "Hyperbola",
    "functions.hyperbola.asymptotes": "Hyperbola",
    "functions.hyperbola.range": "Hyperbola",
    "functions.hyperbola.parameter": "Hyperbola",
    "functions.hyperbola.translation": "Hyperbola",
    "functions.exponential.value": "Exponential functions",
    "functions.exponential.range": "Exponential functions",
    "functions.exponential.sketch": "Exponential functions",
    "functions.exponential.asymptote": "Exponential functions",
    "functions.exponential.intercept": "Exponential functions",
    "functions.exponential.transform": "Exponential functions",
    "functions.log.inverse": "Logarithmic functions",
    "functions.log.value": "Logarithmic functions",
    "functions.log.range": "Logarithmic functions",
    "functions.log.sketch": "Logarithmic functions",
    "functions.log.asymptote": "Logarithmic functions",
    "functions.log.intercept": "Logarithmic functions",
    "functions.line.equation": "Straight lines",
    "functions.line.intercept": "Straight lines",
    "functions.inequality": "Inequalities on graphs",
    "functions.transformation": "Transformations",
    "functions.inverse.domain": "Inverse functions",
    "functions.parameter": "Function parameters",
    "functions.distance.vertical": "Vertical distance",
    "functions.optimisation.length": "Optimisation",
    "finance.compound": "Compound interest",
    "finance.compound.r": "Compound interest",
    "finance.simple_interest": "Simple interest",
    "finance.effective": "Effective & nominal rates",
    "finance.annuity.future": "Future value annuities",
    "finance.loan.n": "Loan repayment",
    "finance.loan.final": "Loan repayment",
    "finance.loan.interest": "Loan repayment",
    "finance.depreciation.n": "Depreciation",
    "calculus.derivative.rules": "Differentiation rules",
    "calculus.derivative.first_principles": "First principles",
    "calculus.derivative.domain": "Differentiation rules",
    "calculus.cubic.turning": "Cubic graphs",
    "calculus.cubic.concave": "Concavity",
    "calculus.cubic.increasing": "Increasing & decreasing",
    "calculus.cubic.intercept": "Cubic graphs",
    "calculus.cubic.sketch": "Cubic graphs",
    "calculus.cubic.parameter": "Cubic graphs",
    "calculus.tangent": "Tangents",
    "calculus.tangent.angle": "Tangents",
    "calculus.optimisation.volume": "Optimisation",
    "calculus.optimisation.max": "Optimisation",
    "calculus.optimisation.min": "Optimisation",
    "calculus.optimisation.model": "Optimisation",
    "calculus.inequality": "Calculus inequalities",
    "calculus.inverse": "Inverse functions",
    "probability.independence": "Independence",
    "probability.union": "Union & intersection",
    "probability.two_way": "Two-way tables",
    "probability.venn": "Venn diagrams",
    "probability.tree": "Tree diagrams",
    "probability.conditional": "Conditional probability",
    "probability.counting": "Counting & arrangements",
    "probability.set": "Set probability",
    "stats.mean": "Mean",
    "stats.mean.parameter": "Mean",
    "stats.median": "Median",
    "stats.quartile": "Quartiles",
    "stats.iqr": "Interquartile range",
    "stats.standard_deviation": "Standard deviation",
    "stats.standard_deviation.interval": "Standard deviation",
    "stats.standard_deviation.invariance": "Standard deviation",
    "stats.regression.equation": "Regression",
    "stats.regression.predict": "Regression",
    "stats.regression.interpret": "Regression",
    "stats.regression.outlier": "Regression",
    "stats.correlation.r": "Correlation",
    "stats.correlation.interpret": "Correlation",
    "stats.frequency.count": "Frequency tables",
    "stats.frequency.cumulative": "Frequency tables",
    "stats.frequency.median_class": "Frequency tables",
    "stats.cumulative.total": "Frequency tables",
    "stats.boxplot": "Box plots",
    "stats.histogram": "Histograms",
    "stats.skewness": "Skewness",
    "stats.percentage": "Percentages",
    "stats.interval": "Intervals",
    "analytical_geom.distance": "Distance formula",
    "analytical_geom.midpoint": "Midpoint formula",
    "analytical_geom.gradient": "Gradient",
    "analytical_geom.inclination": "Angle of inclination",
    "analytical_geom.line_equation": "Line equations",
    "analytical_geom.circle.equation": "Circle equations",
    "analytical_geom.circle.radius": "Circle equations",
    "analytical_geom.circle.point": "Circle equations",
    "analytical_geom.circle.parameter": "Circle equations",
    "analytical_geom.tangent": "Tangents to circles",
    "analytical_geom.tangent.equation": "Tangents to circles",
    "analytical_geom.angle": "Angles in analytical geometry",
    "analytical_geom.area": "Area",
    "analytical_geom.area_ratio": "Area",
    "analytical_geom.parameter": "Parameters",
    "analytical_geom.point": "Points",
    "analytical_geom.ratio": "Ratio",
    "analytical_geom.translation": "Translations",
    "analytical_geom.prove": "Analytical proofs",
    "analytical_geom.parallelogram.prove": "Parallelogram proofs",
    "analytical_geom.circumcentre": "Circumcentre",
    "analytical_geom.collinear": "Collinearity",
    "trig.reduction.simplify": "Reduction formulae",
    "trig.reduction.cos": "Reduction formulae",
    "trig.reduction.range": "Reduction formulae",
    "trig.double_angle": "Double angle formulae",
    "trig.compound.sin": "Compound angle formulae",
    "trig.compound.prove": "Compound angle proofs",
    "trig.compound.expansion": "Compound angle formulae",
    "trig.equation": "Trig equations",
    "trig.equation.general": "General solutions",
    "trig.equation.min": "Trig equations",
    "trig.maximum": "Trig maxima & minima",
    "trig.minimum": "Trig maxima & minima",
    "trig.graph.period": "Trig graphs",
    "trig.graph.range": "Trig graphs",
    "trig.graph.inequality": "Trig graphs",
    "trig.graph.sketch": "Trig graphs",
    "trig.graph.transform": "Trig graphs",
    "trig.graph.value": "Trig graphs",
    "trig.graph.parameter": "Trig graphs",
    "trig.graph.key_points": "Trig graphs",
    "trig.3d.length": "3D trigonometry",
    "trig.3d.angle": "3D trigonometry",
    "trig.3d.area": "3D trigonometry",
    "trig.identity.prove": "Trig identities",
    "trig.identity.simplify": "Trig identities",
    "euclidean.circle.angle_centre": "Circle theorems",
    "euclidean.circle.angle": "Circle theorems",
    "euclidean.circle.radius": "Circle theorems",
    "euclidean.circle.equation": "Circle equations",
    "euclidean.cyclic_quad": "Cyclic quadrilaterals",
    "euclidean.tangent_chord": "Tangent-chord theorem",
    "euclidean.tangent.angle": "Tangent-chord theorem",
    "euclidean.semicircle.prove": "Angle in semicircle",
    "euclidean.semicircle.angle": "Angle in semicircle",
    "euclidean.prop_theorem": "Proportionality theorem",
    "euclidean.parallel": "Parallel lines",
    "euclidean.angle": "Angles",
    "euclidean.area_ratio": "Area ratios",
    "euclidean.similarity": "Similar triangles",
    "euclidean.similarity.ratio": "Similar triangles",
}

TOPIC_PREFIX = {
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


def _subtopic_from_skill(skill_id):
    if not skill_id:
        return ""
    sid = str(skill_id).strip()
    if sid in SKILL_SUBTOPIC_MAP:
        return SKILL_SUBTOPIC_MAP[sid]
    parts = sid.split(".")
    for i in range(len(parts) - 1, 0, -1):
        candidate = ".".join(parts[i-1:])
        if candidate in SKILL_SUBTOPIC_MAP:
            return SKILL_SUBTOPIC_MAP[candidate]
    return ""


def _topic_from_skill(skill_id):
    if not skill_id:
        return None
    s = str(skill_id).lower()
    for prefix, code in TOPIC_PREFIX.items():
        if s.startswith(prefix):
            return code
    return None


def _load_ocr_for_problem(problem_id):
    parts = str(problem_id).split("_")
    if len(parts) < 3:
        return ""
    year, paper = parts[0], parts[1]
    if not paper.startswith("P"):
        return ""
    stem = year + "_nov_p" + paper[1] + "_exam_maths"
    files = sorted(_DIAGRAMS_PAGES_DIR.glob(stem + "_p*.txt"))
    chunks = []
    for f in files:
        try:
            chunks.append(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
    return "\n".join(chunks)


def _extract_from_ocr(problem_id, subquestion):
    if not subquestion:
        return ""
    ocr = _load_ocr_for_problem(problem_id)
    if not ocr:
        return ""
    pattern = re.compile(r"(?:^|\n)\s*" + re.escape(subquestion) + r"\b", re.MULTILINE)
    m = pattern.search(ocr)
    if not m:
        return ""
    body = ocr[m.end():m.end() + 400]
    for cp in [
        re.compile(r"\n\s*\d+\.\d+\b"),
        re.compile(r"\n\s*QUESTION\s+\d+", re.IGNORECASE),
        re.compile(r"Copyright reserved", re.IGNORECASE),
        re.compile(r"Please turn over", re.IGNORECASE),
    ]:
        cm = cp.search(body)
        if cm and cm.start() > 20:
            body = body[:cm.start()]
    return _clean_mapped_prompt(body, max_len=280)


def load_memo_answers(year, paper=None):
    if paper:
        p = MEMO_DIR / ("memo_answers_" + str(year) + "_" + paper + ".csv")
        if p.exists():
            return pd.read_csv(p)
    p = MEMO_DIR / ("memo_answers_" + str(year) + ".csv")
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


def load_overrides(year):
    p = MEMO_DIR / ("question_overrides_" + str(year) + ".csv")
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def load_year_questions(year, paper=None):
    memo = load_memo_answers(year, paper=paper)
    if len(memo) == 0:
        return []
    overrides = load_overrides(year)
    map_path = MAP_DIR / str(year) / ("question_topic_map_" + str(year) + "_v2.csv")
    if not map_path.exists():
        return []
    mapped = pd.read_csv(map_path)
    mapped["_q"] = mapped["question_number"].apply(_normalise)
    mapped["_s"] = mapped["subquestion"].apply(_normalise)
    memo["_q"] = memo["question_number"].apply(_normalise)
    memo["_s"] = memo["subquestion"].apply(_normalise)
    if len(overrides) > 0:
        overrides["_q"] = overrides["question_number"].apply(_normalise)
        overrides["_s"] = overrides["subquestion"].apply(_normalise)
    if paper:
        memo = memo[memo["paper"] == paper]

    mapped_slim = mapped[["paper", "_q", "_s", "question_text", "topic_v2"]].rename(
        columns={"question_text": "question_text_mapped", "topic_v2": "topic_v2_mapped"}
    )
    joined = memo.merge(mapped_slim, on=["paper", "_q", "_s"], how="left")

    if len(overrides) > 0:
        joined = joined.merge(
            overrides[["paper", "_q", "_s", "correct_topic_v2", "clean_prompt", "clean_subtopic"]],
            on=["paper", "_q", "_s"], how="left",
        )
    else:
        joined["correct_topic_v2"] = None
        joined["clean_prompt"] = None
        joined["clean_subtopic"] = None

    problems = []
    for _, row in joined.iterrows():
        skill_str = str(row["skill_id"])
        topic_v2 = _topic_from_skill(skill_str)
        if topic_v2 is None:
            if pd.notna(row.get("correct_topic_v2")):
                topic_v2 = _clean_topic(row["correct_topic_v2"])
            else:
                topic_v2 = _clean_topic(row.get("topic_v2_mapped"))

        prompt = ""
        if pd.notna(row.get("clean_prompt")) and str(row["clean_prompt"]).strip():
            prompt = str(row["clean_prompt"]).strip()
        else:
            mapped_text = ""
            if pd.notna(row.get("question_text_mapped")):
                mapped_text = _clean_mapped_prompt(str(row["question_text_mapped"]))
            short_text = ""
            if pd.notna(row.get("question_text_short")):
                short_text = str(row["question_text_short"]).strip()
            if _is_substantive(mapped_text):
                prompt = mapped_text
            else:
                ocr_text = ""
                try:
                    pid = str(year) + "_" + str(row["paper"]) + "_Q" + str(row["_q"]) + "_" + str(row["_s"])
                    ocr_text = _extract_from_ocr(pid, str(row["_s"]))
                except Exception:
                    ocr_text = ""
                if _is_substantive(ocr_text, min_chars=25):
                    prompt = ocr_text
                elif short_text:
                    prompt = short_text
                elif mapped_text:
                    prompt = mapped_text
                else:
                    prompt = "(question text not available)"

        subtopic = ""
        if pd.notna(row.get("clean_subtopic")) and str(row.get("clean_subtopic")).strip():
            subtopic = str(row["clean_subtopic"]).strip()
        else:
            subtopic = _subtopic_from_skill(skill_str)

        problems.append(Problem(
            problem_id=str(year) + "_" + str(row["paper"]) + "_Q" + str(row["_q"]) + "_" + str(row["_s"]),
            skill_id=row["skill_id"],
            topic=topic_v2,
            subtopic=subtopic,
            structure_type="routine_calculation",
            prompt=prompt[:500],
            expected_answer=str(row["expected_answer"]),
            topic_v2=topic_v2,
        ))
    return problems


def discover_papers():
    found = set()
    for p in MEMO_DIR.glob("memo_answers_*_P*.csv"):
        parts = p.stem.split("_")
        if len(parts) >= 4:
            try:
                yr = int(parts[2])
                pap = parts[3]
                if pap in ("P1", "P2"):
                    found.add((yr, pap))
            except ValueError:
                continue
    return sorted(found)


def load_corpus():
    problems = []
    for year, paper in discover_papers():
        problems.extend(load_year_questions(year, paper=paper))
    return problems


def load_gold_2025():
    return load_year_questions(2025)