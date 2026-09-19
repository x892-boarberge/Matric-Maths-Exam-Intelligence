# Mapping v2 — Session Log 2026-09-19

## Result
- Gold P1 2025 F1: **0.921** (30/49 comparable)
- Coverage 2014–2025: 61–89% (avg ~72%)
- 2 known mismatches, both fixable next session

## What was built
- Clean lexicon v2 (lift-scored, blacklist-filtered)
- OCR-mangled exponent rules (x? , x*, x^2)
- NSC-wording signature patches (infinite series, constant ratio, etc.)
- 120 signatures, 14 structural rules

## What was tried and rolled back
- Inheritance layer (concatenate parent + child) → F1 dropped to 0.495.
  Root cause: parent text overwhelmed child. Corrected design is
  direct-first, parent-only-if-unmapped.

## Two remaining mismatches
1. 2|2.2.2 SEQ→CALC: thin child text; needs corrected inheritance
2. 8|8.2.1 CALC→ALG: STRUCT_ALG x? rule too broad; narrow it

## Next session (day 2 of mapping)
1. Corrected inheritance: parent only when child is genuinely unmapped
2. Narrow STRUCT_ALG rules to fire only on standalone quadratics
3. Re-verify gold F1 ≥ 0.90
4. Add 2024 P1 gold-equivalent check (spot sample)
5. Move to N05–N07 re-run on v2 corpus
