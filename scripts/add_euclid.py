"""
Add EUCLID_PROOFS as a separate dict at end of file, patch generate_all to merge.
No brace matching needed.
"""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

if "EUCLID_PROOFS" in src:
    print("Already present")
    raise SystemExit(0)

# Append new dict at end of file
NEW_DICT = '''

# ==================================================================
# EUCLID_PROOFS — expanded proof bank
# ==================================================================

EUCLID_PROOFS = [
    {"problem": "In circle O, AB is a diameter and C lies on the circle. Prove angle ACB = 90.",
     "steps": ["AB is a diameter.", "C is on the circumference.", "Theorem: angle in a semicircle is 90.", "Therefore angle ACB = 90."],
     "note": "Always remember: name the theorem."},
    {"problem": "ABCD is a cyclic quadrilateral. Prove angle A + angle C = 180.",
     "steps": ["All four vertices on a circle.", "Theorem: opposite angles of cyclic quad are supplementary.", "A + C = 180."],
     "note": "Always remember: reason is 'opposite angles of cyclic quad'."},
    {"problem": "Tangent ST touches circle at T. P, Q on circle. Prove angle STP = angle TQP.",
     "steps": ["Theorem: angle between tangent and chord equals angle in alternate segment.", "Chord is TP.", "Alternate segment angle is TQP.", "Therefore angle STP = angle TQP."],
     "note": "Always remember: this is the tan-chord theorem."},
    {"problem": "AB, CD are parallel chords of circle O. Prove arc AC = arc BD.",
     "steps": ["Parallel chords cut off equal arcs.", "Draw radii OA, OB, OC, OD.", "Equal arcs have equal central angles.", "Therefore arc AC = arc BD."],
     "note": "Always remember: parallel chords cut off equal arcs."},
    {"problem": "Two circles intersect at A and B. Prove line joining centres is perpendicular to AB.",
     "steps": ["Let centres be P and Q.", "PA = PB (radii).", "QA = QB (radii).", "Both P and Q lie on perpendicular bisector of AB.", "Therefore PQ perpendicular to AB."],
     "note": "Always remember: perpendicularity via perpendicular bisector."},
    {"problem": "Triangle ABC right-angled at C, altitude CD to AB. Prove AD x DB = CD^2.",
     "steps": ["Angle ACB = 90.", "Altitude to hypotenuse creates three similar triangles.", "Triangle ACD similar to triangle CBD.", "AD/CD = CD/DB.", "AD x DB = CD^2."],
     "note": "Always remember: altitude-to-hypotenuse theorem."},
    {"problem": "ABCD is a parallelogram inscribed in circle O. Prove ABCD is a rectangle.",
     "steps": ["Cyclic parallelogram: opposite angles sum to 180.", "Parallelogram: opposite angles are equal.", "Each opposite angle is 90.", "Therefore rectangle."],
     "note": "Always remember: cyclic parallelogram is a rectangle."},
    {"problem": "Two tangents from P touch circle O at A and B. Prove PA = PB.",
     "steps": ["Draw OA, OB (radii).", "OA perpendicular PA; OB perpendicular PB.", "Right triangles OAP and OBP.", "OA = OB (radii), OP common.", "Congruent (RHS).", "PA = PB."],
     "note": "Always remember: tangents from a common point are equal."},
    {"problem": "Chords AB, CD intersect at P inside circle O. Prove AP x PB = CP x PD.",
     "steps": ["Draw chords AC, BD.", "Triangle APC similar to triangle DPB.", "AP/DP = CP/PB.", "AP x PB = CP x PD."],
     "note": "Always remember: intersecting chords theorem."},
    {"problem": "Prove angle at centre = 2x angle at circumference.",
     "steps": ["Draw chord AB, centre O, point P on circle.", "Draw PO and produce to Q.", "Angle AOQ = exterior angle of triangle AOP.", "OA = OP, so isosceles. Angle OAP = angle OPA.", "Angle AOQ = 2 x angle OPA.", "Similarly angle BOQ = 2 x angle OPB.", "Add: angle AOB = 2 x angle APB."],
     "note": "Always remember: central angle theorem. State construction first."},
    {"problem": "Triangle ABC with AB = AC, D midpoint of BC. Prove AD perpendicular to BC.",
     "steps": ["AB = AC, so triangle isosceles.", "D midpoint, so BD = DC.", "AD common.", "Triangles ABD, ACD congruent (SSS).", "Angle ADB = angle ADC.", "Supplementary, so each is 90.", "AD perpendicular to BC."],
     "note": "Always remember: perpendicularity via congruent triangles."},
    {"problem": "ABCD is cyclic quad, AB extended to E. Prove angle CBE = angle ADC.",
     "steps": ["Cyclic: angle ABC + angle ADC = 180.", "Straight line: angle ABC + angle CBE = 180.", "Therefore angle CBE = angle ADC."],
     "note": "Always remember: exterior angle of cyclic quad = opposite interior angle."},
    {"problem": "In circle O, PA tangent and PB secant through C and B. Prove PA^2 = PC x PB.",
     "steps": ["Draw chords AC and AB.", "Angle PCA = angle PAB (tan-chord theorem).", "Triangle PCA similar to triangle PAB (shared angle P).", "PA/PB = PC/PA.", "PA^2 = PC x PB."],
     "note": "Always remember: tangent-secant theorem."},
]

'''

# Append at end
src = src.rstrip() + "\n" + NEW_DICT

# Patch generate_all — add a merge step for EUCLID_PROOFS
old_ga = '''    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            if tid in pool and pool[tid]:
                existing = {a.get("problem", "") for a in pool[tid]}
                extra = [e for e in entries if e.get("problem", "") not in existing]
                pool[tid] = list(pool[tid]) + extra
            else:
                pool[tid] = list(entries)
            if verbose:
                print(f"  {tid}: {len(pool[tid])} total ({len(entries)} extra merged)")
    except NameError:
        pass'''

new_ga = '''    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            if tid in pool and pool[tid]:
                existing = {a.get("problem", "") for a in pool[tid]}
                extra = [e for e in entries if e.get("problem", "") not in existing]
                pool[tid] = list(pool[tid]) + extra
            else:
                pool[tid] = list(entries)
            if verbose:
                print(f"  {tid}: {len(pool[tid])} total ({len(entries)} extra merged)")
    except NameError:
        pass

    # Merge EUCLID_PROOFS into euclidean_written
    try:
        existing = {a.get("problem", "") for a in pool.get("euclidean_written", [])}
        extra = [e for e in EUCLID_PROOFS if e.get("problem", "") not in existing]
        pool["euclidean_written"] = list(pool.get("euclidean_written", [])) + extra
        if verbose:
            print(f"  euclidean_written: {len(pool['euclidean_written'])} total (incl. {len(extra)} proofs)")
    except NameError:
        pass'''

if old_ga in src:
    src = src.replace(old_ga, new_ga, 1)
    print("Patched generate_all to merge EUCLID_PROOFS")
else:
    print("WARN: generate_all anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR line", e.lineno, ":", e.msg)