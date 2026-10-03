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
    """Returns {skill_id: [template_id, ...]} — allows aggregation
    when multiple old skill_ids collapse to the same canonical skill."""
    if not MAP_PATH.exists():
        return {}
    mapping = {}
    with open(MAP_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("skill_id") or "").strip()
            tid = (row.get("template_id") or "").strip()
            if sid and tid:
                mapping.setdefault(sid, []).append(tid)
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
    """Return the list of template_ids for a skill, or [] if none.
    Kept as a thin shim for backwards compatibility with callers that
    expected a single id — use get_templates_for for the list."""
    return list(SKILL_TO_TEMPLATE.get(skill_id, []))


def get_templates_for(skill_id: str):
    """Return all template_ids mapped to a canonical skill_id."""
    return list(SKILL_TO_TEMPLATE.get(skill_id, []))


def has_analogue(skill_id: str) -> bool:
    """Return True if the skill has any analogue pool entries."""
    tids = SKILL_TO_TEMPLATE.get(skill_id, [])
    return any(POOL.get(tid, []) for tid in tids)

def all_skills() -> list:
    return sorted(SKILL_TO_TEMPLATE.keys())


def pool_size(template_id: str) -> int:
    return len(POOL.get(template_id, []))


def analogue_key(analogue: dict) -> str:
    return _stable_key(analogue)


def get_random_analogue(skill_id: str, exclude_keys=None):
    """
    Return a random analogue for the given skill, excluding those in
    exclude_keys (a set of analogue_key() hashes). Samples across every
    template_id mapped to the canonical skill_id, so aggregation works.
    Falls back to the full pool if every analogue has been seen.
    """
    tids = SKILL_TO_TEMPLATE.get(skill_id, [])
    if not tids:
        return None

    # Gather all analogues across the skill's template pool
    combined = []
    for tid in tids:
        combined.extend(POOL.get(tid, []))
    if not combined:
        return None

    exclude = set(exclude_keys or [])
    fresh = [a for a in combined if _stable_key(a) not in exclude]
    if fresh:
        return random.choice(fresh)
    return random.choice(combined)



def get_analogue(skill_id: str):
    """Backwards-compatible single call. Returns a random one, no exclusion."""
    return get_random_analogue(skill_id)
