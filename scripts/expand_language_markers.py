"""Add more SA language markers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIS = ROOT / "src" / "tutor" / "disengagement.py"
src = DIS.read_text(encoding="utf-8")

if '"die", "te", "vraag"' in src:
    print("Markers already expanded")
else:
    old = '''SA_LANGUAGE_MARKERS = [
    # Afrikaans
    "nie", "ek", "jy", "julle", "hulle", "hierdie", "daardie",
    "baie", "klein", "groot", "maar", "ook", "nog", "want",
    "waar", "wanneer", "hoekom", "asseblief", "dankie",
    "verstaan", "verduidelik", "geleer", "gese", "reg",
    "verkeerd", "maklik", "moeilik", "sommer", "net", "al",'''

    new = '''SA_LANGUAGE_MARKERS = [
    # Afrikaans - definite/indefinite articles and common words
    "die", "n", "te", "het", "vraag", "som", "hoe", "wat",
    "nie", "ek", "jy", "julle", "hulle", "hierdie", "daardie",
    "baie", "klein", "groot", "maar", "ook", "nog", "want",
    "waar", "wanneer", "hoekom", "asseblief", "dankie",
    "verstaan", "verduidelik", "geleer", "gese", "reg",
    "verkeerd", "maklik", "moeilik", "sommer", "net", "al",'''

    if old in src:
        src = src.replace(old, new, 1)
        DIS.write_text(src, encoding="utf-8")
        print("Markers expanded")
    else:
        print("WARNING - marker block not found")
