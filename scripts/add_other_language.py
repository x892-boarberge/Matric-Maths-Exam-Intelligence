"""Add OTHER_LANGUAGE handling to disengagement, meta library, and dispatch."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIS = ROOT / "src" / "tutor" / "disengagement.py"
META = ROOT / "src" / "tutor" / "meta_library.py"

# ---------- 1. Add OTHER_LANGUAGE to the enum ----------
src = DIS.read_text(encoding="utf-8")

if "OTHER_LANGUAGE" not in src:
    src = src.replace(
        "class DisengagementKind(str, Enum):",
        "class DisengagementKind(str, Enum):\n    OTHER_LANGUAGE = \"other_language\"",
        1,
    )
    print("OTHER_LANGUAGE kind added")

# ---------- 2. Add detection markers and logic ----------
if "SA_LANGUAGE_MARKERS" not in src:
    markers = '''


# Words that are clearly not English. A single hit is not enough;
# we require 2+ markers before firing, to avoid false positives.
SA_LANGUAGE_MARKERS = [
    # Afrikaans
    "nie", "ek", "jy", "julle", "hulle", "hierdie", "daardie",
    "baie", "klein", "groot", "maar", "ook", "nog", "want",
    "waar", "wanneer", "hoekom", "asseblief", "dankie",
    "verstaan", "verduidelik", "geleer", "gese", "reg",
    "verkeerd", "maklik", "moeilik", "sommer", "net", "al",
    # isiZulu and isiXhosa
    "yebo", "cha", "haibo", "eish", "yoh",
    "ngiyazi", "angazi", "ngiyabonga", "ngicela",
    "yini", "kanjani", "kuhle", "kubi", "kodwa", "futhi",
    "manje", "ngoba", "noma", "ndiyazi", "andazi",
    "ndiyabulela", "ndicela", "ntoni", "njani",
    "kwaye", "ngoku", "yinhle", "utlwisisa", "utlwa",
    "sawubona", "sanibonani", "molo",
    # Sesotho, Sepedi, Setswana
    "dumela", "kea", "leboha", "kopa", "gore", "gona",
    "fela", "nnete", "jwang", "empa", "hape", "jwale",
    "hantle", "tseba", "utlwisisa",
    # SA English slang
    "eish", "haibo", "howzit", "bra", "bru", "lekker", "kiff",
]


def _looks_like_other_language(text: str) -> bool:
    if not isinstance(text, str):
        return False
    low = text.lower()
    hits = 0
    for word in SA_LANGUAGE_MARKERS:
        if " " + word + " " in " " + low + " ":
            hits += 1
            if hits >= 2:
                return True
    return False

'''
    # Insert markers before the first class definition
    idx = src.find("class DisengagementKind")
    if idx > 0:
        src = src[:idx] + markers.lstrip("\n") + "\n" + src[idx:]
        print("SA language markers added")
    else:
        print("WARNING - enum definition not found")

# ---------- 3. Add detection in detect_disengagement ----------
if "_looks_like_other_language" in src and "OTHER_LANGUAGE" in src:
    if "if _looks_like_other_language(text)" not in src:
        # Insert before the final return
        idx = src.rfind("    return DisengagementResult")
        if idx > 0:
            check = '''    # Other South African language or code-switching
    if _looks_like_other_language(text):
        return DisengagementResult(
            kind=DisengagementKind.OTHER_LANGUAGE,
            matched_phrase="language_marker",
        )

'''
            src = src[:idx] + check + src[idx:]
            print("OTHER_LANGUAGE detection inserted")
        else:
            print("WARNING - no final return found")
    else:
        print("OTHER_LANGUAGE detection already present")

DIS.write_text(src, encoding="utf-8")

# ---------- 4. Add language responses to meta_library ----------
meta = META.read_text(encoding="utf-8")

if "say_other_language" not in meta:
    block = '''


# ---------- Other language / code-switching ----------

_OTHER_LANGUAGE = [
    "I hear you. Think in whatever language helps you work. Write your answer in English if you can. What is your first step?",
    "That is fine. Use the language that helps you think. When you write the answer, use the maths language of the paper. What do you have so far?",
    "No problem. Many learners think in their home language first. What is the question asking you to find?",
    "Okay. Let us keep going. You can think in your language, and write the maths in English. Where does your working stop?",
    "I understand. Let us focus on the maths. What is the first move you would write down?",
]

_OTHER_LANGUAGE_REPEAT = [
    "Still here. Let us look at the numbers together. What does the question give you?",
    "Okay. Take it one piece at a time. What is the first thing you notice?",
    "That is fine. Just read me the first line of the question.",
]


def say_other_language(learner_id=None, context=None):
    return pick(_OTHER_LANGUAGE, learner_id, "other_language")


def say_other_language_repeat(learner_id=None, context=None):
    return pick(_OTHER_LANGUAGE_REPEAT, learner_id, "other_language_repeat")
'''
    meta = meta.rstrip() + block

    # Extend the dispatch helper
    old_dispatch = '''    if kind_value == "hostile":
        return say_hostile_input_repeat(learner_id) if repeat else say_hostile_input(learner_id)
    return ""'''
    new_dispatch = '''    if kind_value == "hostile":
        return say_hostile_input_repeat(learner_id) if repeat else say_hostile_input(learner_id)
    if kind_value == "other_language":
        return say_other_language_repeat(learner_id) if repeat else say_other_language(learner_id)
    return ""'''
    if old_dispatch in meta:
        meta = meta.replace(old_dispatch, new_dispatch, 1)
        print("Dispatch extended for other_language")
    else:
        print("WARNING - dispatch block not found")

    META.write_text(meta, encoding="utf-8")
    print("Language responses added to meta_library")
else:
    print("Language responses already present")

print()
print("Patch complete")
