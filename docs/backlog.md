# MethodMarker Backlog — Deferred Ideas

Ideas that came up in sessions but are not in the current build.
Each has enough detail to resume without re-deriving.

---

## H. Homework-Variant Session Flow

**Idea (from session 27-29 September 2026):**
The tutor should open every session the way a human tutor does.
Not "Welcome to the tutor." A greeting, a preview, and then a gate:
does the learner have school homework to work through?

**The flow, in eight stages:**

1. **Warm greeting.** Greet the learner by name, time-of-day aware.
   *"Good evening, Tanaka."*

2. **Progress preview.** Summarise where the learner is, from the
   mastery store and recent sessions.
   *"Last time we worked on quadratic equations. Factoring is solid;
   the sign handling is where we are still shaky."*

3. **Homework gate.** Ask if the learner has homework.
   *"Do you have homework or an assignment from school you want to work through?"*

4. **Variant, not answer.** If yes, do NOT solve the homework.
   Generate a variant of it — same method, different numbers.
   The learner works the variant; the underlying skill is revealed.

5. **Step grading.** The step grader runs on the variant. Feedback
   names the exact step that broke, not the answer.

6. **PDF printable.** When the working is done, produce a PDF of
   the question, the learner's working, and the correct steps.
   The learner shows it to a teacher or parent.

7. **Recommendation.** A specific "next session, let's do X"
   recommendation is stored and feeds the next session's preview.

8. **Three-way data.**
   - Tutor: discovery store gets an event.
   - Student: mastery model updates.
   - Parent / teacher: referral layer gets an entry on recurrence.

**What exists already:**

- Step grading on variants — `step_grader.py`
- Discovery store — `tutor_discovery` table
- Warm greeting + preview — `session_open.py` (built this session)

**What is missing:**

- **Variant router.** Given an arbitrary learner-supplied question,
  identify its template and generate a fresh variant. The analogue
  library has 4,364 variants across 64 templates, so the raw material
  exists. The missing piece is the classifier: question -> template.
  This is the hardest piece and belongs in the OpenAI phase
  (LLM can classify the incoming question in one call).

- **PDF generator.** Question + working + correct working, printable.
  Self-contained. `reportlab` or similar.

- **Recommendation output surface.** The discovery store has
  effectiveness rates. The recommendation text itself is missing.

- **Parent / teacher referral surface.** Reports for external
  audiences — Phase 7.

**Design principle that must hold:**

The tutor does not give answers. It works from variants. That is
the pedagogic move that separates MethodMarker from a chatbot.

**When to build:**

Fits during the OpenAI phase — the variant router is the natural
first use of the LLM in the product, since it is a classification
task with a bounded search space.

---

## I. Health check — per-question mark totals

**Idea:** every `memo_step_marks_*.csv` row's marks should sum to
the memo's declared total for that sub-question. Miscounts have
surfaced multiple times. Automated verification would catch them
at write time.

**Pattern:**
question_id, total_marks_expected, total_marks_actual, OK?
2023_P1_Q1.1.1, 3, 3, True
2023_P1_Q1.1.2, 4, 4, True

Source of `total_marks_expected`: `question_structure.csv`
(`marks` column per sub-question).

**When to build:** next session that touches the health check.

---

## J. Health check — malformed CSV row detection

**Idea:** rows with fewer columns than the header should fail loudly
at load time, not silently break the loader. This has happened
three times in two days.

**Pattern:** at the top of `load_steps()` in `step_grader.py`,
verify `len(row) == ncols` for every row; if not, raise with the
line number.

**When to build:** next session that touches the loader.

---

## K. Presentation matcher — step-linking

**Idea:** the current presentation matcher fires rules on keywords
(`sqrt`, `d/dx`, etc.) rather than on the specific learner step
that triggered them. This causes false positives.

**Fix:** tag each presentation rule with a `trigger_step_tag` field
in the CSV, so the matcher only fires rules that correspond to the
actual step the learner just did.

**Status:** matcher disabled pending this fix. Do not re-enable
until step-linking is in place.

**When to build:** own session.

---

## L. 2020 + 2021 proofs — move to dedicated `_proofs.csv`

**Idea:** consistency. Other years (2014-2019, 2022) have EUCL
proofs in dedicated `memo_step_marks_YYYY_P2_proofs.csv` files
using `match_mode: keyword`. 2020 and 2021 have proofs in the
main CSVs using exact mode.

**Fix:** move 2020 + 2021 EUCL rows to `_proofs.csv` with
`match_mode: keyword`.

**Priority:** low. Works as-is.

**When to build:** whenever we next touch the 2020/2021 CSVs.

---

## M. Question corpus 2014-2022 — the next major phase

**Idea:** upload the 2014-2022 question papers (not the memos —
those we already have). OCR each paper. Segment into
sub-questions. Map each to a topic. Type the expected answer
from the memo.

**Output:** the step marks we typed for 2014-2022 become usable.
The drill can present questions from 12 years, not 3.

**Size:** ~4 weeks of content work, one paper per session.

**Dependency:** nothing. It is the next phase.

**When to build:** after closing Phase 5d cleanly.

---

## N. Learner timezone on the learner row

**Idea:** `session_open.greet()` already reads a `timezone` column off
the `learner` row if it exists (IANA name, e.g. `Europe/London`). The
column does not exist yet. Add it, plus a way to set it:

- `ALTER TABLE learner ADD COLUMN timezone TEXT;`
- A first-run prompt: "Which country are you in?" -> map to IANA name.
- Or infer from the learner id / signup metadata.

**Why:** so an international student gets the right time-of-day
greeting without us hard-coding SAST. SAST remains the default when
the column is null or missing.

**When to build:** small; fold into the next session that touches
`learner_store.py`.

---

## O. Warm open — banner ordering

**Idea (cosmetic, noted 29 Sep 2026):** in the CLI, the
`MatricMath CLI Tutor` banner and the `Learner: ... | store: ...`
line currently print *after* the warm-open box. They should print
*before*, so a session opens with the banner, then the greeting,
then the homework gate.

**Fix:** move the banner prints to just before the `warm_open(...)`
call in `scripts/cli_tutor.py`.

**When to build:** next session that touches `cli_tutor.py`.

---

## P. Friendly skill names in the progress preview

**Idea:** `session_open.progress_preview()` currently falls back to
`_friendly_skill()` which just drops the namespace and joins the
remaining dots. So `algebra.quadratic.solve` -> `quadratic solve`,
and `geometry.3d.length` -> `3d length`. It reads robotic.

**Fix:** a lookup table mapping skill ids to human topic names,
e.g.:

- `algebra.quadratic.solve`        -> "quadratic equations"
- `geometry.3d.length`             -> "3-D length problems"
- `trig.reduction.formulae`        -> "reduction formulae"
- `euclidean.semicircle.prove`     -> "angle in a semicircle (proof)"

Fallback: current `_friendly_skill()` behaviour if no mapping exists.

**Where to put the table:** `src/tutor/skill_names.py` (new module),
or a `skill_display_name` column on the `skill` table if one exists.

**When to build:** next session that touches `session_open.py`.

---

## Q. Tutor persona name

**Decision (29 Sep 2026):** the tutor persona is named **Tanaka**.
The name is the project author's own — this project is, in part, a
deliberate recreation of the author as a tutor.

**Where it lives:**

- `src/tutor/session_open.py` -> constant `TUTOR_NAME = "Tanaka"`.
- Banner in `scripts/cli_tutor.py` reads
  `MatricMath CLI Tutor  ·  Tanaka`.
- `_tutor_intro(learner_name)` returns `" I'm Tanaka."` on a first
  meeting, and returns `""` when the learner's first name matches
  the tutor's — so we never say "I'm Tanaka" to a learner called
  Tanaka.

**Product framing:** *MethodMarker* is the engine (the thing that
marks the method). *Tanaka* is the tutor (the voice in the CLI).
Engine name stays on the repo, README, and PDFs. Persona name is
what the learner hears.

**Open questions for a future session:**

- Should the tutor ever reintroduce itself after a long absence
  (e.g. >30 days)? Current: no. Probably fine.
- Does the persona need a surname, or a one-line bio shown once at
  first meeting? Current: no. Nice-to-have.
- Should the persona name be configurable per-deployment (e.g. for
  schools that want their own tutor name)? Current: a single
  constant. Easy to promote to config later if needed.

**When to build (extras):** only if/when needed. Core is done.

---

## R. Session-open ordering contract

**Rule (29 Sep 2026):** in `scripts/cli_tutor.py`, the session open must
follow this order:

1. `store = open_store(store_path)`
2. `show_banner(learner_id, store_path)`      # no DB access
3. `warm_open(learner_id, store)`             # reads PRE-session state
4. homework gate (input)
5. `store.load_learner(learner_id)`           # stamps last_seen
6. topic loop (`while True: pick_problem()`)

**Why:** `load_learner()` writes `last_seen`. If it runs before
`warm_open()`, a brand-new learner looks like a returning one, the
"I'm Tanaka" intro is suppressed, and the greeting says "Good to see
you again". The bug is subtle because it only shows up in the CLI —
standalone `greet()` calls (which don't touch load_learner) behave
correctly, so a unit test won't catch it.

**Also:** `warm_open()` decides `is_new` once and passes it to both
`greet()` and `progress_preview()`, so the greeting and the preview
can never disagree about whether this is a first meeting. If either
function is changed to recompute new-ness independently, that
invariant breaks.

**When to review:** any session that touches the session-open path or
`load_learner()`. Add a lint / assertion if we ever refactor main().

---

## T. Skill taxonomy granularity — 2014–2022 vs 2023–2025

**Problem (surfaced 29 Sep 2026):** `memo_step_marks_*.csv` for 2014–2022 use a
coarse skill vocabulary (`sequences.arithmetic`), while the hand-curated 2023–2025
files use a finer one (`sequences.ap.term`). Rebuilding 2023 P1 from the step
marks matches 10/50 skill_ids against the hand-curated reference. The remaining
40 use coarser ids.

**Impact:**

- **Not blocking.** Mastery still tracks; the loop's newest-first progression
  is per-topic, not per-skill; grading works.
- **Cosmetic for feedback.** Feedback names the topic correctly but not the
  specific sub-skill. `sequences.arithmetic` covers AP term, AP sum, AP
  difference — three subtly different skills collapsed into one.

**Fix (eventual):** map coarse ids to fine ids in the step-marks CSVs.

- A hand-maintained mapping CSV: `coarse_id, fine_id, evidence_pattern`.
- Derive from `method_tag` + `question_text`.
- Use the 2023 hand-curated taxonomy as canonical vocabulary, then refine
  each older year against it.

**When to build:** separate session; content work, not code work.

---

## U. Expected-answer normalization (2014–2022 machine-built)

**Problem:** machine-built `memo_answers_*.csv` produce expected answers like
`x=3 or x=-4` and `P(A and B)=1/4`. The hand-curated files use `x = 3 or x = -4`
and bare `1/4`. After whitespace strip, 24/50 match; the rest differ in
formatting convention. A few real differences also surfaced:

- `1.1.3` — ours `x=0 or x=4`, ref `x=4`. Extraneous root not rejected.
- `10.2.1` — ours missing one probability branch the ref has (0.35, 0.65).

**Fix:** a normalization pass over the machine-built files:

- Strip leading `P(...)=` prefixes.
- Normalize spacing around `=`, `<`, `>`.
- Add extraneous-root rejection logic when the question type allows.
- Compare each machine file against its memo PDF for outliers.

**When to build:** separate session, after M is live and the loop has been
observed against real learners.

---

## V. Mixed corpus — 2023–2025 hand-curated vs 2014–2022 machine-built

**Note:** 2023, 2024, 2025 files are hand-curated (higher polish). 2014–2022
are machine-built (first-pass). The corpus is now mixed.

**Decision:** keep hand-curated files as the target quality bar. Over time,
polish machine-built files toward the same standard. Do **not** replace the
hand-curated files with machine output for the sake of uniformity — the
hand-curated files are the reference, not the fallback.

**When to review:** after the first cohort of real learners has hit the
2014–2022 questions and we can see which subquestions caused friction.

---

## W. Question text quality in 2014–2022 (OCR residue)

**Note:** the `question_text_short` column in the machine-built files
inherits OCR residue from the topic maps (`3x° —2x =14` instead of
`3x^2 - 2x = 14`). This does *not* affect the drill — the drill reads its
prompt from the topic map via `question_loader.py`, not from this column.
But if a future feature ever uses `question_text_short` directly (e.g.
a printable PDF of the anchor), the OCR residue would surface.

**Fix:** a per-year OCR cleanup pass, folded in with sections T and U.

**When to build:** low priority; only if a feature needs clean text.

---

## X. Backfill P2 geometry step marks (2014–2022)

**Problem (29 Sep 2026):** step-mark completeness audit found 21 questions
missing from `memo_step_marks_*.csv`:

- 2014 P2: Q8, Q9, Q10
- 2015 P2: Q8, Q9, Q10, Q11
- 2016 P2: Q9, Q10
- 2017 P2: Q4, Q8, Q10, Q11
- 2018 P2: Q8, Q9, Q10
- 2021 P1: Q11
- 2022 P2: Q4, Q8, Q9, Q10

Every missing question is in P2 and is Analytical or Euclidean Geometry.
These are the DBE's most-reported error area — diagram_assumption errors
alone are 13.3% of all reported errors, every year.

**Impact:**

- Diagnostic attribution: ~110 of the 221 topic-level rows collapse onto
  coarse `euclidean.circle` / `analytical.circle`, because the fine skills
  can't be looked up.
- Drill: can't present these questions at all — they're missing from
  `memo_answers`.
- Variant library: no step sequence to anchor compositional geometry
  variants against.

**Fix:** extract memo PDFs for the 21 questions, type step marks in the
same format as existing `memo_step_marks_*.csv`, then re-run the M6
rebuild for affected papers.

**Size:** ~100–150 subquestions. 2–3 content sessions.

**When to build:** dedicated content session. Not on the code critical path,
but blocks fine-grained Euclidean diagnostic attribution and drill coverage.

---

## Y. LLM classification pass on the 'general' bucket and residual topic-level rows

**Problem (29 Sep 2026):** after the regex re-classification pass:

- 319 rows still have `error_class == 'general'` — real error texts the
  regexes couldn't bucket.
- 221 rows still have topic-level attribution, ~110 of which are blocked
  on backlog X, ~110 of which have genuinely ambiguous refs.

**Fix:**

1. **Error-class pass.** Send each `general` row's `error_text` to
   DeepSeek with the 6 classes (procedural / conceptual / notation /
   reading / arithmetic / presentation) as the candidate set. ~R0.05/row
   × 319 = ~R16.
2. **Attribution pass.** For rows with no subquestion_ref and no regex
   match, send the row + the topic map for that question to DeepSeek,
   ask it to pick the most likely subquestion. ~R0.05/row × 110 = ~R5.

**Total:** ~R21 to bring `general` below 5% and topic-level below 3%.

**When to build:** after backlog X lands (so the LLM isn't asked to
attribute rows whose step marks don't exist yet). One session.

---

## Z. Variant pool spec — contaminated rows

**State (29 Sep 2026):** `data/processed/tutor/variant_pool_spec.csv`
contains 148 skills, 1,645 variants targeted. Each row carries an
`attribution_quality` flag:

- `clean` — usable for generator work now.
- `mixed` — mostly clean but with some topic-level contamination.
- `coarse` — attribution is <40% subquestion-level; wait for backlog X.

**Rule:** only build generators for `clean` skills until backlog X lands.
For `coarse` skills (`euclidean.circle`, `analytical.circle`, and any
others that surface), the pool composition is directional at best and
will be recomputed after the step marks are backfilled.

**Also to note:** the current spec doesn't yet carry the fingerprint
surface (numbers, verbs, answer form, diagram presence). That's the
second axis and wraps around this spec in a later pass.

**When to review:** after backlog X, before generator work scales past
the `clean` set.
