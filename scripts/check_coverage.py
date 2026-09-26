from pathlib import Path
from collections import defaultdict

# What years do we have OCR pages for?
ocr_years = defaultdict(set)
for txt in Path("data/processed/diagrams/pages").glob("*_exam_maths_p*.txt"):
    stem = txt.stem
    parts = stem.rsplit("_p", 1)[0].split("_")
    if len(parts) >= 3:
        year = parts[0]
        paper = parts[2].upper()
        ocr_years[year].add(paper)

print("OCR exam pages by year:")
for year in sorted(ocr_years.keys()):
    papers = sorted(ocr_years[year])
    print(f"  {year}: {papers}")

# What years do we have topic maps for?
print()
print("Topic maps by year:")
for yd in sorted(Path("data/processed/mapped").glob("20*")):
    if yd.is_dir():
        files = list(yd.glob("question_topic_map_*_v2.csv"))
        print(f"  {yd.name}: {len(files)} map(s)")