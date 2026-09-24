"""
Memo answer extractor v2.
- better answer-line selection: prefer lines after the LAST checkmark
- normalizer for comparison
"""
import re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TXT_DIR = ROOT / "data" / "processed" / "extracted_text_v2"
OUT_DIR = ROOT / "data" / "processed" / "memo_answers"

QNUM_RE = re.compile(r"^\s*(\d+(?:\.\d+){1,2})\b")
CHECK_RE = re.compile(r"✓")
END_RE   = re.compile(r"^\s*\(\d+\)\s*$")


def normalise(s: str) -> str:
    """For comparison only — unify minus, comma-decimal, whitespace, checkmarks."""
    if not s:
        return ""
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    s = s.replace("✓", "").replace("✔", "")
    # comma decimal → period decimal (e.g. 0,26 -> 0.26)
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip("- ").strip()
    return s.lower()


def find_blocks(text):
    lines = text.splitlines()
    current = None
    buf = []
    for line in lines:
        m = QNUM_RE.match(line)
        if m and len(line) < 200:
            if current:
                yield current, buf
            current = m.group(1)
            buf = [line]
        else:
            if current is not None:
                buf.append(line)
    if current:
        yield current, buf


def extract_answer(lines):
    """Pick best answer line from a block's lines."""
    # strip empties but keep index
    nonempty = [(i, l.strip()) for i, l in enumerate(lines) if l.strip()]
    if not nonempty:
        return ""

    # find last checkmark line
    last_check = -1
    for i, l in nonempty:
        if CHECK_RE.search(l):
            last_check = i

    candidates = []
    for i, l in nonempty:
        # skip question-number line
        if QNUM_RE.match(l) and len(l) < 20:
            continue
        # skip end marks
        if END_RE.match(l):
            continue
        # skip pure checkmarks
        if l.replace("✓", "").strip() == "":
            continue
        # require some content signal
        if "=" not in l and "or" not in l.lower() and "<" not in l and ">" not in l and "≤" not in l and "≥" not in l:
            continue
        # score
        score = 0
        if i > last_check and last_check >= 0:
            score += 10
        if " or " in l.lower():
            score += 4
        if re.search(r"[xy]\s*=\s*[-]?\d", l):
            score += 5
        if "<" in l or ">" in l or "≤" in l or "≥" in l:
            score += 3
        # prefer shorter, cleaner lines
        L = len(l)
        if L < 50:
            score += 3
        if L < 80:
            score += 1
        score -= L / 200.0
        candidates.append((score, l))

    if not candidates:
        return ""
    candidates.sort(key=lambda t: -t[0])
    return candidates[0][1]


def extract_year(year):
    rows = []
    for key in (f"{year}_nov_p1_memo_maths", f"{year}_nov_p2_memo_maths"):
        p = TXT_DIR / (key + ".txt")
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        if len(text) < 100:
            print(f"  SKIP empty: {p.name}")
            continue
        paper = "P1" if "_p1_" in key else "P2"
        seen = set()
        for qnum, block in find_blocks(text):
            if qnum in seen:
                continue
            seen.add(qnum)
            ans = extract_answer(block)
            if not ans:
                continue
            q_text = block[0][len(qnum):].strip() if block else ""
            rows.append({
                "year": year,
                "paper": paper,
                "question_number": qnum.split(".")[0],
                "subquestion": qnum,
                "expected_answer": ans,
                "question_text_short": q_text[:120],
            })
    return pd.DataFrame(rows)


def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    df = extract_year(year)
    out = OUT_DIR / f"memo_answers_{year}_extracted.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nWrote {len(df)} rows -> {out}")


if __name__ == "__main__":
    main()
