"""Add CELEBRATION and META_COMMENT kinds. Fix hint escalation default."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIS = ROOT / "src" / "tutor" / "disengagement.py"
HINT = ROOT / "src" / "tutor" / "hint_policy.py"

# ---------- Disengagement kinds ----------
src = DIS.read_text(encoding="utf-8")

if "CELEBRATION" not in src:
    src = src.replace(
        'class DisengagementKind(str, Enum):\n    OTHER_LANGUAGE = "other_language"',
        'class DisengagementKind(str, Enum):\n    OTHER_LANGUAGE = "other_language"\n    CELEBRATION = "celebration"\n    META_COMMENT = "meta_comment"',
        1,
    )
    print("Added CELEBRATION and META_COMMENT kinds")

if "CELEBRATION_MARKERS" not in src:
    markers = '''


CELEBRATION_MARKERS = [
    "am i a genius", "i am a genius", "im a genius", "i'm a genius",
    "i got it", "i solved it", "i got the answer", "i finally got",
    "yes i did it", "i did it", "nailed it", "easy", "that was easy",
    "i am the best", "im the best", "i am smart", "im smart",
    "correct right", "how was that", "did i get it", "is that right",
    "check me", "am i right", "yes!", "yes!!", "got it",
]


META_COMMENT_MARKERS = [
    "are you real", "are you human", "are you a bot", "are you an ai",
    "are you an a.i", "you are just an a.i", "just an ai", "just a bot",
    "who are you", "who made you", "where did you go",
    "where are you", "are you there", "you there",
    "do you sleep", "do you eat", "are you a person",
    "is this chatgpt", "is this ai", "what model are you",
]


def _matches_markers(text: str, markers) -> bool:
    if not isinstance(text, str):
        return False
    low = text.lower()
    return any(m in low for m in markers)

'''
    idx = src.find("class DisengagementKind")
    if idx > 0:
        src = src[:idx] + markers.lstrip("\n") + "\n" + src[idx:]
        print("Marker lists added")

# Insert detection before the final return
if "_matches_markers" in src and "CELEBRATION_MARKERS" in src:
    if "if _matches_markers(text, CELEBRATION_MARKERS)" not in src:
        idx = src.rfind("    return DisengagementResult")
        if idx > 0:
            check = '''    # Celebration - learner just succeeded
    if _matches_markers(text, CELEBRATION_MARKERS):
        return DisengagementResult(
            kind=DisengagementKind.CELEBRATION,
            matched_phrase="celebration",
        )

    # Meta-comment about the tutor
    if _matches_markers(text, META_COMMENT_MARKERS):
        return DisengagementResult(
            kind=DisengagementKind.META_COMMENT,
            matched_phrase="meta_comment",
        )

'''
            src = src[:idx] + check + src[idx:]
            print("Celebration + meta_comment detection inserted")

DIS.write_text(src, encoding="utf-8")

# ---------- Hint policy fix ----------
h = HINT.read_text(encoding="utf-8")

old_dict = '''HINT_ESCALATION = {
    1: HintLevel.H0,
    2: HintLevel.H1,
    3: HintLevel.H2,
    4: HintLevel.H3,
    5: HintLevel.H4,
}'''

new_dict = '''HINT_ESCALATION = {
    0: HintLevel.H0,
    1: HintLevel.H0,
    2: HintLevel.H1,
    3: HintLevel.H2,
    4: HintLevel.H3,
    5: HintLevel.H4,
}'''

if old_dict in h:
    h = h.replace(old_dict, new_dict, 1)
    HINT.write_text(h, encoding="utf-8")
    print("Hint escalation now includes 0 -> H0 (safe default)")
else:
    print("Hint dict not found - check hint_policy.py manually")

print()
print("Patch 1 complete")
