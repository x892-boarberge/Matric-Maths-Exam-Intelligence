"""Universal CLI Refinements: v=variant, q=menu, no hardcoded elif chain."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

# 1. Make "v" trigger variants immediately
old_v = '''            if _ln.lower() == "v":
                print("\\n  Variants come after a failed attempt - try 'done' first.\\n")
                continue'''
new_v = '''            if _ln.lower() == "v":
                # Universal refinement: allow variants anytime
                return "VARIANT"'''
if old_v in src:
    src = src.replace(old_v, new_v, 1)
    print("Patch 1 applied: 'v' triggers variants immediately")
else:
    print("WARN: 'v' anchor not found or already patched.")

# 2. Make "q" trigger a navigation menu instead of just skipping
old_q = '''            if _ln.lower() == "q":
                print("\\n  (quit this question)")
                return None'''
new_q = '''            if _ln.lower() == "q":
                # Universal refinement: q opens escape menu
                print("\\n------------------------------------------------------------")
                print("  What would you like to do?")
                print("    1. Skip this question")
                print("    2. Main menu")
                print("    3. Quit entirely")
                print("------------------------------------------------------------")
                _choice = input("  > ").strip()
                if _choice == "1":
                    return None
                elif _choice == "2":
                    return "MENU"
                elif _choice == "3":
                    return "QUIT"
                else:
                    return None'''
if old_q in src:
    src = src.replace(old_q, new_q, 1)
    print("Patch 2 applied: 'q' opens escape menu")
else:
    print("WARN: 'q' anchor not found or already patched.")

# 3. Strip the hardcoded elif chain, enforce universal get_teaching() pipe
old_elif = '''                if _lesson:
                    for _ln in _lesson.split("\\n"):
                        print("  Tanaka: " + _ln if _ln.strip() else "")
                elif obj and obj.get("learner_message"):
                    print(f"  Tanaka: {obj['learner_message']}")
                elif misconception == "M_INCOMPLETE_ROOTS":
                    print("  Tanaka: You gave one root. A quadratic has two. The second one is missing.")
                elif misconception == "M_CALCULATION_ERROR":
                    print("  Tanaka: Your method is right, but the final number is wrong. Go back to your last step and recalculate carefully.")
                elif misconception == "M_COORDINATE_SWAP":
                    print("  Tanaka: You swapped x and y. Read the question again: which value is x, and which is y?")
                elif misconception == "M_INEQ_SIGN_FLIP":
                    print("  Tanaka: Your interval boundaries are almost right, but one sign is flipped. Check whether each boundary should be negative or positive.")
                elif misconception == "M_INEQ_EQUATION_FORM":
                    print("  Tanaka: You wrote an equation. This is an inequality. Write your answer as an interval like 'x < a or x > b'.")
                elif misconception == "M_INEQ_MISSING_INTERVAL":
                    print("  Tanaka: You found one interval, but there's a second one. A quadratic inequality usually has two parts joined by 'or'.")
                elif misconception == "M_SURD_CALCULATION_ERROR":
                    print("  Tanaka: The method is right, but the final number is wrong. Did you square both sides and reject the extraneous root?")
                elif misconception == "M_COORDINATE_SIGN_FLIP":
                    print("  Tanaka: The number is right, but one sign is flipped. Check your x and y values against your working.")
                elif misconception == "M_INCOMPLETE_PAIR":
                    print("  Tanaka: You found the x values but not the y values. A simultaneous equation answer needs both.")
                elif misconception == "M_UNITS_IN_ANSWER":
                    print("  Tanaka: Your numbers are right, but you've attached units. In 'solve for x' questions, leave off the units — write just the number. The examiner marks you down for it.")
                elif misconception == "M_LOG_BASE_INVERTED":
                    print("  Tanaka: Check your base. The base of the log and the base in the exponent must match. If you invert the base, you must flip the sign of the answer.")
                else:
                    print(f"  Tanaka: There is a mistake here. Let's look at it together.")'''

new_elif = '''                if _lesson:
                    for _ln in _lesson.split("\\n"):
                        print("  Tanaka: " + _ln if _ln.strip() else "")
                elif obj and obj.get("learner_message"):
                    print(f"  Tanaka: {obj['learner_message']}")
                else:
                    print(f"  Tanaka: There is a mistake here. Let's look at it together.")'''

if old_elif in src:
    src = src.replace(old_elif, new_elif, 1)
    print("Patch 3 applied: Hardcoded elif chain removed (universal pipe enforced)")
else:
    print("WARN: elif chain anchor not found. You may have already modified it.")

target.write_text(src, encoding="utf-8")
print("\\nUniversal CLI Refinements applied successfully.")
