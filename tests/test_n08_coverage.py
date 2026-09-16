import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
from src.tutor.diagnosis import reachable_misconception_ids
from src.tutor.n08_loader import get_library


def test_all_n08_ids_reachable():
    lib = get_library(force_reload=True)
    n08_ids = set(lib.by_misconception.keys())
    diag_ids = reachable_misconception_ids()
    missing = n08_ids - diag_ids
    assert not missing, f"N08 IDs with no diagnosis path: {missing}"


def test_no_unknown_misconception_ids():
    lib = get_library(force_reload=True)
    n08_ids = set(lib.by_misconception.keys())
    diag_ids = reachable_misconception_ids()
    extra = diag_ids - n08_ids
    assert not extra, f"Diagnosis IDs not in N08 CSV: {extra}"