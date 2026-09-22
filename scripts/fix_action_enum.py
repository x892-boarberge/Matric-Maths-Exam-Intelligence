"""Add OFFER_WORKED_ANALOGUE to ActionType."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "src" / "tutor" / "schemas.py"
src = SCHEMAS.read_text(encoding="utf-8")

if "OFFER_WORKED_ANALOGUE" in src:
    print("Already present")
else:
    old = '    FLAG_FOR_HUMAN = "FLAG_FOR_HUMAN"'
    new = '    FLAG_FOR_HUMAN = "FLAG_FOR_HUMAN"\n    OFFER_WORKED_ANALOGUE = "OFFER_WORKED_ANALOGUE"'
    if old in src:
        src = src.replace(old, new, 1)
        SCHEMAS.write_text(src, encoding="utf-8")
        print("OFFER_WORKED_ANALOGUE added to ActionType")
    else:
        print("WARNING - FLAG_FOR_HUMAN line not found")
