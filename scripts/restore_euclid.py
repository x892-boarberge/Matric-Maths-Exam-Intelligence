"""Restore EUCL to 15+ proofs. Merges via EXTRA_WRITTEN_ANALOGUES."""
from pathlib import Path
import ast
import re

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# How many entries currently in euclidean_written?
count = 0
for m in re.finditer(r'"problem"\s*:', src):
    pass

# Simpler: check if EXTRA already has euclidean_written
if '"euclidean_written"' in src.split("EXTRA_WRITTEN_ANALOGUES")[1][:3000] if "EXTRA_WRITTEN_ANALOGUES" in src else False:
    print("EXTRA_WRITTEN_ANALOGUES already has euclidean_written")
    raise SystemExit(0)

# Find EXTRA_WRITTEN_ANALOGUES block end (last closing brace before TEMPLATES)
idx = src.find("EXTRA_WRITTEN_ANALOGUES")
if idx < 0:
    print("EXTRA_WRITTEN_ANALOGUES not found")
    raise SystemExit(1)

# Find opening brace
brace = src.find("{", idx)
depth = 0
end = brace
for i in range(brace, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

if end == brace:
    print("Could not find closing brace")
    raise SystemExit(1)

EUCL_BLOCK = '''
    "euclidean_written": [
        {"problem": "In circle O, AB is a diameter and C lies on the circle. Prove angle ACB = 90.", "steps": ["AB is a diameter.", "C is on the circumference.", "Theorem: angle in a semicircle is 90.", "Therefore angle ACB = 90."], "note": "Always remember: name the theorem."},
        {"problem": "ABCD is a cyclic quadrilateral. Prove angle A + angle C = 180.", "steps": ["All four vertices on a circle.", "Theorem: opposite angles of cyclic quad are supplementary.", "A + C = 180."], "note": "Always remember: reason is 'opposite angles of cyclic quad'."},
        {"problem": "Tangent ST touches circle at T. P, Q on circle. Prove angle STP = angle TQP.", "steps": ["Theorem: angle between tangent and chord equals angle in alternate segment.", "Chord is TP.", "Alternate segment angle is TQP.", "Therefore angle STP = angle TQP."], "note": "Always remember: this is the tan-chord theorem."},
        {"problem": "AB, CD are parallel chords of circle O. Prove arc AC = arc BD.", "steps": ["Parallel chords cut off equal arcs.", "Draw radii OA, OB, OC, OD.", "Equal arcs have equal central angles.", "Therefore arc AC = arc BD."], "note": "Always remember: parallel chords cut off equal arcs."},
        {"problem": "Two circles intersect at A and B. Prove line joining centres is perpendicular to AB.", "steps": ["Let centres be P and Q.", "PA = PB (radii).", "QA = QB (radii).", "Both P and Q lie on perpendicular bisector of AB.", "Therefore PQ perpendicular to AB."], "note": "Always remember: perpendicularity via perpendicular bisector."},
        {"problem": "Triangle ABC right-angled at C, altitude CD to AB. Prove AD x DB = CD^2.", "steps": ["Angle ACB = 90.", "Altitude to hypotenuse creates three similar triangles.", "Triangle ACD similar to triangle CBD.", "AD/CD = CD/DB.", "AD x DB = CD^2."], "note": "Always remember: altitude-to-hypotenuse theorem."},
        {"problem": "ABCD is a parallelogram inscribed in circle O. Prove ABCD is a rectangle.", "steps": ["Cyclic parallelogram: opposite angles sum to 180.", "Parallelogram: opposite angles are equal.", "Each opposite angle is 90.", "Therefore rectangle."], "note": "Always remember: cyclic parallelogram is a rectangle."},
        {"problem": "Two tangents from P touch circle O at A and B. Prove PA = PB.", "steps": ["Draw OA, OB (radii).", "OA perpendicular PA; OB perpendicular PB.", "Right triangles OAP and OBP.", "OA = OB (radii), OP common.", "Congruent (RHS).", "PA = PB."], "note": "Always remember: tangents from a common point are equal."},
        {"problem": "Chords AB, CD intersect at P inside circle O. Prove AP x PB = CP x PD.", "steps": ["Draw chords AC, BD.", "Triangle APC similar to triangle DPB.", "AP/DP = CP/PB.", "AP x PB = CP x PD."], "note": "Always remember: intersecting chords theorem."},
        {"problem": "Prove angle at centre = 2x angle at circumference.", "steps": ["Draw chord AB, centre O, point P on circle.", "Draw PO and produce to Q.", "Angle AOQ = exterior angle of triangle AOP.", "OA = OP, so isosceles. Angle OAP = angle OPA.", "Angle AOQ = 2 x angle OPA.", "Similarly angle BOQ = 2 x angle OPB.", "Add: angle AOB = 2 x angle APB."], "note": "Always remember: central angle theorem. State construction first."},
        {"problem": "Triangle ABC with AB = AC, D midpoint of BC. Prove AD perpendicular to BC.", "steps": ["AB = AC, so triangle isosceles.", "D midpoint, so BD = DC.", "AD common.", "Triangles ABD, ACD congruent (SSS).", "Angle ADB = angle ADC.", "Supplementary, so each is 90.", "AD perpendicular to BC."], "note": "Always remember: perpendicularity via congruent triangles."},
        {"problem": "ABCD is cyclic quad, AB extended to E. Prove angle CBE = angle ADC.", "steps": ["Cyclic: angle ABC + angle ADC = 180.", "Straight line: angle ABC + angle CBE = 180.", "Therefore angle CBE = angle ADC."], "note": "Always remember: exterior angle of cyclic quad = opposite interior angle."},
        {"problem": "In circle O, PA tangent and PB secant through C and B. Prove PA^2 = PC x PB.", "steps": ["Draw chords AC and AB.", "Angle PCA = angle PAB (tan-chord theorem).", "Triangle PCA similar to triangle PAB (shared angle P).", "PA/PB = PC/PA.", "PA^2 = PC x PB."], "note": "Always remember: tangent-secant theorem."},
    ],
'''

# Insert before the closing brace of EXTRA
src = src[:end] + EUCL_BLOCK + src[end:]

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Added euclidean_written (13 proofs) to EXTRA_WRITTEN_ANALOGUES")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)