# Memo Answers — Known Limitations

## 2025 corpus coverage

The 2025 P1 mapped corpus is missing 5 subquestions:
- 1.1.1 (quadratic equation, `algebra.quadratic.solve`)
- 1.1.2 (quadratic equation, `algebra.quadratic.solve`)
- 4.3
- 4.4
- 4.5

These were dropped by the N03 segmentation pass. They are recorded in the gold
set (49 rows) but not in the mapped corpus (44 rows).

## Impact on CLI demo

The corpus menu therefore offers 4 questions, not 6:
- 2025 P1 5.2 — FUNC — functions.parabola.range
- 2025 P2 5.2.1 — TRIG — trig.reduction.simplify
- 2025 P2 3.5 — AGEO — analytical_geom.parallelogram.prove
- 2025 P2 10.3 — EUCL — euclidean.semicircle.prove

Missing:
- 2025 P1 1.1.1 — ALG — algebra.quadratic.solve
- 2025 P1 1.1.2 — ALG — algebra.quadratic.solve

## Resolution

Backfill the missing 2025 P1 subquestions in a dedicated segmentation-correction
pass. Not urgent. Demo works without them.
