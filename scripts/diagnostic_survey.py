"""Survey the diagnostic PDFs to check text layer availability."""
import pdfplumber
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "diagnostic_reports"

RANGES = {
    2014: (117, 139),
    2015: (158, 182),
    2016: (155, 181),
    2017: (161, 184),
    2018: (139, 159),
    2019: (177, 201),
    2020: (184, 207),
    2021: (186, 212),
    2022: (198, 220),
}


def find_pdf(year):
    matches = (list(RAW.glob(f"{year}_maths_*.pdf"))
               + list(RAW.glob(f"*{year}*maths*.pdf")))
    return matches[0] if matches else None


def check_pdf(path, start, end):
    try:
        with pdfplumber.open(path) as pdf:
            total = len(pdf.pages)
            if end > total:
                end = total
            idxs = list(range(start - 1, min(end, total)))
            chars = 0
            for i in idxs:
                text = pdf.pages[i].extract_text() or ""
                chars += len(text)
            avg = chars / max(1, len(idxs))
            return {
                "total_pages": total,
                "range": f"{start}-{end}",
                "pages_checked": len(idxs),
                "avg_chars": round(avg, 1),
                "has_text_layer": avg > 200,
            }
    except Exception as e:
        return {"error": str(e)}


def main():
    print(f"{'Year':6s} {'Range':12s} {'Pages':6s} {'Avg chars':10s} {'Status':12s}")
    print("-" * 60)
    for year in sorted(RANGES.keys()):
        start, end = RANGES[year]
        pdf_path = find_pdf(year)
        if not pdf_path:
            print(f"{year:6d} {'?':12s} {'?':6s} {'?':10s} MISSING_PDF")
            continue
        r = check_pdf(pdf_path, start, end)
        if "error" in r:
            print(f"{year:6d} {start}-{end} {'?':6s} {'?':10s} ERROR")
            continue
        status = "TEXT_OK" if r["has_text_layer"] else "NEEDS_OCR"
        print(f"{year:6d} {r['range']:12s} {r['pages_checked']:6d} {r['avg_chars']:10.1f} {status}")


if __name__ == "__main__":
    main()
