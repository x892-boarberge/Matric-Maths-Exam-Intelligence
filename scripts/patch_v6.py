"""Quick patch: add COUNTING PRINCIPLE to topic map. Re-run."""
import re
from pathlib import Path

P = Path("scripts/parse_diagnostic_v6.py")
src = P.read_text(encoding="utf-8")

old = '"DATA HANDLING": "STAT", "STATISTICS": "STAT",\n    "MEASUREMENT": "MEAS",'
new = '''"DATA HANDLING": "STAT", "STATISTICS": "STAT",
    "MEASUREMENT": "MEAS", "COUNTING PRINCIPLE": "PROB",
    "COUNTING PRINCIPLES": "PROB",'''

if old in src:
    src = src.replace(old, new, 1)
    P.write_text(src, encoding="utf-8")
    print("Added COUNTING PRINCIPLE -> PROB")
else:
    print("WARN anchor not found")