"""
Analogue library v2 — pool-based with per-session variety.

Loads:
  * data/processed/tutor/analogue_template_map.csv  (skill_id -> template_id)
  * src/tutor/analogue_generators.py                (template_id -> generator)

Public:
    get_random_analogue(skill_id, exclude_keys=None) -> dict or None
    has_analogue(skill_id)                            -> bool
    all_skills()                                      -> list
    pool_size(template_id)                            -> int
    analogue_key(analogue)                            -> str   stable hash for exclusion
"""
from pathlib import Path
import hashlib
import random
import csv

from . import analogue_generators


ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "data" / "processed" / "tutor" / "analogue_template_map.csv"


# ------------------------------------------------------------------
# Load the map: skill_id -> template_id
# ------------------------------------------------------------------
def _load_template_map() -> dict:
    if not MAP_PATH.exists():
        return {}
    mapping = {}
    with open(MAP_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("skill_id") or "").strip()
            tid = (row.get("template_id") or "").strip()
            if sid and tid:
                mapping[sid] = tid
    return mapping


SKILL_TO_TEMPLATE = _load_template_map()


# ------------------------------------------------------------------
# Build the pool: template_id -> list of analogues
# ------------------------------------------------------------------
POOL = analogue_generators.generate_all(verbose=False)


def _stable_key(analogue: dict) -> str:
    """Hash the problem text so we can exclude already-shown analogues."""
    problem = str(analogue.get("problem", ""))
    return hashlib.md5(problem.encode("utf-8")).hexdigest()[:12]


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def get_template_for(skill_id: str):
    return SKILL_TO_TEMPLATE.get(str(skill_id).strip())


def has_analogue(skill_id: str) -> bool:
    tid = get_template_for(skill_id)
    if tid is None:
        return False
    return len(POOL.get(tid, [])) > 0


def all_skills() -> list:
    return sorted(SKILL_TO_TEMPLATE.keys())


def pool_size(template_id: str) -> int:
    return len(POOL.get(template_id, []))


def analogue_key(analogue: dict) -> str:
    return _stable_key(analogue)


def get_random_analogue(skill_id: str, exclude_keys=None):
    """
    Return a random analogue for the given skill, excluding those in
    exclude_keys (a set of analogue_key() hashes). If every analogue has
    been shown, falls back to the full pool (so the learner still sees
    something rather than nothing).
    """
    tid = get_template_for(skill_id)
    if tid is None:
        return None
    pool = POOL.get(tid, [])
    if not pool:
        return None

    exclude = set(exclude_keys or [])
    fresh = [a for a in pool if _stable_key(a) not in exclude]

    if fresh:
        return random.choice(fresh)

    # Every one has been seen. Reset and pick randomly from the full pool.
    return random.choice(pool)


def get_analogue(skill_id: str):
    """Backwards-compatible single call. Returns a random one, no exclusion."""
    return get_random_analogue(skill_id)
