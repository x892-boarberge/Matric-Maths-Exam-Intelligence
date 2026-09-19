# Mapping v2 — Sample Verification (2026-09-19)

## Sample of 10 (random)
Correct:   5/10
Unmapped:  3/10 (1.1.3, 5.3.2, 2.1.1 — all thin text, needs inheritance)
Wrong:     1/10 (P2 8.4 FUNC → should be TRIG)
Anomaly:   1/10 (P2 subquestion "5.11" — segmentation bug in v1 file)

## Known issues to fix next session
1. P2 Q8 misclassification: add TRIG structural rule (stage/backdrop terms)
2. Three unmapped rows: inheritance layer from parent stem
3. P2 subquestion "5.11": segmentation bug in 2025 v1 mapped file

## Important context
- Gold P1 F1 = 0.972 (gate passed)
- Sample includes P2, which is not covered by the gold set
- Sample rate is not the gate metric — it is a post-gate sanity check
