import pymupdf
from pathlib import Path

SRC = Path("data/raw/memos")
DST = Path("data/processed/extracted_text_v2")
DST.mkdir(parents=True, exist_ok=True)

for pdf in sorted(SRC.glob("*_memo_maths.pdf")):
    doc = pymupdf.open(pdf)
    text = "\n".join(page.get_text(sort=True) for page in doc)
    out = DST / (pdf.stem + ".txt")
    out.write_text(text, encoding="utf-8")
    print(f"{pdf.name} -> {out.name} ({len(text)} chars)")
