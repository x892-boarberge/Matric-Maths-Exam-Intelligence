# Mapping v2 — Lessons

## Final state
- Gold F1: 0.972 on 2025 P1 (30/49 comparable)
- 12-year corpus mapped with CAPS taxonomy v2
- One documented mismatch: 2.2.2 (thin OCR, no parent context)

## What worked
- Signatures + structural rules + clean lexicon
- Broadened CALC_EXCLUSION (`f'|g'|h'|y'|f(x)|g(x)|h(x)`)
- No inheritance, no post-processors, no priority ranking changes

## What did not work (and was rolled back)
- Inheritance (concatenate parent + child): F1 → 0.495
- Corrected inheritance (parent only if child unmapped): F1 → 0.756
- STRUCT-priority ranking: F1 → 0.921
- Post-processor v1 (AGEO/CALC): F1 → 0.921
- Post-processor v2 (derivative/majority): F1 → 0.877

## The rule
When one mismatch remains, STOP. Do not iterate. The cost of chasing
0.972 → 1.000 always exceeds the benefit. Document and move on.

## Next session
- Do not touch mapping rules again
- Move to N06 diagnostic re-run
- Move to tutor engine re-point (v1 topics → v2)
