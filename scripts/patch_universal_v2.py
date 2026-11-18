"""Universal CLI refinements: migrate elif→TEACHINGS, delete chain, q menu, v works."""
import sys, datetime
from pathlib import Path

# ============================================================
# PART 1 — Add 8 missing TEACHINGS for elif-chain messages
# ============================================================
diag = Path("src/tutor/diagnosis.py")
diag_backup = diag.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
diag_backup.write_bytes(diag.read_bytes())
print(f"Backup: {diag_backup}")

diag_src = diag.read_text(encoding="utf-8")

if '"M_UNITS_IN_ANSWER": (' in diag_src and 'leave off the units' in diag_src:
    print("SKIP: 8 elif-migrations already added")
else:
    new_teachings = '''"M_COORDINATE_SWAP": (
        "You swapped x and y.\\n\\n"
        "  A point is always written (x; y) — x comes first.\\n"
        "  Read the question again: which value is x, and which is y?\\n\\n"
        "  Check your working: did you swap the values when writing the coordinates?"
    ),
    "M_INEQ_SIGN_FLIP": (
        "Your interval boundaries are almost right, but one sign is flipped.\\n\\n"
        "  When you multiply or divide an inequality by a negative number, the inequality sign FLIPS.\\n"
        "  Example: -2x > 6 becomes x < -3, not x > -3.\\n\\n"
        "  Check your working: did you flip the sign when you divided by a negative?"
    ),
    "M_INEQ_EQUATION_FORM": (
        "You wrote an equation, but this is an inequality.\\n\\n"
        "  Inequalities need interval notation or a comparison symbol: x < a, x > b, or x < a or x > b.\\n"
        "  Using '=' when the question says 'inequality' loses the mark.\\n\\n"
        "  Check your working: did you end with 'x = ...' instead of 'x < ...' or 'x > ...'?"
    ),
    "M_INEQ_MISSING_INTERVAL": (
        "You found one interval, but there is a second one.\\n\\n"
        "  A quadratic inequality usually has TWO parts joined by 'or'.\\n"
        "  Example: x^2 > 9 means x > 3 OR x < -3.\\n"
        "  Both intervals are required for full marks.\\n\\n"
        "  Check your working: did you write both parts with 'or' between them?"
    ),
    "M_SURD_CALCULATION_ERROR": (
        "The method is right, but the final number is wrong.\\n\\n"
        "  In surd equations, you must square both sides and then REJECT any extraneous root.\\n"
        "  Check every root against the original equation — one of them may not work.\\n\\n"
        "  Check your working: did you square both sides fully, and reject the root that fails?"
    ),
    "M_COORDINATE_SIGN_FLIP": (
        "The number is right, but one sign is flipped.\\n\\n"
        "  When writing coordinates, the sign inside the bracket corresponds to the position on the axes.\\n"
        "  Left of the y-axis = negative x. Below the x-axis = negative y.\\n\\n"
        "  Check your working: are both signs correct for where the point lies?"
    ),
    "M_INCOMPLETE_PAIR": (
        "You found the x values but not the y values.\\n\\n"
        "  A simultaneous equation answer needs BOTH x and y as a pair.\\n"
        "  Substitute your x-value back into one of the original equations to find y.\\n\\n"
        "  Check your working: did you give the answer as (x; y)?"
    ),
    "M_UNITS_IN_ANSWER": (
        "Your numbers are right, but you attached units.\\n\\n"
        "  In 'solve for x' questions, the answer is just a number — no units.\\n"
        "  Units are for real-world quantities (length, money, time), not for algebraic variables.\\n\\n"
        "  Check your working: did you write 'x = 5 cm' instead of just 'x = 5'?"
    ),
    '''

    anchor = '"M_INVERSE_ALWAYS_LOG": ('
    if anchor not in diag_src:
        print("FATAL: TEACHINGS anchor not found")
        sys.exit(1)
    diag_src = diag_src.replace(anchor, new_teachings + anchor, 1)
    diag.write_text(diag_src, encoding="utf-8")
    print("PART 1 ✓ — Added 8 TEACHINGS for elif-chain messages")


# ============================================================
# PART 2 — Delete elif chain + 3,4 (q menu, v works) in CLI
# ============================================================
cli = Path("scripts/cli_tutor.py")
cli_backup = cli.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
cli_backup.write_bytes(cli.read_bytes())
print(f"Backup: {cli_backup}")

cli_src = cli.read_text(encoding="utf-8")

# 2. Delete the entire elif chain (1000-1021) — keep only else
old_elif = '''                elif misconception == "M_INCOMPLETE_ROOTS":
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
                else:
                    print(f"  Tanaka: There is a mistake here. Let's look at it together.")'''

new_elif = '''                else:
                    print(f"  Tanaka: There is a mistake here. Let's look at it together.")'''

if old_elif not in cli_src:
    print("WARN: elif chain anchor not found (may be already deleted)")
else:
    cli_src = cli_src.replace(old_elif, new_elif, 1)
    print("PART 2 ✓ — elif chain deleted (universal pipe enforced)")

# 3. Replace v-handler — return VARIANT marker
old_v = '''        if low == "v":
            print()
            print("  Variants come after a failed attempt - try 'done' first.")
            print()
            continue'''
new_v = '''        if low == "v":
            # universal refinement: allow variants on demand
            return "VARIANT"'''

if old_v not in cli_src:
    print("WARN: v-handler anchor not found")
else:
    cli_src = cli_src.replace(old_v, new_v, 1)
    print("PART 3 ✓ — v-handler returns VARIANT (on demand)")

# 4. Insert q menu before existing q-handler
old_q_anchor = '''        if low in ("q", "quit", "exit"):'''
new_q_block = '''        if low in ("q", "quit", "exit"):
            # universal refinement: 3-option escape menu
            print("\\n------------------------------------------------------------")
            print("  What would you like to do?")
            print("    1. Skip this question")
            print("    2. Main menu")
            print("    3. Quit entirely")
            print("------------------------------------------------------------")
            _choice = input("  > ").strip()
            if _choice == "2":
                return "MENU"
            elif _choice == "3":
                return "QUIT"
            # choice 1 or invalid -> fall through to original skip
        if low in ("q", "quit", "exit"):'''

if new_q_block in cli_src:
    print("SKIP: q menu already inserted")
elif old_q_anchor not in cli_src:
    print("WARN: q anchor not found")
else:
    # Only replace the FIRST occurrence (the main loop, not variant loop)
    cli_src = cli_src.replace(old_q_anchor, new_q_block, 1)
    print("PART 4 ✓ — q menu inserted before existing handler")

cli.write_text(cli_src, encoding="utf-8")
print(f"\\nFile: {cli}")
