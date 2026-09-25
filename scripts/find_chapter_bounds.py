import pymupdf
import re
from pathlib import Path

PDF_DIR = Path("data/raw/diagnostic_reports")

for year in [2015, 2018, 2019]:
    pdf = PDF_DIR / f"{year}_maths_diagnostic_part1.pdf"
    if not pdf.exists():
        print(f"{year}: NOT FOUND")
        continue
    doc = pymupdf.open(pdf)
    print(f"=== {year} ({len(doc)} pages) ===")

    # Find CHAPTER 10 MATHEMATICS
    ch10_start = None
    next_ch = None
    for i in range(len(doc)):
        text = doc[i].get_text("text")
        if ch10_start is None and "CHAPTER 10" in text and "MATHEMATICS" in text.upper():
            ch10_start = i + 1
        elif ch10_start and next_ch is None and re.search(
            r"CHAPTER 1[1-9]|PHYSICAL SCIENCES|ACCOUNTING|LIFE SCIENCES|ECONOMICS",
            text, re.I
        ):
            next_ch = i + 1

    print(f"  Maths chapter starts: page {ch10_start}")
    print(f"  Maths chapter ends:   page {next_ch - 1 if next_ch else '?'}")

    # Find PAPER 1 / PAPER 2 markers inside the range
    if ch10_start:
        end = next_ch if next_ch else len(doc)
        for p in range(ch10_start - 1, end):
            text = doc[p].get_text("text")
            m = re.search(r"PERFORMANCE\s+IN\s+EACH\s+QUESTION\s+IN\s+PAPER\s+([12])", text, re.I)
            if m:
                print(f"  PAPER {m.group(1)} section starts: page {p+1}")

    # Sample QUESTION heading format
    if ch10_start:
        end = next_ch if next_ch else len(doc)
        found = False
        for p in range(ch10_start - 1, end):
            text = doc[p].get_text("text")
            heads = re.findall(r"QUESTION\s+\d+\s*:[^\n]{0,70}", text)
            if heads:
                print(f"  Sample QUESTION headings (page {p+1}):")
                for h in heads[:4]:
                    print(f"    {h!r}")
                found = True
                break
        if not found:
            print("  ** NO QUESTION HEADINGS FOUND IN RANGE **")
    print()