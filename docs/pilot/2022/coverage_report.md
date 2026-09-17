# 2022 Pilot — Mapping summary

**Date:** 2026-09-17T22:06:00.850853+00:00
**Rows:** 116
**Coverage:** 99.1%
**Unmapped:** 1

## Status
- PASS on coverage gate (≥ 85%)
- Taxonomy: frozen v1
- Method: OCR-tolerant rules + question-level inheritance

## Limitations (do not overclaim)
1. Exam text is OCR; mark totals incomplete (P1 ~113, P2 ~85 after cleanup).
2. Calculus count is suspiciously low (1) — possible under-detection or over-inheritance into Functions.
3. Functions count is high (40) — may include inherited neighbours; sample-verify before using for exposure rankings.
4. 2022 results are **pilot only** — not firm multi-year conclusions.

## Next pilot steps
1. Sample-verify 10 random rows (especially Calculus / Functions).
2. Optional: memo mark cross-check for one paper.
3. Only after verification: compare 2022 topic profile to 2023–2025 (descriptive, not definitive).


---

## Pilot decision: ACCEPTED with limitations (2026-09-17)

- 10-sample verification: 9/10 OK, 1 UNSURE (P2 4.4 mixed Calc candidate)
- OCR issues register: docs/pilot/2022/ocr_issues_2022.csv
- data_quality flags reconciled with OCR register
- P2 Q1 table recovery: attempted / pending (see Cell 19 output)
- Diagram extraction deferred
- 2022 topic counts not firm until degraded rows excluded or recovered
- Rows with data_quality = degraded_image_or_table excluded from text-only downstream analysis
