"""Add HOSTILE kind and detection to disengagement.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIS = ROOT / "src" / "tutor" / "disengagement.py"
src = DIS.read_text(encoding="utf-8")

# Add HOSTILE to the enum if missing
if "HOSTILE" not in src:
    src = src.replace(
        "class DisengagementKind(str, Enum):",
        "class DisengagementKind(str, Enum):\n    HOSTILE = \"hostile\"",
        1,
    )
    print("HOSTILE kind added to enum")

# Add hostile pattern check in detect_disengagement
if "HOSTILE" in src and "swear_words" not in src:
    # Insert hostile detection before the final return
    hostile_pattern_insert = '''    # Hostile or abusive input
    HOSTILE_WORDS = [
        "fuck", "fuk", "shit", "bullshit", "damn", "hell",
        "stupid", "idiot", "fool", "dick", "asshole", "bastard",
        "shut up", "screw you", "piss off",
    ]
    low = (text or "").lower()
    if any(w in low for w in HOSTILE_WORDS):
        return DisengagementResult(
            kind=DisengagementKind.HOSTILE,
            matched_phrase=next(w for w in HOSTILE_WORDS if w in low),
        )

'''
    # Find the last "return DisengagementResult" and put hostile check before
    idx = src.rfind("    return DisengagementResult")
    if idx > 0:
        src = src[:idx] + hostile_pattern_insert + src[idx:]
        print("Hostile pattern check inserted")
    else:
        print("WARNING - no final return found")

DIS.write_text(src, encoding="utf-8")
print("disengagement.py updated")
