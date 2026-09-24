"""
OCR each rendered page PNG, extract QUESTION N markers per page,
build the question->page map.

Fixed: sort by numeric page number, and keep the LOWEST page per question.
"""
import json
import re
import subprocess
import shutil
from pathlib import Path

ROOT = Path(".").resolve()
PAGES = ROOT / "data" / "processed" / "diagrams" / "pages"
OUT = ROOT / "data" / "processed" / "diagrams" / "question_page_map.json"

QUESTION_RE = re.compile(r"QUESTION\s+(\d+)", re.IGNORECASE)

tess = shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print("Using tesseract: " + tess)


def page_sort_key(p: Path):
    stem, pnum = p.stem.rsplit("_p", 1)
    return (stem, int(pnum))


pngs = sorted(PAGES.glob("*.png"), key=page_sort_key)
print("Pages to process: " + str(len(pngs)))

full_map = {}

for i, png in enumerate(pngs, 1):
    stem, pnum_str = png.stem.rsplit("_p", 1)
    pnum = int(pnum_str)

    ocr_txt = png.with_suffix(".txt")
    if not ocr_txt.exists():
        subprocess.run(
            [tess, str(png), str(png.with_suffix(""))],
            capture_output=True, check=False,
        )
    if not ocr_txt.exists():
        continue
    text = ocr_txt.read_text(encoding="utf-8", errors="ignore")

    for m in QUESTION_RE.finditer(text):
        q = m.group(1)
        full_map.setdefault(stem, {})
        # Keep the LOWEST page number for each question
        if q not in full_map[stem] or pnum < full_map[stem][q]:
            full_map[stem][q] = pnum

    if i % 50 == 0:
        print("  processed " + str(i) + "/" + str(len(pngs)))

OUT.write_text(json.dumps(full_map, indent=2, sort_keys=True), encoding="utf-8")
print()
print("=" * 60)
print("Papers mapped: " + str(len(full_map)))
for stem in sorted(full_map.keys())[:3]:
    pairs = sorted(full_map[stem].items(), key=lambda kv: int(kv[0]))
    print("  " + stem + ": " + str(pairs))
