"""Add common teaching verbs to the warmth openers list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALT = ROOT / "src" / "tutor" / "salt_check.py"
src = SALT.read_text(encoding="utf-8")

old = '''WARMTH_OPENERS = [
    "okay", "alright", "that is", "that's", "let's", "let us",
    "i hear", "i know", "i understand", "i am not",
    "not a problem", "no rush", "no problem",
    "fine", "right", "good", "nice",
    "very close", "nearly", "close", "almost",
    "so near", "take", "yes",
]'''

new = '''WARMTH_OPENERS = [
    # Soft openers and acknowledgements
    "okay", "alright", "that is", "that's", "let's", "let us",
    "i hear", "i know", "i understand", "i am not",
    "not a problem", "no rush", "no problem",
    "fine", "right", "good", "nice",
    "very close", "nearly", "close", "almost",
    "so near", "take", "yes",
    # Teaching verbs - direct but kind, the way a tutor speaks
    "check", "look", "read", "notice", "remember", "notice",
    "try", "write", "draw", "label", "mark", "name",
    "state", "identify", "circle", "underline", "box",
    "compare", "substitute", "simplify", "factorise",
    # Explanatory openers for notes and worked examples
    "use", "the ", "in this", "when ", "if ", "for ",
    "each ", "every ", "never ", "always ", "this ",
]'''

if old in src:
    src = src.replace(old, new, 1)
    SALT.write_text(src, encoding="utf-8")
    print("Warmth list expanded with teaching verbs")
else:
    print("WARNING - warmth list not found")
