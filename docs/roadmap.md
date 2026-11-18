# MethodMarker Roadmap

*Written 2026-10-09. Plan. Changes only when a phase fails its exit.*

## 1. What MethodMarker is

A closed-loop teaching system over the South African NSC Mathematics
curriculum. It observes a learner's working, grades it against DBE memos,
diagnoses the error, teaches the point of need, verifies learning, and
accumulates evidence about what teaching works.

The five questions the system exists to answer:

1. What does this learner actually know?
2. Why are they struggling?
3. What should I do next to help them?
4. Did what I did actually work?
5. Across many learners, what is Tanaka learning about how to teach?

Any feature that does not help answer one of these is noise.

## 2. Naming and the two engines

**Tanaka** is the brain. `src/tutor/tutor_engine.py`. He is the tutor.

**The drill** is the sandbox. `src/tutor/drill.py`. Built first to prove
the loop. Those proofs migrate into Tanaka. Then the drill retires.

Direction of every port: **drill -> Tanaka**.

## 3. The section structure

```
SECTION (topic + sub-section)
    CORPUS         real exam questions
    MEMOS          step schemes per question
    DIAGNOSIS      DBE error patterns
    FINGERPRINT    how DBE poses and marks this section
    SHAPES         the shapes the section contains
    GENERATORS     one parameterised generator per shape
    DIAGRAM SPECS  one diagram spec per shape
    STEP SCHEMES   derived from memos, per shape
```

Ten sections: Algebra, Trigonometry, Functions, Calculus, Sequences,
Statistics, Probability, Finance, Analytical Geometry, Euclidean Geometry.

Every fix either completes a section, wires a section, or generalises
across sections. No fix is per-question.

## 4. The four steps per section

**Step 1 - Derivation.** Read the DBE diagnostic rows for the section.
Extract behaviours. Cluster into misconception rules. Register them in
`diagnosis.RULES`, most-specific-first. Verify each rule fires on its own
DBE example.

**Step 2 - Teaching objectives.** One per rule. Sourced from the DBE
recommendation. Concept, why, example, probe. Stored in
`data/processed/tutor/teaching_objectives/`.

**Step 3 - Step-role map.** Run the universal map builder. Auto-derives
`step_role_map.json`. Audit `step_role_overrides.json`.

**Step 4 - Drill test.** Trigger each rule. Verify the correct lesson
fires. Verify evidence persists. Section closed.

Roughly 90 minutes per section, plus your review time.

## 5. The persona rule

> Be gracious. Be distinct. Not licentious.

**Gracious** is the tone. **Distinct** is the substance. **Licentious** is
what kindness becomes when distinctness is dropped.

Every wrong answer gets one sentence. The sentence names the specific
error. Tone is warm. Message is not hedged.

## 6. The five LLM roles

1. **Phraser** - `llm_phraser.py`. Rewrites a decided hint. Wired.
2. **Diagnoser** - `llm_diagnoser.py`. Reasons about errors the rules
   cannot explain. **Dormant.**
3. **Meta-renderer** - `meta_renderer.py`. Answers human moments. Wired.
4. **Tool-caller** - `llm_caller.py` + `tools.py`. Complete tool engine.
   **Dormant.**
5. **Teaching tutor** - `teaching_objectives.py`. Delivers DBE lessons.
   Wired.

The LLM is an instrument. Never the tutor.

## 7. What the LLM does with alternative methods

**Trigger:** answer is correct, but method is not the one in the memo.

**Response, three parts:**

1. **Acknowledge.** Name the method. Confirm the maths is correct. If the
   answer has a small arithmetic slip, correct that too.
2. **One example, from the variants.** Not invented. The LLM pulls an
   existing variant from `analogue_library`.
3. **Sharp warning, on first use.** No deferral. "In South Africa, the
   exam expects [method X]. Here is why. Use that."

**If the learner persists:** no further teaching. "That method works. I
have given one example. Going further is outside the NSC syllabus, so I
cannot continue." Then return to the work.

**Required:** classifier for `alt_method`; a specific prompt; a recording
layer. Not built yet.

## 8. What Tanaka learns from students

Every input the rules cannot classify is recorded:

| Kind | When |
|---|---|
| `off_topic_question` | Question outside the current topic |
| `curiosity` | Question about the maths at hand |
| `alternative_method` | Correct answer via non-memo method |
| `insight` | Learner notices a pattern |
| `unknown_error` | Wrong answer, no rule fires |

**What happens to these records:**

1. Weekly pass reads attempts, interventions, outcomes, unknowns
2. Produces patterns
3. For groups of 3+, drafts a candidate rule JSON
4. Teacher reads, decides. Approve, edit, reject.

**Tanaka proposes. The teacher disposes. The rule goes live only after
review.**

## 9. The freeze rule

When a new idea comes:

1. Write it in `docs/backlog.md`
2. Mark it "frozen until Phase X completes"
3. Do not implement it
4. If it blocks a current phase, bring it up. Otherwise it waits.

Phases complete in order. Patches only to unblock a phase exit criterion.
Every patch logged.

## 10. The phases

### Phase 0 - Freeze and record [DONE]
Deliverables: this file, `architecture.md`, `backlog.md`.

### Phase 1 - Close Claim 1 [DONE]
MATCH, NO_MATCH, UNCERTAIN all produce complete evidence. Closed 2026-10-07.

### Phase 2 - Data reconciliation (per section)
- 2.1 Map reconciliation
- 2.2 Memo step audit
- 2.3 Presentation rules wiring
- 2.4 Question id audit
- 2.5 Router cleanup
- 2.6 Persona wording audit
- 2.7 Verify - section report all Y

**Section state as of 2026-10-09:**

| Section | Rules | Objectives | Map | Verified |
|---|---|---|---|---|
| algebra.quadratic.solve | 8 | 7 | 53% | QA pass |
| algebra.surd.solve | 8 | 6 | 100% | **closed 2026-10-10** |
| algebra.quadratic.inequality | 0 | 0 | - | - |
| algebra.exponential.solve | 0 | 0 | - | - |
| algebra.exponential.proof | 0 | 0 | - | - |
| algebra.simultaneous.solve | 0 | 0 | - | - |
| algebra.proof | 0 | 0 | - | - |
| algebra.proof.integer | 0 | 0 | - | - |
| nine other topics | 0 | 0 | - | - |

### Phase 3 - Shape catalogue
Build `data/processed/tutor/shape_specs.json`. Every shape as data.
One shape done: `surd_equation_s1`.

### Phase 4 - Parameterised generators + diagrams
For each shape: write generator, emit `diagram_spec`, wire dispatcher,
delete the WRITTEN_ANALOGUES entry.

### Phase 5 - Port drill improvements into Tanaka
Port evidence persistence, math_grader, step-based diagnosis, template
routing. Extend `llm_gate.FIXED_ACTIONS`. Wire persona wording.

### Phase 6 - General step schemes
Replace `step_schemes._BUILDERS` with a function that reads memo CSVs for
anchors and analogue steps for variants.

### Phase 7 - Corpus context to the learner
Drill prints DBE comment on wrong answers.

### Phase 8 - Teaching loop extension
Transfer, retention, `attempt_outcome` table.

### Phase 9 - Tutor learning
Unknowns write to `tutor_discovery`. Weekly aggregation. Candidate rules.

### Phase 10 - Learning and analysis
`scripts/analyse_learning.py`:
- Reads attempts, interventions, outcomes for last 7 days
- Groups unknowns by similarity
- For groups of 3+, calls `llm_diagnoser` to describe the pattern
- Writes `reports/learning/YYYY-Www-<section>.md`
- Writes candidate rule JSONs to `candidate_rules/`

Exit: one weekly report produced, one candidate rule approved or rejected.

### Phase 11 - Teacher intelligence
Markdown reports per section per week.

### Phase 12 - Retire the drill
Remove `run_drill` from CLI. Delete `drill.py`. Keep `math_grader`,
`step_grader`, `answer_matcher` as libraries.

### Phase 13 - Cleanup
Collapse scripts, delete `.bak`, reorganise `docs/`, add `pyproject.toml`,
`Makefile`, `README.md`.

## 11. The repository is the memory

ChatGPT and I do not learn between sessions. Every conversation starts
fresh. What gets carried forward is only what we write into files.

**The learning is in the repository, not in the model.**

Tanaka is the same. He gets smarter by having a layer that reads what he
wrote and produces something new. That layer is Phase 10.

## 12. What is not in this roadmap

- Cambridge curriculum - after NSC is complete
- Additional topics beyond the ten sections
- Mobile app, web UI, marketing
- Restructuring beyond Phase 13
- Rewriting what already works

If it is not here, it is not the priority.

