"""Content: Add top 7 high-frequency teachings to diagnosis.py."""
import sys, datetime
from pathlib import Path

target = Path("src/tutor/diagnosis.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if '"M_SIGN_ERROR_READING_ROOT":' in src:
    print("FATAL: teachings already exist.")
    sys.exit(1)

new_entries = '''"M_SIGN_ERROR_READING_ROOT": (
        "You read the root, but the sign is flipped.\\n\\n"
        "  When you factorise or read from a graph, remember: (x - 3) means x = +3, not -3.\\n"
        "  The sign inside the bracket is the opposite of the root.\\n\\n"
        "  Check your working: did you flip the sign when you moved the term to the other side?"
    ),
    "M_INCOMPLETE_ROOTS": (
        "You gave one root, but this is a quadratic equation.\\n\\n"
        "  A quadratic equation (highest power is x^2) almost always has TWO roots.\\n"
        "  If you have x^2 = 16, then x = 4 OR x = -4.\\n\\n"
        "  Check your working: did you drop the negative root? Did you divide by x and lose a solution?"
    ),
    "M_ALG_SIGN_FLIP_FACTOR": (
        "The signs in your brackets are wrong.\\n\\n"
        "  When factorising x^2 + 5x + 6, you need two numbers that multiply to +6 and add to +5.\\n"
        "  The numbers are +2 and +3, so the brackets are (x + 2)(x + 3).\\n\\n"
        "  Check your working: do the signs inside the brackets add up to the middle term?"
    ),
    "M_SIGN_ERROR_FACTORISATION": (
        "You factorised correctly, but flipped a sign in the final step.\\n\\n"
        "  If (x + 2)(x + 3) = 0, then x + 2 = 0 or x + 3 = 0.\\n"
        "  This gives x = -2 or x = -3 (the signs flip when you move them across the equals sign).\\n\\n"
        "  Check your working: did you flip the sign when solving for x?"
    ),
    "M_CALCULATION_ERROR": (
        "Your method is right, but the final number is wrong.\\n\\n"
        "  This is a calculation error, not a misunderstanding. Go back to your last step and recalculate carefully.\\n"
        "  Did you drop a negative sign? Did you type the wrong number into your calculator?\\n\\n"
        "  Rewrite the calculation on a fresh line to double-check."
    ),
    "M_LOG_FRACTION_BASE_POSITIVE": (
        "You kept the answer positive, but the base is a fraction.\\n\\n"
        "  If the base is between 0 and 1 (like 1/2 or 1/3), the logarithm of a whole number is NEGATIVE.\\n"
        "  Example: log_{1/2}(4) = -2.\\n"
        "  Because (1/2)^-2 = 4.\\n\\n"
        "  Check your working: did you flip the sign because the base is less than 1?"
    ),
    "M_3D_WRONG_RATIO": (
        "You used the wrong trigonometric ratio for the 3D triangle.\\n\\n"
        "  In 3D trig, identify the right-angled triangle first.\\n"
        "  Label the sides opposite, adjacent, and hypotenuse relative to the angle you are working with.\\n"
        "  Then choose SOH CAH TOA based on which sides you have and which side you need.\\n\\n"
        "  Check your working: did you use the hypotenuse instead of the adjacent side?"
    ),
    '''

anchor = '"M_INVERSE_ALWAYS_LOG": ('
if anchor not in src:
    print("FATAL: TEACHINGS anchor not found")
    sys.exit(1)

src = src.replace(anchor, new_entries + anchor, 1)
target.write_text(src, encoding="utf-8")
print("7 high-frequency teachings added.")
