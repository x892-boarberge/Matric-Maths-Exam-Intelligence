"""Fix the five lines that failed the salt check."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "src" / "tutor" / "meta_library.py"
SALT = ROOT / "src" / "tutor" / "salt_check.py"

# ---------- Meta library line fixes ----------

meta = META.read_text(encoding="utf-8")

replacements = [
    # 1. "No. But here is..." - no warmth
    (
        "No. But here is what I will do: I will help you see where you went wrong. Show me your last step.",
        "I hear you. I will not give the answer, but I can help you find it. What is your last step?",
    ),
    # 2. "Alright... you need to" - forbidden phrase
    (
        "Alright. First move only. What is the operation you need to undo to start?",
        "Alright. First move only. Which operation do you undo first?",
    ),
    # 3. "So near. One thing is off by a little. Check..." - no warmth
    (
        "So near. One thing is off by a little. Check your arithmetic in the last line.",
        "So near. One thing is off by a little. What does your last line say?",
    ),
    # 4. "There it is. And you found it yourself..." - no warmth
    (
        "There it is. And you found it yourself after a few tries. That is how this works. The struggle is the learning. Let us keep going.",
        "Good - you found it yourself after a few tries. That is how this works, and the struggle is the learning. Let us keep going.",
    ),
    (
        "There it is. And you found it yourself after a few tries. That is how this works. The struggle is the learning. Let's keep going.",
        "Good - you found it yourself after a few tries. That is how this works, and the struggle is the learning. Let's keep going.",
    ),
    # 5. "Correct. Onwards." - no warmth
    (
        "\"Correct. Onwards.\",",
        "\"Good - onwards.\",",
    ),
]

for old, new in replacements:
    if old in meta:
        meta = meta.replace(old, new, 1)
        print("Fixed:", old[:50])
    else:
        print("Not found:", old[:50])

META.write_text(meta, encoding="utf-8")

# ---------- Add 'alright' to warmth openers ----------

salt = SALT.read_text(encoding="utf-8")

old_warm = '''WARMTH_OPENERS = [
    "okay", "that is", "that's", "let's", "let us",
    "i hear", "i know", "i understand", "i am not",
    "not a problem", "no rush", "no problem",
    "fine", "right", "good", "nice",
    "very close", "nearly", "close", "almost",
    "take", "yes",
]'''

new_warm = '''WARMTH_OPENERS = [
    "okay", "alright", "that is", "that's", "let's", "let us",
    "i hear", "i know", "i understand", "i am not",
    "not a problem", "no rush", "no problem",
    "fine", "right", "good", "nice",
    "very close", "nearly", "close", "almost",
    "so near", "take", "yes",
]'''

if old_warm in salt:
    salt = salt.replace(old_warm, new_warm, 1)
    print("salt_check.py: added 'alright' and 'so near' to warmth openers")
else:
    print("WARNING - warmth opener block not found in salt_check.py")

SALT.write_text(salt, encoding="utf-8")

print()
print("Fix script complete")
