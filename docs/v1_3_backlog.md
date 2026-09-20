# v1.3 Backlog

## Tutor layer

### Answer matcher
- [ ] Layer 6 (suffix-value) must not fire when expected contains
      an inequality operator (<=, >=, <, >, !=) and response does not.
      Current behavior: `compare("8", "y <= 8")` returns MATCH.
      Desired: NO_MATCH. Documented in tests/test_matcher_limitation.py.

### Diagnosis expansion
- [ ] Add skill rules for topics currently diagnostic-only:
      - sequences.geometric.sum_infinity
      - sequences.arithmetic.series
      - sequences.quadratic.pattern
      - calculus.differentiate.polynomial
      - calculus.cubic.turning_point
      - calculus.concavity
      - calculus.tangent
      - calculus.optimisation
      - finance.compound_interest
      - finance.annuity.future_value
      - finance.annuity.present_value
      - finance.depreciation
      - probability.venn
      - probability.independence
      - probability.counting
      - analytical_geom.gradient
      - analytical_geom.distance
      - analytical_geom.circle.equation
      - statistics.mean
      - statistics.standard_deviation
      - statistics.regression
      - statistics.correlation
- [ ] Each new rule ties to an existing N08 misconception ID.

### Corpus loading
- [ ] Backfill 2025 P1 1.1.1 and 1.1.2 into the mapped corpus.
      Currently missing due to N03 segmentation gap.
- [ ] Extend memo_answers_2025.csv to cover more subquestions
      once diagnosis expansion adds new skills.
- [ ] Add memo_answers_YYYY.csv for 2014-2024 as needed.
