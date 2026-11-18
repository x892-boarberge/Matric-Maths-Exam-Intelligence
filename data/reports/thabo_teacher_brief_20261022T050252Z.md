# Teaching Brief — Thabo

*Generated October 22, 2026 · covering the last 30 days · policy `v1_2026_10`*

## Status at a glance

- **Overall state:** struggling
- **Attempts (last 30 days):** 225
- **Overall first-try accuracy:** 43%
- **Skills worked on:** 5
- **Priority actions this cycle:** 2 HIGH, 0 MEDIUM, 1 LOW

## Priority actions

### 🔴 Quadratic equations — HIGH
*1 of 2 on this skill — multiple HIGH items on this skill; sequence carefully*

**Type:** retention check  
**Why this is prioritized:** retention check was scheduled at day 30 from the provisional mastery decision. Current status: pending.

**Instruction for the tutor:**

> At session start, prompt the learner to complete the retention check for Quadratic equations — 5 questions, unassisted, using the current variant pool.

**Success criterion:** 4 of 5 correct on the retention check

**If it fails:** fewer than 4 of 5 correct → mark durable mastery as failed, re-teach from playbook

**Evidence:**
- decided at: 2026-10-21T15:14:03.319354+00:00
- retention due at: 2026-11-20T15:14:03.319354+00:00
- retention status: pending
- variant pool: `data\processed\tutor\variant_pools\1.1.1_pool.json`

### 🔴 Quadratic equations — HIGH
*2 of 2 on this skill — multiple HIGH items on this skill; sequence carefully*

**Type:** targeted drill  
**Misconception:** `M_SIGN_ERROR_READING_ROOT` — flips sign when reading a root from a bracket  
**Why this is prioritized:** 19 occurrences over 30 days on Quadratic equations — the pattern is persistent and not breaking with the current approach.

**Instruction for the tutor:**

> Before each new quadratic equations question, prompt the learner to say the trap out loud: "flips sign when reading a root from a bracket". Then let them attempt the question. If they avoid the trap, reinforce with one line: "that's the habit you're building."

**Success criterion:** 3 consecutive questions on quadratic equations where the learner does NOT make the flips sign when reading a root from a bracket error

**If it fails:** 3 failures in a row on this drill → switch to the teaching objective (if available) for a structured lesson
  *(escalate to human tutor)*

**Evidence:**
- occurrences: 19
- total attempts: 213
- current accuracy: 0.452
- days since last: 0
- playbook: `data\processed\tutor\playbooks\2025_P1_Q1.json`
- variant pool: `data\processed\tutor\variant_pools\1.1.1_pool.json`

### 🟢 Exponential equations — LOW

**Type:** curriculum gap  
**Why this is prioritized:** No attempts recorded on exponential equations yet. This skill is part of the standard Grade 12 curriculum and will be needed for Paper 1.

**Instruction for the tutor:**

> Introduce exponential equations in the next session when the learner is warmed up and has momentum.

**Success criterion:** first attempt made and specific errors named

**Evidence:**
- attempts: 0

## Curriculum progress

| Skill | Attempts | Accuracy | Variant transfer | Top misconception |
|---|---|---|---|---|
| Quadratic equations | 213 | 45% | 38% | M_SIGN_ERROR_READING_ROOT (19×) |
| 3D trigonometry (length) | 8 | 0% | — | M_3D_WRONG_RATIO (5×) |
| Surd equations | 2 | 50% | — | M_ALG_SIGN_FLIP_FACTOR (1×) |
| Quadratic inequalities | 1 | 0% | — | M_ALG_SIGN_FLIP_FACTOR (1×) |
| Simultaneous equations | 1 | 0% | — | M_ALG_SIGN_FLIP_FACTOR (1×) |

---

*This brief is a rendering of the executable plan (`data/plans/thabo_plan.json`). The tutor loads the plan at session start, executes each action, and revises after each session. Same content, two renderings.*