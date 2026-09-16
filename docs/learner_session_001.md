# Learner session 001

Date: 2026-09-16
Learner context: Pilot / self-run multi-skill CLI trial
Duration: ~20–25 min across skills 1–5

## What they typed that failed or confused the engine

1. `x =2 0r 3` — typo `0r` instead of `or` → UNKNOWN (not correct, not sign-flip)
2. `y>=4` — wrong range (sign/value error) → UNKNOWN (no misconception rule for “forgot the minus”)
3. `costheta` on reduction → UNKNOWN (not mapped to a specific wrong-trig identity beyond sign flip)
4. `ok i see now its sin theta` — correct answer buried in a sentence → not recognised as correct
5. `angle subtended by a diameter is 90 degrees` — good theorem language → still UNKNOWN / not accepted as sufficient citation
6. `i am confused` / `i dont know` / `you tell me wat i am missing` — soft help-seeking; only partial disengagement coverage

## What helped

1. Normalisation accepted `x = 2 or 3`, `x =2 or x= 3`, `sintheta`, `y >= -4`, `y>= -4`
2. Disengagement on `i dont understand` → calm reframe (HANDLE_DISENGAGEMENT)
3. Euclidean path did fire `M_MISSING_THEOREM_CITATION` once on informal 90° language
4. Correct answers still never dumped full solutions first

## Top 3 friction points to fix next (max 3)

1. **Typo-tolerant `or`** — map `0r` / `ror` → `or` in `_norm` (high frequency in real typing)
2. **Accept correct answer embedded in a sentence** — if normalised text contains the expected form as a substring/token, treat as correct (e.g. `... sin theta`)
3. **Richer “stuck” language** — treat `i dont know`, `i am confused`, `tell me what i'm missing` like frustrated disengagement (not only `i don't understand`)

## Notes

- Fallback ratio rose when learner explored wrong paths without matching a known misconception (expected at demo skill count).
- Proof skills need softer acceptance of theorem phrasing before “unknown” fatigue sets in.
- Do not expand to new topics until these three matching/UX fixes land.

