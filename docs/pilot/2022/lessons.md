# 2022 Pilot — Lessons for 2021+

## What OCR missed
- Mashed fixed-width tables (P2 Q1 popularity/votes)
- Image-only diagrams and numeric values (Venn, ogive, scatter, Euclidean figures)
- Character swaps (y vs n)
- Collapsed mark allocations at block ends

## What the pipeline got right
- Topic mapping sample: 9/10 OK (1 UNSURE on mixed Calc/Analytical item)
- Question-level inheritance useful but must not override circle/geometry cues
- Explicit data_quality / diagram_present flags prevent silent corruption downstream

## One change for 2021
- Carry `diagram_present` and `data_quality` in the mapping schema from the start
- Build OCR issues register per year before accepting the year
- Do not feed degraded rows into exposure/difficulty totals without exclusion
