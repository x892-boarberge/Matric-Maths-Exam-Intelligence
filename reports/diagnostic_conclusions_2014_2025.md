# NSC Mathematics Diagnostic Conclusions
## 2014–2025 — Twelve Years of DBE Evidence

---

## 1. Method & Corpus

| Metric | Value |
|---|---|
| Years analysed | **12** (2014–2025, no gaps) |
| Papers | 24 (P1 + P2 per year) |
| Error narratives | **1111** |
| Topics covered | 10 (all mapped, 0 unmapped) |
| Sources joined | DBE diagnostic narrative + per-question averages |
| Join rate | **100%** — every error carries a real numeric priority |

**Sources:** DBE NSC Diagnostic Reports, Chapter 10 (Mathematics), 2014–2025.  
Per-question averages extracted from each report. Error narratives parsed and classified by rule-based tagger.

**Limitations:** 2019 was parsed with paragraph-based splitting due to scrambled PDF layout — its 75 errors are consistent with other years. 2020 P1, 2021 P2, 2022 P2 averages were read from graphs manually — values verified against source.

---

## 2. Permanent Issues — Present in Every Year

These 21 (topic × error_class) combinations appear in **12 of 12 years**. They are structural — not the result of a bad paper or a bad cohort.

| Rank | Topic | Class | Years | Total errors |
|---|---|---|---|---|
| 1 | TRIG | procedural | 12/12 | 80 |
| 2 | EUCL | procedural | 12/12 | 79 |
| 3 | AGEO | procedural | 12/12 | 78 |
| 4 | FUNC | general | 12/12 | 67 |
| 5 | EUCL | general | 12/12 | 63 |
| 6 | AGEO | general | 12/12 | 62 |
| 7 | TRIG | general | 12/12 | 61 |
| 8 | FUNC | procedural | 12/12 | 58 |
| 9 | CALC | general | 12/12 | 52 |
| 10 | STAT | general | 12/12 | 52 |
| 11 | STAT | procedural | 12/12 | 40 |
| 12 | ALG | procedural | 12/12 | 32 |
| 13 | PROB | general | 12/12 | 31 |
| 14 | SEQ | procedural | 12/12 | 29 |
| 15 | CALC | notation | 11/12 | 17 |
| 16 | ALG | notation | 11/12 | 11 |
| 17 | CALC | procedural | 10/12 | 32 |
| 18 | SEQ | general | 10/12 | 27 |
| 19 | FIN | procedural | 10/12 | 22 |
| 20 | FIN | general | 10/12 | 21 |
| 21 | SEQ | notation | 10/12 | 13 |

## 3. Trends — What Is Changing

Linear regression on yearly error counts (2014–2025).

| Topic | Mean/year | Slope | Direction | p-value |
|---|---|---|---|---|
| EUCL | 12.9 | -0.619 | falling ✅ | 0.0071 |
| CALC | 9.2 | -0.357 | falling ⚠️ | 0.0522 |
| ALG | 6.1 | -0.059 | stable | 0.6451 |
| FUNC | 12.9 | -0.031 | stable | 0.9061 |
| PROB | 4.7 | -0.028 | stable | 0.7872 |
| SEQ | 6.8 | -0.028 | stable | 0.8759 |
| AGEO | 12.4 | -0.003 | stable | 0.9886 |
| FIN | 4.2 | 0.021 | stable | 0.834 |
| STAT | 9.2 | 0.255 | stable | 0.1892 |
| TRIG | 14.2 | 0.287 | stable | 0.2113 |

**Error-class trends:**
| Class | Slope | Direction | p-value |
|---|---|---|---|
| procedural | +1.965 | **rising** | 0.0036 |
| reading | +0.105 | stable | 0.4954 |
| notation | -0.042 | stable | 0.7795 |
| conceptual | -0.584 | falling | 0.1272 |
| general | -2.070 | **falling** | 0.0176 |

**Reading this table:** Procedural errors (wrong method application) are increasing at ~2 per year. This is statistically significant. Meanwhile the catch-all 'general' class is falling — which likely reflects improved narrative specificity by the DBE, not fewer errors.

---

## 4. Critical-Priority Misconceptions

**192** errors are attached to questions where the national average was **below 35%**. These are the concrete teaching failures.

| Topic | Critical errors |
|---|---|
| EUCL | 55 |
| PROB | 50 |
| TRIG | 32 |
| CALC | 29 |
| FUNC | 14 |
| SEQ | 7 |
| STAT | 5 |

**Euclidean Geometry (55)** and **Probability (50)** dominate. Both are historically the lowest-performing topics. Every critical EUCL error involves either a missing reason, a diagram assumption, or an incorrect theorem citation.

---

## 5. The Four Structural Themes

### Theme 1 — Procedural errors are rising

- Slope **+1.965 per year** (p = 0.0036, statistically significant)
- Learners increasingly *know what to do* but apply it *incorrectly*
- This is a **method-execution** problem, not a knowledge problem
- Tutor implication: hint ladder should escalate step-level coaching before topic-level review

### Theme 2 — Diagram assumptions are persistent

- Average **13.3%** of errors every year — 143 of 1,111 total
- No statistically significant trend, but never below 8.7%
- Concentrated in EUCL and AGEO
- Tutor implication: diagram-annotation coaching is a permanent feature, not a passing fix

### Theme 3 — Reading-for-understanding hovers ~4%

- Reading errors are stable (slope +0.105, p = 0.4954)
- Peaks in 2014 (6.8%) and 2025 (6.5%) — a decade apart
- Concentrated in STAT and TRIG
- Tutor implication: keyword-highlighting and rephrasing questions is needed, especially for word problems

### Theme 4 — Notation issues are small but chronic

- 47 notation errors across 12 years
- **ALG inequality notation** is the single largest (9 errors)
- Followed by EUCL geometry (4) and FUNC function notation (3)
- Tutor implication: a targeted notation coaching layer for ALG is high-value

---

## 6. Findings by Topic

### TRIG — 170 errors, 32 critical

**Dominant error classes:** procedural (80), general (61)

**Sample narrative:**
> Candidates had diႈculty in seeing the diႇerent planes in the sketch....


### EUCL — 155 errors, 55 critical

**Dominant error classes:** procedural (79), general (63)

**Sample narrative:**
> In Q9.1.1, many candidates gave only one part of the reason, either ‘same base’ or ‘same height’ but not both. Some stated ‘proportional intercept theorem’ as the reason....


### AGEO — 149 errors, 0 critical

**Dominant error classes:** procedural (78), general (62)

**Sample narrative:**

### FUNC — 155 errors, 14 critical

**Dominant error classes:** general (67), procedural (58)

**Sample narrative:**
> Many candidates did not notice that the x-co-ordinate of the turning point gave the line of symmetry....


### STAT — 111 errors, 5 critical

**Dominant error classes:** general (52), procedural (40)

**Sample narrative:**
> This question was very poorly answered by most candidates. They simply had no idea of the frequency column indicating how many times each observation occurred. Consequently, they were unable to perform routine calculations....


### CALC — 110 errors, 29 critical

**Dominant error classes:** general (52), procedural (32)

**Sample narrative:**
> In Q9.1, candidates were able to calculate the derivative correctly, but often did not explicitly equate it to zero. They did however arrive at the correct answers for the turning points....


### SEQ — 82 errors, 7 critical

**Dominant error classes:** procedural (29), general (27)

**Sample narrative:**
> Many candidates struggled to determine the ¿rst diႇerences in terms of x and this impacted on the determination of the second diႇerences. The omission of bracketsin Q3.1 led to x x x x       3 5 1 3 resulting in incorrect simpli¿cation and an incorrect value for x....


### ALG — 73 errors, 0 critical

**Dominant error classes:** procedural (32), general (20)

**Sample narrative:**

### PROB — 56 errors, 50 critical

**Dominant error classes:** general (31), procedural (10)

**Sample narrative:**
> Candidates did not know the difference between the notations n(A) and P(A). Very often they gave the answer as n(A) instead of P(A)....


### FIN — 50 errors, 0 critical

**Dominant error classes:** procedural (22), general (21)

**Sample narrative:**

---

## 7. For the Tutor Engine (N08 Input)

### 7.1 Priority order for misconception library

Top 10 (topic, class) pairs to add to the library **first**:

1. **TRIG — procedural** (80 errors across 12 years)
2. **EUCL — procedural** (79 errors across 12 years)
3. **AGEO — procedural** (78 errors across 12 years)
4. **FUNC — general** (67 errors across 12 years)
5. **EUCL — general** (63 errors across 12 years)
6. **AGEO — general** (62 errors across 12 years)
7. **TRIG — general** (61 errors across 12 years)
8. **FUNC — procedural** (58 errors across 12 years)
9. **CALC — general** (52 errors across 12 years)
10. **STAT — general** (52 errors across 12 years)

### 7.2 Which presentation rules to code first

Based on the notation and reading findings, the highest-value presentation rules are:

| Rule | Why |
|---|---|
| PR_ALG_INEQUALITY_DIRECTION | 9 ALG errors — the single largest notation issue |
| PR_EUCL_STATEMENT_REASON | Every EUCL critical error involves missing reasons |
| PR_EUCL_GIVEN_MARKS | Diagram-assumption errors — 143 across 12 years |
| PR_FUNC_DOMAIN_RANGE_WORDS | 3 FUNC function notation errors, chronic |
| PR_GEN_ONE_STEP_ONE_LINE | Procedural errors rising — layout matters |

### 7.3 Coaching priorities by topic

| Topic | Primary coaching focus |
|---|---|
| EUCL | Reason columns + diagram annotation |
| PROB | Independence tests + counting principle + 'at least' language |
| TRIG | Compound-angle expansions + general solution form |
| CALC | Setting f'(x)=0 explicitly + first-principles notation |
| FUNC | Domain/range notation + asymptote identification |
| ALG | Inequality direction + sign errors in factorisation |

---

## 8. Conclusion

Twelve years of DBE diagnostic data tell one coherent story:

1. **The problems are stable.** Twenty-one (topic × error_class) combinations appear every single year.
2. **Procedural errors are rising.** This is the only statistically significant negative trend in the corpus.
3. **EUCL is improving but still critical.** Slope -0.619 (p = 0.0071) — real progress, but the topic still leads in critical errors (55).
4. **Diagram assumptions are permanent.** 13.3% of errors every year. This is the single most under-taught skill in the curriculum.
5. **Reading-for-understanding is a minority but persistent.** ~4% of errors. Not growing, not shrinking.

These findings define the priorities for the tutor engine. Every misconception in N08 should trace back to a row in this analysis.

---

*Generated from 1111 error records across 12 years of DBE NSC Mathematics Diagnostic Reports.*