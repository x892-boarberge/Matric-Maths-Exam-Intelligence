"""Load and validate N08 intervention_specification CSV with safe fallback."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

import pandas as pd

from .schemas import DiagnosisResult, InterventionSelection, ProvenanceKind

# Curated five-case map — always available as secondary lookup
FALLBACK_MAP = {
    "M_SIGN_ERROR_FACTORISATION": ("IP_MISCONCEPTION_CONTRAST", "N08_ALG_QUAD_SIGN_01"),
    "M_TP_COORD_CONFUSION": ("IP_REPRESENTATION_SHIFT", "N08_FUNC_PARAB_02"),
    "M_REDUCTION_SIGN": ("IP_MISCONCEPTION_CONTRAST", "N08_TRIG_RED_01"),
    "M_DIAGRAM_ASSUMPTION": ("IP_STEP_ISOLATION", "N08_AGEO_PROOF_01"),
    "M_MISSING_THEOREM_CITATION": ("IP_SELF_EXPLANATION", "N08_EUCL_PROOF_01"),
}

REQUIRED_COLUMNS = {
    "intervention_id",
    "topic",
    "misconception_id",
    "intervention_pattern",
}

COLUMN_ALIASES = {
    "pattern": "intervention_pattern",
    "misconception": "misconception_id",
    "misconception_label": "misconception_id",
    "id": "intervention_id",
}


@dataclass
class N08Library:
    by_misconception: Dict[str, Dict[str, Any]]
    source_path: Optional[str]
    source_hash: Optional[str]
    load_status: str  # "csv" | "fallback"
    validation_errors: List[str]


def _default_csv_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "data" / "processed" / "intervention" / "intervention_specification_v1.csv"


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    rename = {}
    for col in list(df.columns):
        key = col.lower().replace(" ", "_")
        if key in COLUMN_ALIASES:
            rename[col] = COLUMN_ALIASES[key]
        elif key in REQUIRED_COLUMNS or key == "status":
            rename[col] = key
    if rename:
        df = df.rename(columns=rename)
    return df


def _fallback_library(errors: List[str]) -> N08Library:
    by_misc = {
        mid: {
            "intervention_id": n08_id,
            "intervention_pattern": pattern,
            "topic": "",
            "misconception_id": mid,
        }
        for mid, (pattern, n08_id) in FALLBACK_MAP.items()
    }
    return N08Library(
        by_misconception=by_misc,
        source_path=None,
        source_hash=None,
        load_status="fallback",
        validation_errors=errors,
    )


def load_n08_library(csv_path: Optional[Path] = None) -> N08Library:
    path = Path(csv_path) if csv_path else _default_csv_path()
    errors: List[str] = []

    if not path.exists():
        errors.append(f"CSV not found: {path}")
        return _fallback_library(errors)

    try:
        df = pd.read_csv(path)
    except Exception as e:
        errors.append(f"CSV read failed: {e}")
        return _fallback_library(errors)

    df = _normalise_columns(df)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
        return _fallback_library(errors)

    if "status" in df.columns:
        status = df["status"].astype(str).str.strip().str.lower()
        df = df[status.isin(["active", "nan", ""]) | df["status"].isna()]

    by_misc: Dict[str, Dict[str, Any]] = {}
    seen_ids = set()

    for _, row in df.iterrows():
        iid = str(row["intervention_id"]).strip()
        mid = str(row["misconception_id"]).strip()
        pattern = str(row["intervention_pattern"]).strip()
        topic = str(row["topic"]).strip()

        if not iid or iid.lower() == "nan":
            errors.append("Blank intervention_id skipped")
            continue
        if not mid or mid.lower() == "nan":
            errors.append(f"Blank misconception_id for {iid}")
            continue
        if not pattern or pattern.lower() == "nan":
            errors.append(f"Blank intervention_pattern for {iid}")
            continue
        if iid in seen_ids:
            errors.append(f"Duplicate intervention_id: {iid}")
            continue
        seen_ids.add(iid)

        if mid not in by_misc:
            by_misc[mid] = {
                "intervention_id": iid,
                "intervention_pattern": pattern,
                "topic": topic,
                "misconception_id": mid,
            }

    if not by_misc:
        errors.append("No valid intervention rows after validation")
        return _fallback_library(errors)

    return N08Library(
        by_misconception=by_misc,
        source_path=str(path),
        source_hash=_file_hash(path),
        load_status="csv",
        validation_errors=errors,
    )


_LIBRARY: Optional[N08Library] = None


def get_library(force_reload: bool = False, csv_path: Optional[Path] = None) -> N08Library:
    global _LIBRARY
    if _LIBRARY is None or force_reload or csv_path is not None:
        _LIBRARY = load_n08_library(csv_path)
    return _LIBRARY


def select_intervention_from_library(
    diagnosis: DiagnosisResult,
    library: Optional[N08Library] = None,
) -> Tuple[InterventionSelection, str]:
    """
    Lookup order:
      1) loaded library (csv or fallback library)
      2) curated FALLBACK_MAP (if CSV loaded but IDs differ)
      3) true generic fallback
    """
    lib = library or get_library()
    mid = diagnosis.misconception_id

    if not mid:
        sel = InterventionSelection(
            intervention_pattern="IP_GENERIC_PROMPT",
            provenance=ProvenanceKind.GENERIC_FALLBACK,
            n08_intervention_id=None,
            rule_id="ISEL_GENERIC",
            notes="No misconception id; generic prompt.",
        )
        return sel, "fallback"

    # 1) Library hit (CSV or full fallback library)
    row = lib.by_misconception.get(mid)
    if row:
        source = lib.load_status  # "csv" or "fallback"
        sel = InterventionSelection(
            intervention_pattern=row["intervention_pattern"],
            provenance=ProvenanceKind.N08_BACKED,
            n08_intervention_id=row["intervention_id"],
            rule_id="ISEL_N08_CSV" if source == "csv" else "ISEL_N08_FALLBACK_MAP",
            notes=f"source={source}; hash={lib.source_hash}",
        )
        return sel, source

    # 2) Curated map even when CSV loaded with different IDs
    if mid in FALLBACK_MAP:
        pattern, n08_id = FALLBACK_MAP[mid]
        sel = InterventionSelection(
            intervention_pattern=pattern,
            provenance=ProvenanceKind.N08_BACKED,
            n08_intervention_id=n08_id,
            rule_id="ISEL_N08_FALLBACK_MAP",
            notes="csv/library miss; used curated FALLBACK_MAP",
        )
        return sel, "fallback_map"

    # 3) True generic
    sel = InterventionSelection(
        intervention_pattern="IP_GENERIC_PROMPT",
        provenance=ProvenanceKind.GENERIC_FALLBACK,
        n08_intervention_id=None,
        rule_id="ISEL_UNMAPPED_MISCONCEPTION",
        notes=f"Misconception {mid} not in CSV or FALLBACK_MAP.",
    )
    return sel, "fallback"
