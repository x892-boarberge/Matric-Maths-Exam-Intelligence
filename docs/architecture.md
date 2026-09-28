# MethodMarker Architecture — Governing Specification

*Companion to docs/spirit.md. Judged against it in every session.*

## The architectural consequence

We are not building a smarter question-answering system. We are building a
learning tutor whose knowledge compounds from learner evidence.

The engine is the foundation. The accumulated memory is the product.

## Locked principles

1. **NSC-first remains the current content boundary.** The vision is broad.
   The implementation stays South African NSC Mathematics.

2. **Diagnosis is evidence-based.** Memo -> learner work -> observed marks ->
   diagnosis. The system does not infer a missing step merely because it
   was not typed.

3. **The AI layer is genuinely part of the architecture.** The LLM is the
   mechanism for handling genuinely unexplained cases. It is not the
   defining feature and can be swapped.

4. **Discovery is persistent.** tutor_discoveries is the beginning of the
   tutor's long-term institutional memory. Evidence is preserved.

5. **Learner memory and tutor memory are different.**
   - Learner model: what do I know about Tanaka?
   - Tutor discovery store: what have I learned across learners?
   - Teacher referral layer: what should a human teacher know or act on?

6. **Presentation is not diagnosis.** Architectural boundary.

7. **The teacher remains in the loop.** Discoveries mature through
   recurrence and teacher confirmation. The learner is never blocked.

8. **Never optimise for being a better chatbot.** Every feature is judged
   against the four questions and the weekend test.

## The four questions as design constraints

Every subsystem exists to help MethodMarker answer one or more of:

1. What does this learner actually know? -> Learner model, mastery store
2. Why did this step fail? -> Step grader, diagnosis, discovery store
3. What should happen next? -> Foundational DAG, drill router, intervention log
4. Did that work? -> Outcome measurement, transfer testing, intervention effectiveness

If a subsystem does not contribute to at least one of these, it is not core.

## The Tutor Learning Engine

    OBSERVE     learner attempt captured
       ->
    DIAGNOSE    layers 1, 2, 3 in order
       ->
    INTERVENE   smallest action targeting the identified gap
       ->
    MEASURE     transfer test, days later
       ->
    LEARN       what worked, for whom, at which step (discovery)
       ->
    UPDATE      routing, rules, patterns, teaching strategy

Discovery is inside LEARN. Not the whole engine.

## The persistence contract

The critical property: a discovery exists as a first-class object even if
the LLM is swapped or removed.

    learner attempt
        ->
    Layer 1 diagnosis (deterministic)
        ->
    Layer 2 pattern search (across learners)
        ->
    if unresolved:
        Discovery event created
        ->
    LLM reasoning attached (optional, swappable)
        ->
    learner-facing explanation delivered NOW
        ->
    persistent tutor_discovery written
        ->
    future recurrence strengthens it

## The discovery record

    discovery_id          PRIMARY KEY
    pattern_description   what the tutor noticed
    example_lines         the actual learner lines that triggered it
    first_seen_at         timestamp
    last_seen_at          timestamp
    times_seen            integer, increments on recurrence
    learners_affected     list of learner_ids
    confidence            0.0 to 1.0
    llm_explanation       what the LLM said (revisable)
    promoted_to_rule      boolean
    teacher_notes         text, teacher can annotate
    status                open / confirmed / dismissed / promoted

Evidence is preserved. Two years from now, the tutor has not just
conclusions but the raw learner lines from which it learned them.

## The three stores

- **Learner model** — history, mastery, gaps, interventions. Per learner.
- **Discovery store** — patterns, recurrence, LLM reasoning, teacher feedback. Across learners.
- **Teacher referral layer** — "Here is what I am seeing and why it matters."

## Long-term architecture

    NSC Knowledge
    (memos / diagnostics / fingerprint / skills)
              |
              v
        TUTOR
        (diagnosis / teaching / drilling / reasoning)
              |
        +-----+-----+
        v           v
    Learner      Discovery
    Model        Store
        |           |
        |           v
        |     Pattern / Rule
        |     Promotion
        |           |
        +-----+-----+
              v
        Teacher Referral
        "Here is what I am seeing and why it matters."

## The first engineering step

Not the LLM. Not the generative variants. The persistence contract.

1. Schema: tutor_discoveries table with the fields above.
2. Module: src/tutor/discovery_store.py with:
   - record_discovery(learner_id, pattern_desc, example_lines, llm_explanation=None)
   - find_similar(pattern_desc) — recurrence matching
   - promote(discovery_id) — mark as promoted
   - add_teacher_note(discovery_id, note)
3. Hook: diagnosis.py calls record_discovery when layers 1 and 2 cannot
   explain the error. The LLM call is optional (behind the existing LLM
   gate). The discovery is written either way.

The LLM comes after the storage works and the hook is in place.

## The second engineering step

Once discoveries are stored, add intervention logging:

1. Schema: interventions table — discovery_id, action, applied_at, learner_id
2. Schema: outcomes table — intervention_id, measured_at, transfer_result
3. Wire into drill.py: when the tutor routes a learner to a prerequisite
   drill, log the intervention and the later outcome.

This is what makes "did that teaching actually work?" answerable.

## The test for every feature

Before building anything, ask:

1. Which of the four questions does this help answer?
2. Could another AI tutor add this in a weekend?
3. Does it strengthen the teaching archive, or is it cosmetic?

If it does not help answer a question, could be built in a weekend, or is
cosmetic, it is not core.

## The sentence to keep visible during development

"The product gets better not merely when the code improves, but when the
tutor learns something from a learner that it can use again."

That is the moat.

---

*Tanaka Peace Boanerge. ThunderMark. 2026.*
