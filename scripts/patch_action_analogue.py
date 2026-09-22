"""Add OFFER_WORKED_ANALOGUE to ActionType enum."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "src" / "tutor" / "schemas.py"
src = SCHEMAS.read_text(encoding="utf-8")

if "OFFER_WORKED_ANALOGUE" in src:
    print("Already present")
else:
    old = '''    FLAG_FOR_HUMAN = "FLAG_FOR_HUMAN"
    HANDLE_DISENGAGEMENT = "HANDLE_DISENGAGEMENT"'''
    new = '''    FLAG_FOR_HUMAN = "FLAG_FOR_HUMAN"          # deprecated, kept for compat
    OFFER_WORKED_ANALOGUE = "OFFER_WORKED_ANALOGUE"
    HANDLE_DISENGAGEMENT = "HANDLE_DISENGAGEMENT"'''
    if old in src:
        src = src.replace(old, new, 1)
        SCHEMAS.write_text(src, encoding="utf-8")
        print("OFFER_WORKED_ANALOGUE added")
    else:
        print("WARNING - ActionType block not found")
