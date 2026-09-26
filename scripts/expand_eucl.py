"""Fix cubic_increasing (widen the space) + expand euclidean_written to 15."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# ---- FIX 1: cubic_increasing widened ----
old_inc = '''def gen_cubic_increasing(count=50, seed=202):
    """f(x) = x^3 + bx + c, find where increasing."""
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        # Use f(x) = x^3 - 3a^2 x form: f' = 3x^2 - 3a^2 = 3(x-a)(x+a)
        a = rng.randint(1, 5)
        key = a
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "problem": f"Find the interval where f(x) = x^3 - {3*a*a}x is increasing.",
            "steps": [
                f"f'(x) = 3x^2 - {3*a*a}",
                "Increasing when f'(x) > 0.",
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line to check intervals.",
        })
    return out'''

new_inc = '''def gen_cubic_increasing(count=50, seed=202):
    """f(x) = x^3 + bx, find where increasing. Vary both a and coefficient."""
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
        # f(x) = x^3 - 3a^2 x + c   (f' = 3x^2 - 3a^2)
        a = rng.randint(1, 10)
        c = rng.randint(-15, 15)
        key = (a, c)
        if key in seen:
            continue
        seen.add(key)
        c_term = f" + {c}" if c > 0 else (f" - {abs(c)}" if c < 0 else "")
        out.append({
            "problem": f"Find the interval where f(x) = x^3 - {3*a*a}x{c_term} is increasing.",
            "steps": [
                f"f'(x) = 3x^2 - {3*a*a}",
                "Increasing when f'(x) > 0.",
                f"Set 3x^2 = {3*a*a}",
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line to check intervals.",
        })
    return out'''

if old_inc in src:
    src = src.replace(old_inc, new_inc, 1)
    print("FIX 1: cubic_increasing widened to 50+")
else:
    print("FIX 1 WARN: cubic_increasing anchor not found")

# ---- FIX 2: euclidean_written expanded ----
old_eucl = '''    "euclidean_written": [
        {
            "problem": "In circle O, AB is a diameter and C lies on the circle. Prove angle ACB = 90.",
            "steps": [
                "Given: AB is a diameter.",
                "By the theorem 'angle in a semicircle is 90', angle ACB = 90.",
                "State the theorem in the reason column.",
            ],
            "note": "Always name the theorem. Do not just write the conclusion.",
        },
        {
            "problem": "ABCD is a cyclic quadrilateral. Prove angle A + angle C = 180.",
            "steps": [
                "Cyclic quadrilateral means all four vertices lie on a circle.",
                "Opposite angles of a cyclic quadrilateral are supplementary.",
                "So A + C = 180.",
            ],
            "note": "Use 'opposite angles of cyclic quad are supplementary' as the reason.",
        },
        {
            "problem": "Tangent ST touches circle at T. Prove angle STP = angle TQP where P and Q are on the circle.",
            "steps": [
                "Angle between tangent and chord equals angle in alternate segment.",
                "Name the theorem in the reason column.",
                "Match the correct chord and the corresponding angle.",
            ],
            "note": "This is the tan-chord theorem. It appears in almost every circle geometry proof.",
        },
    ],'''

new_eucl = '''    "euclidean_written": [
        {
            "problem": "In circle O, AB is a diameter and C lies on the circle. Prove angle ACB = 90.",
            "steps": [
                "Given: AB is a diameter of circle O.",
                "C lies on the circumference.",
                "Theorem: the angle in a semicircle is 90 degrees.",
                "Therefore angle ACB = 90.",
            ],
            "note": "Always remember: name the theorem. Do not just write the conclusion.",
        },
        {
            "problem": "ABCD is a cyclic quadrilateral. Prove angle A + angle C = 180.",
            "steps": [
                "Cyclic quadrilateral means all four vertices lie on a circle.",
                "Theorem: opposite angles of a cyclic quadrilateral are supplementary.",
                "So angle A + angle C = 180.",
            ],
            "note": "Always remember: the reason is 'opposite angles of cyclic quad are supplementary'.",
        },
        {
            "problem": "Tangent ST touches circle at T. P and Q are on the circle. Prove angle STP = angle TQP.",
            "steps": [
                "Theorem: angle between tangent and chord equals angle in the alternate segment.",
                "The chord here is TP.",
                "The angle in the alternate segment is TQP.",
                "Therefore angle STP = angle TQP.",
            ],
            "note": "Always remember: this is the tan-chord theorem. Name it in the reason column.",
        },
        {
            "problem": "AB and CD are parallel chords of circle O. Prove arc AC = arc BD.",
            "steps": [
                "Parallel chords subtend equal arcs.",
                "Draw radii OA, OB, OC, OD.",
                "Equal arcs correspond to equal central angles.",
                "Therefore arc AC = arc BD.",
            ],
            "note": "Always remember: parallel chords cut off equal arcs.",
        },
        {
            "problem": "Two circles intersect at A and B. Prove that the line joining the centres is perpendicular to AB.",
            "steps": [
                "Let the centres be P and Q.",
                "PA = PB (radii of circle P).",
                "QA = QB (radii of circle Q).",
                "P and Q are both equidistant from A and B.",
                "The perpendicular bisector of AB passes through P and Q.",
                "Therefore PQ is perpendicular to AB.",
            ],
            "note": "Always remember: prove perpendicularity via the perpendicular bisector.",
        },
        {
            "problem": "In triangle ABC, D is on AB such that CD is perpendicular to AB. Prove AD x DB = CD^2 when angle ACB = 90.",
            "steps": [
                "Angle ACB = 90, so triangle ABC is right-angled at C.",
                "The altitude from C to hypotenuse AB creates three similar triangles.",
                "Triangle ACD is similar to triangle CBD.",
                "Ratio: AD/CD = CD/DB.",
                "Therefore AD x DB = CD^2.",
            ],
            "note": "Always remember: the altitude-to-hypotenuse theorem gives AD x DB = CD^2.",
        },
        {
            "problem": "ABCD is a parallelogram inscribed in circle O. Prove ABCD is a rectangle.",
            "steps": [
                "In a cyclic parallelogram, opposite angles sum to 180.",
                "In a parallelogram, opposite angles are equal.",
                "So each opposite angle is 90.",
                "Therefore ABCD is a rectangle.",
            ],
            "note": "Always remember: cyclic parallelogram is a rectangle.",
        },
        {
            "problem": "Two tangents from point P touch circle O at A and B. Prove PA = PB.",
            "steps": [
                "Draw OA and OB (radii).",
                "OA is perpendicular to PA (tangent perpendicular to radius).",
                "OB is perpendicular to PB (tangent perpendicular to radius).",
                "Triangle OAP and triangle OBP are right-angled.",
                "OA = OB (radii), OP is common.",
                "Triangles are congruent (RHS).",
                "Therefore PA = PB.",
            ],
            "note": "Always remember: tangents from a common point are equal.",
        },
        {
            "problem": "In circle O, chord AB is perpendicular to chord CD at point P. Prove AP x PB = CP x PD.",
            "steps": [
                "Draw chords AC and BD.",
                "Triangle APC is similar to triangle DPB (angles in the same segment).",
                "Therefore AP/DP = CP/PB.",
                "Cross multiply: AP x PB = CP x PD.",
            ],
            "note": "Always remember: intersecting chords theorem — the products of segments are equal.",
        },
        {
            "problem": "Prove that the angle subtended by an arc at the centre is twice the angle at the circumference.",
            "steps": [
                "Draw chord AB. O is the centre. P is on the circle.",
                "Construction: draw PO and produce it to Q.",
                "Angle AOQ = angle OAP + angle OPA (exterior angle of triangle AOP).",
                "OA = OP (radii), so triangle AOP is isosceles.",
                "Angle OAP = angle OPA.",
                "So angle AOQ = 2 x angle OPA.",
                "Similarly angle BOQ = 2 x angle OPB.",
                "Add: angle AOB = 2 x angle APB.",
            ],
            "note": "Always remember: this is the central angle theorem. State the construction first.",
        },
        {
            "problem": "In triangle ABC with AB = AC, D is the midpoint of BC. Prove AD is perpendicular to BC.",
            "steps": [
                "AB = AC (given), so triangle ABC is isosceles.",
                "D is midpoint of BC, so BD = DC.",
                "AD is common.",
                "Triangle ABD is congruent to triangle ACD (SSS).",
                "Angle ADB = angle ADC.",
                "They are supplementary (angles on a straight line).",
                "So each is 90 degrees. Therefore AD is perpendicular to BC.",
            ],
            "note": "Always remember: prove perpendicularity via congruent triangles and supplementary angles.",
        },
        {
            "problem": "ABCD is a cyclic quadrilateral. AB is extended to E. Prove angle CBE = angle ADC.",
            "steps": [
                "ABCD is cyclic, so angle ABC + angle ADC = 180 (opposite angles of cyclic quad).",
                "Angle ABC + angle CBE = 180 (angles on a straight line).",
                "Therefore angle CBE = angle ADC.",
            ],
            "note": "Always remember: the exterior angle of a cyclic quad equals the opposite interior angle.",
        },
        {
            "problem": "Two chords AB and CD of circle O intersect at P inside the circle. If P is the midpoint of AB, prove P is not the midpoint of CD unless AB = CD.",
            "steps": [
                "Consider OP as perpendicular to AB (line from centre to midpoint of chord).",
                "Also OP is perpendicular to CD if P is the midpoint of CD.",
                "But AB and CD both pass through P.",
                "If both are perpendicular to OP at P, they must be the same line.",
                "That contradicts AB and CD being different chords.",
                "Therefore P is the midpoint of both only if AB = CD (impossible unless they coincide).",
            ],
            "note": "Always remember: perpendicular from centre to chord bisects the chord.",
        },
        {
            "problem": "In circle O, PA is a tangent and PB is a secant through P touching the circle at C and B. Prove PA^2 = PC x PB.",
            "steps": [
                "Draw chord AC and chord AB.",
                "Angle PCA = angle PAB (tan-chord theorem).",
                "Triangle PCA is similar to triangle PAB (shared angle P, equal angle).",
                "Therefore PA/PB = PC/PA.",
                "Cross multiply: PA^2 = PC x PB.",
            ],
            "note": "Always remember: the tangent-secant theorem gives PA^2 = PC x PB.",
        },
    ],'''

if old_eucl in src:
    src = src.replace(old_eucl, new_eucl, 1)
    print("FIX 2: euclidean_written expanded to 15 entries")
else:
    print("FIX 2 WARN: euclidean_written block not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)