# MatricMath Intelligence

South African NSC Mathematics Exam Intelligence, Learner-Error Mining and Evidence-Driven Tutoring Policy.

A data-science project that turns official NSC papers and DBE diagnostic evidence into priority bands, intervention patterns, and a rule-governed tutor policy — not a free-form solution chatbot.

## Problem

Matric Mathematics learners face recurring topic pressure and documented misconceptions. Many digital tools explain generically. Few show a clear chain from official assessment evidence to what the tutor is allowed to do next.

This repository builds that chain.

## Pipeline (status)

| Stage | Artefact | Status |
|------:|----------|--------|
| 01 | Document inventory and register | Complete |
| 02 | Collection, extraction, OCR | Complete |
| 03 | Question segmentation | Complete |
| 04 | Topic mapping (gold-calibrated) | Complete |
| 05 | Assessment exposure | Complete |
| 06 | Diagnostic error / difficulty | Complete |
| 07 | Priority engine (P1/P2) | Complete |
| 08 | Intervention specification | Complete |
| 09 | Tutor behaviour policy | Complete |
| — | Prompt contract + behavioural tests | Complete |
| — | Minimal tutor engine | Next |
| — | Math keyboard / handwriting capture | Later |
| — | 2014-2022 historical expansion | Phase B research |  

## Tutor engine (v1)

A minimal **rule-governed** tutoring engine lives under `src/tutor/`.

- **Principle:** the engine decides (diagnosis, intervention, hint level); the renderer only phrases.
- **Demo:** five diagnosis cases (Algebra, Functions, Trig, Analytical Geometry, Euclidean Geometry).
- **Tests:** 13 behavioural checks in `tests/test_tutor_engine.py` (R1–R10 style rules + five cases).

### Run the five cases

```bash
python scripts/run_five_cases.py


## Core insight

The central challenge is not only whether learners practise enough. It is which skills deserve instructional priority, given exposure, documented diagnostic error pressure, and persistence, and how a tutor can act on that evidence without becoming a solution machine.

## Paper clusters (project data, 2023-2025)

Paper 1: Calculus; Functions and Graphs

Paper 2: Trigonometry; Analytical Geometry; Euclidean Geometry

## Tutor principles (locked)

1. Never full solution first
2. Diagnose before intervening
3. One misconception target at a time
4. Hint ladder H0 to H4 (hybrid attempt-based escalation)
5. Session mastery (N08) vs skill mastery (N09)
6. At least 70 percent of interventions in a session should trace to N08
7. Persist state across disconnect (load-shedding / data drops)
8. Young-learner tone: clear, non-shaming, process-focused
9. Engine decides; LLM only phrases

## Skills demonstrated

- Multi-source educational data engineering
- PDF extraction and OCR discipline
- Question segmentation and structured tables
- Gold-calibrated topic mapping
- Exposure vs difficulty separation
- Multi-criteria priority scoring and sensitivity
- Intervention specification without content fabrication
- Policy design for an auditable AI tutor
- Testable behavioural rules (R1-R10)

## How to explore

1. Read docs/01_Problem_Framing.md
2. Review notebooks 05-07
3. Open data/processed/priority/ and data/processed/intervention/
4. Read docs/09_Tutor_Behaviour_Spec.md and docs/tutor_prompt_contract.md
5. Run: python tests/tutor_test_suite.py

## Licence / use

Portfolio and research use. Official exam and diagnostic materials remain the property of their rights holders (for example the Department of Basic Education). This project analyses publicly available educational artefacts for research and tutoring-policy design.
## Tutor engine (v1.1)

Rule-governed NSC Mathematics tutoring prototype.

### What it does
- Diagnoses selected demo misconceptions (with answer normalisation)
- Selects interventions from `data/processed/intervention/intervention_specification_v1.csv` (N08)
- Escalates hints H0–H4 without giving full solutions first
- Detects simple disengagement (answer demand / frustration)
- Writes append-only session logs under `data/processed/tutor/logs/`

### Run five-case demo
```bash
python scripts/run_five_cases.py
