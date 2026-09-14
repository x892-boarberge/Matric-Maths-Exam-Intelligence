from .schemas import DiagnosisResult, InterventionSelection, ProvenanceKind

N08_INTERVENTION_MAP = {
    "M_SIGN_ERROR_FACTORISATION": ("IP_MISCONCEPTION_CONTRAST", "N08_ALG_QUAD_SIGN_01"),
    "M_TP_COORD_CONFUSION": ("IP_REPRESENTATION_SHIFT", "N08_FUNC_PARAB_02"),
    "M_REDUCTION_SIGN": ("IP_MISCONCEPTION_CONTRAST", "N08_TRIG_RED_01"),
    "M_DIAGRAM_ASSUMPTION": ("IP_STEP_ISOLATION", "N08_AGEO_PROOF_01"),
    "M_MISSING_THEOREM_CITATION": ("IP_SELF_EXPLANATION", "N08_EUCL_PROOF_01"),
}


def select_intervention(diagnosis: DiagnosisResult) -> InterventionSelection:
    mid = diagnosis.misconception_id
    if not mid:
        return InterventionSelection(
            intervention_pattern="IP_GENERIC_PROMPT",
            provenance=ProvenanceKind.GENERIC_FALLBACK,
            n08_intervention_id=None,
            rule_id="ISEL_GENERIC",
            notes="No misconception id; falling back to generic prompt.",
        )

    if mid in N08_INTERVENTION_MAP:
        pattern, n08_id = N08_INTERVENTION_MAP[mid]
        return InterventionSelection(
            intervention_pattern=pattern,
            provenance=ProvenanceKind.N08_BACKED,
            n08_intervention_id=n08_id,
            rule_id="ISEL_N08_LOOKUP",
        )

    return InterventionSelection(
        intervention_pattern="IP_GENERIC_PROMPT",
        provenance=ProvenanceKind.GENERIC_FALLBACK,
        n08_intervention_id=None,
        rule_id="ISEL_UNMAPPED_MISCONCEPTION",
        notes=f"Misconception {mid} not in N08 map.",
    )