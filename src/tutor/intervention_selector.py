from .schemas import DiagnosisResult, InterventionSelection
from .n08_loader import select_intervention_from_library, get_library


def select_intervention(diagnosis: DiagnosisResult) -> InterventionSelection:
    selection, _source = select_intervention_from_library(diagnosis)
    return selection


def select_intervention_with_source(diagnosis: DiagnosisResult):
    return select_intervention_from_library(diagnosis)


def library_status() -> dict:
    lib = get_library()
    return {
        "load_status": lib.load_status,
        "source_path": lib.source_path,
        "source_hash": lib.source_hash,
        "n_misconceptions": len(lib.by_misconception),
        "keys_sample": list(lib.by_misconception.keys())[:10],
        "validation_errors": list(lib.validation_errors),
    }
