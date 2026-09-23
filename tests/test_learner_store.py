"""Tests for the SQLite learner store and mastery evaluation."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.learner_store import open_store
from src.tutor.schemas import MasteryState


def _store():
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    return open_store(tmp)


def test_new_learner_created():
    st = _store()
    l = st.load_learner("L001")
    assert l["is_new"] is True
    l2 = st.load_learner("L001")
    assert l2["is_new"] is False
    st.close()


def test_session_and_attempts_saved():
    st = _store()
    st.load_learner("L001")
    sid = st.start_session("L001", "algebra.quadratic.solve")
    st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                    "x = 2 or x = 3", "D_CORRECT", None, None, "none")
    st.end_session(sid)
    rows = st.conn.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
    assert rows == 1
    st.close()


def test_mastery_not_started_with_no_attempts():
    st = _store()
    st.load_learner("L001")
    m = st.get_mastery("L001", "algebra.quadratic.solve")
    assert m["mastery_state"] == MasteryState.NOT_STARTED.value
    st.close()


def test_mastery_practising_with_one_wrong_attempt():
    st = _store()
    st.load_learner("L001")
    sid = st.start_session("L001", "algebra.quadratic.solve")
    st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                    "x = 5 or x = 2", "D_QUAD_SIGN_FLIP",
                    "M_SIGN_ERROR_FACTORISATION", "H0", "procedural")
    st.end_session(sid)
    state = st.recompute_mastery("L001", "algebra.quadratic.solve")
    assert state == MasteryState.PRACTISING.value
    st.close()


def test_mastery_near_mastery_after_one_passing_sitting():
    st = _store()
    st.load_learner("L001")
    sid = st.start_session("L001", "algebra.quadratic.solve")
    # 4 attempts, 3 correct
    for i in range(3):
        st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                        "x = -5 or x = 2", "D_CORRECT", None, None, "none")
    st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                    "x = 5 or x = 2", "D_QUAD_SIGN_FLIP",
                    "M_SIGN_ERROR_FACTORISATION", "H1", "procedural")
    st.end_session(sid)
    state = st.recompute_mastery("L001", "algebra.quadratic.solve")
    assert state == MasteryState.NEAR_MASTERY.value
    st.close()


def test_mastery_mastered_after_two_passing_sittings():
    st = _store()
    st.load_learner("L001")
    for s in range(2):
        sid = st.start_session("L001", "algebra.quadratic.solve")
        for i in range(3):
            st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                            "x = -5 or x = 2", "D_CORRECT", None, None, "none")
        st.save_attempt(sid, "L001", "algebra.quadratic.solve",
                        "x = 5 or x = 2", "D_QUAD_SIGN_FLIP",
                        "M_SIGN_ERROR_FACTORISATION", "H1", "procedural")
        st.end_session(sid)
    state = st.recompute_mastery("L001", "algebra.quadratic.solve")
    assert state == MasteryState.MASTERED.value
    st.close()


def test_mastery_persists_across_store_reopen():
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    st1 = open_store(tmp)
    st1.load_learner("L001")
    sid = st1.start_session("L001", "algebra.quadratic.solve")
    st1.save_attempt(sid, "L001", "algebra.quadratic.solve",
                     "x = -5 or x = 2", "D_CORRECT", None, None, "none")
    st1.end_session(sid)
    st1.recompute_mastery("L001", "algebra.quadratic.solve")
    st1.close()

    st2 = open_store(tmp)
    m = st2.get_mastery("L001", "algebra.quadratic.solve")
    assert m["mastery_state"] in (MasteryState.PRACTISING.value,
                                   MasteryState.NEAR_MASTERY.value)
    st2.close()
