"""Salt check must accept colons and semicolons after warmth openers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALT = ROOT / "src" / "tutor" / "salt_check.py"
src = SALT.read_text(encoding="utf-8")

old = '''    # Warmth signal
    if "?" in line:
        return True, ""
    for opener in WARMTH_OPENERS:
        if low.startswith(opener + " ") or low.startswith(opener + ",") or low.startswith(opener + "."):
            return True, ""
    # Also allow warmth mid-line for very short lines
    for opener in WARMTH_OPENERS:
        if " " + opener + " " in low[:40]:
            return True, ""'''

new = '''    # Warmth signal
    if "?" in line:
        return True, ""
    punct = [" ", ",", ".", ":", ";", "!", "-", "\\u2014"]
    for opener in WARMTH_OPENERS:
        for p in punct:
            if low.startswith(opener + p):
                return True, ""
    # Also allow warmth mid-line for very short lines
    for opener in WARMTH_OPENERS:
        if " " + opener + " " in low[:40]:
            return True, ""'''

if old in src:
    src = src.replace(old, new, 1)
    SALT.write_text(src, encoding="utf-8")
    print("Salt check now accepts colons and other punctuation")
else:
    print("WARNING - warmth block not found. Inspect salt_check.py manually.")
    # Print the warmth section for inspection
    idx = src.find("Warmth signal")
    if idx > 0:
        print()
        print("Current warmth block:")
        print(src[idx:idx+500])
