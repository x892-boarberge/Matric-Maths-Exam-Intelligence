"""Ladder freeze on non-maths input + LLM bypass for four kinds."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

# ---------- 1. Freeze attempts counter on non-attempt input ----------
old_diag = '''        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)
        learner_state.attempts_total += 1'''

new_diag = '''        diag = diagnose(problem.skill_id, learner_response, problem.expected_answer)

        # Count the attempt only when the learner actually attempted the maths.
        # Celebration, meta-comment, hostile, language, silence, and pure
        # answer-demand do not count as attempts, so they must not advance
        # the hint ladder.
        NON_ATTEMPT_KINDS = {
            "celebration",
            "meta_comment",
            "hostile",
            "other_language",
            "silent",
        }
        is_real_attempt = diseng.kind.value not in NON_ATTEMPT_KINDS
        # Also treat "answer_demand" as a non-attempt for ladder purposes
        if diseng.kind.value == "answer_demand":
            is_real_attempt = False

        if is_real_attempt:
            learner_state.attempts_total += 1'''

if old_diag in src:
    src = src.replace(old_diag, new_diag, 1)
    print("Ladder freeze rule added")
else:
    print("WARNING - diagnose block not found")

# ---------- 2. LLM bypass for four kinds ----------
old_call = '''            meta_message = meta_renderer.render_meta_response(
                diseng.kind.value,
                learner_text=learner_response,
                learner_id=learner_state.learner_id,
                attempts=prior_same,
            )'''

new_call = '''            # The pool handles these kinds more reliably than the LLM:
            #   celebration    - short acknowledgement, no variety needed
            #   meta_comment   - honest brief answer, LLM drifts
            #   other_language - LLM does not speak SA languages well
            #   silent         - one prompt, pool is fine
            POOL_ONLY_KINDS = {
                "celebration",
                "meta_comment",
                "other_language",
                "silent",
            }

            if diseng.kind.value in POOL_ONLY_KINDS:
                meta_message = meta_library.respond_to_disengagement(
                    diseng.kind.value,
                    learner_id=learner_state.learner_id,
                    attempts=prior_same,
                )
            else:
                meta_message = meta_renderer.render_meta_response(
                    diseng.kind.value,
                    learner_text=learner_response,
                    learner_id=learner_state.learner_id,
                    attempts=prior_same,
                )'''

if old_call in src:
    src = src.replace(old_call, new_call, 1)
    print("LLM bypass added for celebration/meta/language/silence")
else:
    print("WARNING - meta call block not found")

ENGINE.write_text(src, encoding="utf-8")
print("Patch 3 complete")
