# MethodMarker Architecture

*Written 2026-10-09. The map. Describes what exists, what is wired, what
is dormant.*

## 1. What MethodMarker is

A closed-loop teaching system over the South African NSC Mathematics
curriculum. **Tanaka** is the tutor (`tutor_engine.py`). **The drill**
(`drill.py`) is the sandbox. Direction of every port: **drill -> Tanaka**.

## 2. The pipeline

Old pipeline (before this session):

```
input -> rules -> N08 fallback -> misconception id
```

Every input forced into a DBE-shaped hole. Off-topic questions, alternative
methods, and student insights were all diagnosed as errors.

Correct pipeline:

```
input
  +-- disengagement detect
  |     +-- human-moment -> meta_renderer
  |     +-- off_topic question -> short refusal + record
  |     +-- curiosity -> short answer + record
  |     +-- alternative_method -> acknowledge + example + warn + record
  |     +-- insight -> recognise + record
  +-- normal attempt
        +-- rules -> known? -> teach objective -> teach -> probe -> retry
        +-- no rule fires -> llm_diagnoser.diagnose_unknown() -> record
```

**The rules are for known cases. The LLM is the second line.**

## 3. The section structure

```
SECTION
    CORPUS         data/processed/mapped/, memo_answers/
    MEMOS          data/processed/memo_step_marks/
    DIAGNOSIS      data/processed/diagnostics/diagnostic_errors_with_skill.csv
    FINGERPRINT    data/processed/fingerprint/
    SHAPES         data/processed/tutor/shape_specs.json
    GENERATORS     src/tutor/analogue_generators.py
    DIAGRAM SPECS  per shape
    STEP SCHEMES   derived from memos
```

## 4. The five LLM roles

| Role | File | Wired | Job |
|---|---|---|---|
| Phraser | llm_phraser.py | yes | Rewrites a decided hint |
| Diagnoser | llm_diagnoser.py | **no** | Reasons about errors |
| Meta-renderer | meta_renderer.py | yes | Answers human moments |
| Tool-caller | llm_caller.py | **no** | Full tool engine |
| Teaching tutor | teaching_objectives.py | yes | Delivers DBE lessons |

The LLM is an instrument. Never the tutor.

## 5. Files that matter - grading

| File | Purpose |
|---|---|
| math_grader.py | 11 matchers. MATCH / NO_MATCH / UNCERTAIN. |
| step_grader.py | Memo-line grader. Per-step status. |
| step_schemes.py | Builds step schemes for drill variants. |
| first_failed_step_diagnosis | Maps step role -> misconception, per section. |
| answer_matcher.py | 6-layer equivalence. Legacy. |

## 6. Files that matter - diagnosis

| File | Purpose |
|---|---|
| diagnosis.py | Rules table + predicates. Per skill. |
| misconception_hints.py | Second-person hints. |
| presentation_matcher.py | Behaviour-based notes. Two tiers. |

## 7. Files that matter - templates

| File | Purpose |
|---|---|
| template_router.py | skill_id + prompt -> template_id |
| analogue_library.py | Loads the variant pool. |
| analogue_generators.py | ~55 parameterised generators. |
| question_loader.py | Loads NSC corpus from mapped CSVs. |

## 8. Files that matter - sessions

| File | Purpose |
|---|---|
| learner_store.py | SQLite. |
| event_log.py | JSONL session logger. |
| discovery_store.py | Unknown errors. Write-only. |
| intervention_store.py | Interventions. |
| session_open.py | Warm-open greeting. |

## 9. Files that matter - LLM

| File | Purpose |
|---|---|
| llm_config.py | Env-driven config. |
| llm_caller.py | Tool-calling loop. Dormant. |
| llm_gate.py | Decides when the LLM is called. |
| llm_phraser.py | Phraser. |
| llm_diagnoser.py | Reasoner. Dormant. |
| llm_conversation_prompt.py | System prompt for tool-caller. |
| meta_prompt.py | System prompt for meta-renderer. |
| meta_renderer.py | Meta renderer. |
| salt_check.py | Persona guardrail. |
| tools.py | 7 tools. 3 real, 3 stubs. |

## 10. Files that matter - disengagement

| File | Purpose |
|---|---|
| disengagement.py | Rule-based input classifier. |
| meta_library.py | Pool per kind. |
| hint_policy.py | Attempts -> hint level. |
| intervention_selector.py | Wraps N08 loader. |
| n08_loader.py | Loads N08 CSV. |

## 11. The SQLite tables

| Table | Written by | Read by |
|---|---|---|
| learner | load_learner | dashboard |
| session | start_session | mastery |
| attempt | drill, tutor_engine | analysis |
| mastery | recompute_mastery | session_open |
| tutor_discovery | drill (unknowns) | **nothing yet** |
| intervention | drill | **nothing yet** |
| outcome | drill | **nothing yet** |

**The reader is missing. Phase 10 builds it.**

## 12. Wired vs dormant

**Wired:** grading, diagnosis, teaching objectives, presentation matcher,
disengagement detection, meta renderer, LLM phraser, evidence persistence,
template routing.

**Dormant:** `llm_diagnoser.diagnose_unknown()`, `llm_caller.converse_turn()`,
`tools.py` stubs, `discovery_store` reader, `intervention_store` reader,
`outcome` reader.

**Missing:** `student_learning_events` table, `alt_method` classifier,
`alt_method` prompt, `analyse_learning.py`, candidate rule pipeline,
diagram parameterisation for variants.

## 13. Four universal bugs fixed this session

1. `math_grader._SEP` split on "and" - accepted wrong connectors as matches
2. `first_failed_step_diagnosis` blamed absent working for failed steps
3. `_declared_roots` missed bare numbers after "or"/"and"/",". Also missed
   whitespace-optional forms after `_norm`
4. `math_grader.m_coordinate_pair` fired without brackets

Each silently affected every section. All fixed.

## 14. The five rules that keep the architecture connected

1. Never let the LLM be the source of truth.
2. Never let a correct answer automatically mean mastery.
3. Never let one observation become a permanent teaching rule.
4. Never lose the learner's history.
5. Every teaching action should have an observable outcome.

## 15. A learner's session

```
CLI start
    learner id
    warm open (greeting, mastery preview, homework gate)
    topic picker
    problem presented
    drill begins (5 questions)
        for each question:
            collect working
            grade (MATCH / NO_MATCH / UNCERTAIN)
            if MATCH: step feedback, presentation notes, next
            if NO_MATCH or UNCERTAIN:
                diagnosis (rules, step map, LLM)
                mark for this question
                step feedback
                teaching objective (if a rule fired)
                probe
                retry original
                next question
    sitting summary
    close
```

## 16. What happens every week

*Not built yet. Phase 10.*

```
weekly cron or manual run
    scripts/analyse_learning.py
        read attempts, interventions, outcomes for last 7 days
        group unknown errors by similarity
        for groups of 3+, ask llm_diagnoser to describe
        write reports/learning/YYYY-Www-<section>.md
        write candidate_rules/CR_YYYY_Www_NN.json
    teacher opens the report, reads, decides
```

**That is the mechanism by which Tanaka learns from the students.**

## 17. The one-line summary

Tanaka observes, grades, diagnoses, teaches, verifies, and records. The
repository holds what he learned. The weekly pass turns the records into
patterns. The teacher reviews the patterns. The rules change. Tanaka gets
better.

The mechanism exists. The reader is missing. Phase 10 builds it.

