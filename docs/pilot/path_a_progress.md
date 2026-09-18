# Path A Progress — 2014 to 2020

**Status:** COMPLETE (v1.2 with stem detection)

| Year | P1 rows | P1 stems | P1 real | P2 rows | P2 stems | P2 real | OCR |
|------|---------|----------|---------|---------|----------|---------|-----|
| 2020 | 55 | 8 | 47 | 52 | 7 | 45 | No (text layer) |
| 2019 | 54 | 7 | 47 | 45 | 5 | 40 | Exams only |
| 2018 | 57 | 8 | 49 | 67 | 12 | 55 | Exams only |
| 2017 | 44 | 7 | 37 | 56 | 10 | 46 | Exams only |
| 2016 | 40 | 2 | 38 | 42 | 5 | 37 | Exams only |
| 2015 | 40 | 4 | 36 | 38 | 2 | 36 | Exams only |
| 2014 | 36 | 3 | 33 | 46 | 5 | 41 | Exams only |

**Totals:** 587 real questions, 85 stems, 672 rows.

**Segmentation rules applied:**
- Parent-prefix filter (v1.1): rejects cross-question false positives
- Stem detection (v1.2): labels X.Y rows that have X.Y.Z children as 'stem'
- Marks extracted from trailing (n) or [n], values > 15 discarded

**Known limitations:**
- Exam PDFs are scanned images — require OCR, marks partial
- Memo PDFs have text layers — high fidelity, used in N04 mapping
- Older years (2014-2016) have lower real counts due to shorter CAPS papers
- 2018 P2 = 55 real is high end; spot-check later if convenient

**Tagged:** segment-YYYY-v1 for each year.
**Next:** taxonomy v2 rebuild (CAPS + corpus lexicon + memo signatures).
