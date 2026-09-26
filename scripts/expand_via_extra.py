"""Append 40 new hand-authored entries via EXTRA_WRITTEN_ANALOGUES."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

if "EXTRA_WRITTEN_ANALOGUES" in src:
    # Already exists — check if our new keys are there
    if "TRIG_WRITTEN_PLUS" in src:
        print("Already applied")
        raise SystemExit(0)
    # Will need to inject into existing dict — more complex
    print("EXTRA_WRITTEN_ANALOGUES already exists but our keys are missing")
    print("Aborting to avoid overwrite")
    raise SystemExit(1)

NEW_BLOCK = '''

EXTRA_WRITTEN_ANALOGUES = {
    "trig_written": [
        {
            "problem": "Prove that cos 2x = 1 - 2 sin^2 x.",
            "steps": [
                "cos 2x = cos(x + x) = cos x cos x - sin x sin x.",
                "= cos^2 x - sin^2 x.",
                "Replace cos^2 x with 1 - sin^2 x.",
                "= 1 - 2 sin^2 x.",
            ],
            "note": "Always remember: cos 2x has three forms. Choose the one that fits.",
        },
        {
            "problem": "Prove that sin^2 x + cos^2 x = 1.",
            "steps": [
                "Consider a right triangle with hypotenuse r and legs y, x.",
                "sin theta = y/r, cos theta = x/r.",
                "sin^2 + cos^2 = (y^2 + x^2)/r^2 = r^2/r^2 = 1.",
            ],
            "note": "Always remember: this is the Pythagorean identity.",
        },
        {
            "problem": "Prove that sin(A+B) + sin(A-B) = 2 sin A cos B.",
            "steps": [
                "sin(A+B) = sin A cos B + cos A sin B.",
                "sin(A-B) = sin A cos B - cos A sin B.",
                "Add: 2 sin A cos B.",
            ],
            "note": "Always remember: expand both, then add. Opposite terms cancel.",
        },
        {
            "problem": "Prove that sin(A+B) - sin(A-B) = 2 cos A sin B.",
            "steps": [
                "sin(A+B) = sin A cos B + cos A sin B.",
                "sin(A-B) = sin A cos B - cos A sin B.",
                "Subtract: 2 cos A sin B.",
            ],
            "note": "Always remember: same expansion, subtract instead of add.",
        },
        {
            "problem": "Prove that cos(A+B) + cos(A-B) = 2 cos A cos B.",
            "steps": [
                "cos(A+B) = cos A cos B - sin A sin B.",
                "cos(A-B) = cos A cos B + sin A sin B.",
                "Add: 2 cos A cos B.",
            ],
            "note": "Always remember: cos of a sum minus sin of a product.",
        },
        {
            "problem": "Prove that 1 + tan^2 x = sec^2 x.",
            "steps": [
                "Divide sin^2 x + cos^2 x = 1 by cos^2 x.",
                "sin^2 / cos^2 + cos^2 / cos^2 = 1 / cos^2.",
                "tan^2 x + 1 = sec^2 x.",
            ],
            "note": "Always remember: divide the Pythagorean identity by cos^2.",
        },
        {
            "problem": "Prove that 1 + cot^2 x = cosec^2 x.",
            "steps": [
                "Divide sin^2 x + cos^2 x = 1 by sin^2 x.",
                "1 + cot^2 x = cosec^2 x.",
            ],
            "note": "Always remember: divide by sin^2 to get the third Pythagorean identity.",
        },
        {
            "problem": "Prove that cos 2x = 2 cos^2 x - 1.",
            "steps": [
                "cos 2x = cos^2 x - sin^2 x.",
                "Replace sin^2 x with 1 - cos^2 x.",
                "= cos^2 x - (1 - cos^2 x) = 2 cos^2 x - 1.",
            ],
            "note": "Always remember: this is the cos-only form of cos 2x.",
        },
        {
            "problem": "Prove that sin 2x = 2 tan x / (1 + tan^2 x).",
            "steps": [
                "RHS: 2 tan x / (1 + tan^2 x).",
                "Substitute tan x = sin x / cos x and 1 + tan^2 x = sec^2 x.",
                "= 2 (sin x / cos x) / sec^2 x.",
                "= 2 sin x / cos x x cos^2 x.",
                "= 2 sin x cos x = sin 2x.",
            ],
            "note": "Always remember: converting to sin and cos usually unlocks the proof.",
        },
    ],

    "trig_graph_written": [
        {
            "problem": "Sketch y = sin 2x for x in [0; 360]. State the period.",
            "steps": [
                "Period = 360 / 2 = 180.",
                "Amplitude = 1.",
                "Two full cycles between 0 and 360.",
                "Key points: (0; 0), (45; 1), (90; 0), (135; -1), (180; 0), repeat.",
            ],
            "note": "Always remember: period = 360 / coefficient of x.",
        },
        {
            "problem": "Sketch y = 3 sin x for x in [0; 360]. State amplitude and range.",
            "steps": [
                "Amplitude = 3.",
                "Range = [-3; 3].",
                "Period = 360.",
                "Key points: (0; 0), (90; 3), (180; 0), (270; -3), (360; 0).",
            ],
            "note": "Always remember: the number in front of sin is the amplitude.",
        },
        {
            "problem": "Sketch y = cos(x - 90). Describe the transformation.",
            "steps": [
                "Amplitude 1, period 360.",
                "cos x shifted 90 to the right.",
                "cos(x - 90) = sin x.",
            ],
            "note": "Always remember: shifting cos by 90 gives sin.",
        },
        {
            "problem": "Sketch y = tan x for x in [0; 360]. State asymptotes and period.",
            "steps": [
                "Period = 180.",
                "Asymptotes at x = 90 and x = 270.",
                "tan 0 = 0, tan 45 = 1, tan 135 = -1, tan 180 = 0.",
            ],
            "note": "Always remember: tan has asymptotes where cos = 0.",
        },
        {
            "problem": "Sketch y = -cos x for x in [0; 360].",
            "steps": [
                "Reflection of cos x in the x-axis.",
                "Key points: (0; -1), (90; 0), (180; 1), (270; 0), (360; -1).",
            ],
            "note": "Always remember: negative in front reflects vertically.",
        },
        {
            "problem": "Sketch y = sin x + 2 for x in [0; 360].",
            "steps": [
                "Amplitude 1, period 360.",
                "Shifted up by 2.",
                "Range = [1; 3].",
                "Key points: (0; 2), (90; 3), (180; 2), (270; 1), (360; 2).",
            ],
            "note": "Always remember: adding a constant shifts vertically.",
        },
        {
            "problem": "Sketch y = 2 cos 2x for x in [0; 360].",
            "steps": [
                "Amplitude 2, period 180.",
                "Two cycles between 0 and 360.",
                "Key points: (0; 2), (45; 0), (90; -2), (135; 0), (180; 2), repeat.",
            ],
            "note": "Always remember: amplitude and period change independently.",
        },
        {
            "problem": "Sketch y = sin(x + 30) for x in [0; 360].",
            "steps": [
                "Amplitude 1, period 360.",
                "Shifted 30 to the left.",
                "Key points shift by 30.",
            ],
            "note": "Always remember: plus inside bracket shifts left, minus shifts right.",
        },
        {
            "problem": "Sketch y = -2 sin x for x in [0; 360].",
            "steps": [
                "Amplitude 2, range [-2; 2].",
                "Reflected in x-axis.",
                "Key points: (0; 0), (90; -2), (180; 0), (270; 2), (360; 0).",
            ],
            "note": "Always remember: the reflection flips peaks and troughs.",
        },
    ],

    "trig_3d_written": [
        {
            "problem": "In triangle ABC, AB = 8, AC = 6, angle A = 60. Find BC.",
            "steps": [
                "Cosine rule: BC^2 = 8^2 + 6^2 - 2(8)(6)cos 60.",
                "= 64 + 36 - 48 = 52.",
                "BC = sqrt(52).",
            ],
            "note": "Always remember: cosine rule for two sides and the included angle.",
        },
        {
            "problem": "A vertical pole 10 m tall casts a shadow 8 m long. Find the angle of elevation.",
            "steps": [
                "Right triangle: vertical 10, horizontal 8.",
                "tan(theta) = 10/8 = 1.25.",
                "theta = 51.34 degrees.",
            ],
            "note": "Always remember: draw the right triangle first.",
        },
        {
            "problem": "From 50 m away, the angle of elevation to a tower top is 35. Find the height.",
            "steps": [
                "tan 35 = h / 50.",
                "h = 50 tan 35 = 35.01 m.",
            ],
            "note": "Always remember: tower + ground + sight line form a right triangle.",
        },
        {
            "problem": "Two observers 100 m apart see a balloon. Angles of elevation 30 and 45. Find the height.",
            "steps": [
                "Let h = height, x = distance to 45-degree observer.",
                "tan 45 = h/x gives h = x.",
                "tan 30 = h/(100-x).",
                "x = (100-x)/sqrt(3).",
                "x(1 + sqrt(3)) = 100.",
                "x = 36.6, h = 36.6 m.",
            ],
            "note": "Always remember: two triangles, write both tan equations.",
        },
        {
            "problem": "In triangle ABC, AB = 7, BC = 9, angle B = 120. Find AC.",
            "steps": [
                "Cosine rule: AC^2 = 49 + 81 - 2(7)(9)cos 120.",
                "= 130 + 63 = 193.",
                "AC = 13.89.",
            ],
            "note": "Always remember: cos 120 = -0.5, so the third term becomes positive.",
        },
        {
            "problem": "In triangle ABC, a = 10, b = 12, angle C = 45. Find the area.",
            "steps": [
                "Area = (1/2) ab sin C.",
                "= (1/2)(10)(12) sin 45 = 42.43.",
            ],
            "note": "Always remember: (1/2)ab sin C for area with included angle.",
        },
        {
            "problem": "A ship sails 20 km on bearing 060 then 15 km on bearing 150. Distance from start?",
            "steps": [
                "Angle between the legs = 90 degrees.",
                "d^2 = 20^2 + 15^2 = 625.",
                "d = 25 km.",
            ],
            "note": "Always remember: bearings are measured clockwise from north.",
        },
        {
            "problem": "A ladder 8 m long makes angle 65 with the ground. Height up the wall?",
            "steps": [
                "sin 65 = h / 8.",
                "h = 8 sin 65 = 7.25 m.",
            ],
            "note": "Always remember: the ladder is the hypotenuse.",
        },
        {
            "problem": "Buildings 40 m apart. From top of the shorter (12 m), angle of elevation to the taller is 20. Find the taller height.",
            "steps": [
                "Difference = 40 tan 20 = 14.56.",
                "Taller = 12 + 14.56 = 26.56 m.",
            ],
            "note": "Always remember: the difference in heights is the opposite side.",
        },
        {
            "problem": "In triangle ABC, AB = 6, AC = 5, BC = 7. Find angle A.",
            "steps": [
                "cos A = (36 + 25 - 49) / (2 x 6 x 5) = 12/60 = 0.2.",
                "A = 78.46 degrees.",
            ],
            "note": "Always remember: cosine rule rearranged for an angle.",
        },
    ],

    "stats_written": [
        {
            "problem": "A box plot has Q1 = 20, median = 22, Q3 = 30. Comment on the distribution.",
            "steps": [
                "Median is closer to Q1 than Q3.",
                "The box is wider on the right side.",
                "Right-skewed distribution.",
            ],
            "note": "Always remember: median closer to Q1 means skewed right.",
        },
        {
            "problem": "Is the value 95 an outlier given Q1 = 20, Q3 = 40?",
            "steps": [
                "IQR = 20.",
                "Upper fence = 40 + 1.5 x 20 = 70.",
                "95 > 70, so 95 is an outlier.",
            ],
            "note": "Always remember: state the fences before deciding.",
        },
        {
            "problem": "Describe the correlation if r = -0.85.",
            "steps": [
                "r close to -1.",
                "Negative sign means opposite directions.",
                "Answer: strong negative correlation.",
            ],
            "note": "Always remember: comment on strength AND direction.",
        },
        {
            "problem": "Is the value 3 an outlier given Q1 = 10, Q3 = 25?",
            "steps": [
                "IQR = 15.",
                "Lower fence = 10 - 22.5 = -12.5.",
                "3 > -12.5, so 3 is NOT an outlier.",
            ],
            "note": "Always remember: check both fences.",
        },
        {
            "problem": "Histogram heavily right-side with long left tail. Describe the distribution.",
            "steps": [
                "Long tail on the left = left-skewed.",
                "Most data at higher values.",
                "Answer: negatively skewed.",
            ],
            "note": "Always remember: the tail points in the direction of the skew.",
        },
        {
            "problem": "Compare SD = 2 vs SD = 8. Comment.",
            "steps": [
                "Larger SD means more spread.",
                "SD = 8 data is more spread than SD = 2 data.",
            ],
            "note": "Always remember: SD measures spread, not location.",
        },
        {
            "problem": "Dataset has x-bar = 50, sigma = 5. Is 62 within one SD?",
            "steps": [
                "Range: 45 to 55.",
                "62 > 55.",
                "No, 62 is not within one SD.",
            ],
            "note": "Always remember: state x-bar +/- sigma before deciding.",
        },
        {
            "problem": "Student 1: 80% (mean 70, SD 10). Student 2: 60% (mean 40, SD 15). Who did relatively better?",
            "steps": [
                "Student 1: (80-70)/10 = +1 SD.",
                "Student 2: (60-40)/15 = +1.33 SD.",
                "Student 2 is relatively further above the mean.",
            ],
            "note": "Always remember: compare z-scores, not raw marks.",
        },
        {
            "problem": "Scatter plot widely scattered with no clear pattern. Comment on r.",
            "steps": [
                "No pattern means weak or zero correlation.",
                "r close to 0.",
            ],
            "note": "Always remember: r close to 0 means weak correlation.",
        },
        {
            "problem": "Histogram of exam marks is symmetric. Comment.",
            "steps": [
                "Symmetric means the two halves mirror each other.",
                "Mean is close to the median.",
            ],
            "note": "Always remember: symmetric data has mean close to median.",
        },
    ],
}
'''

# Append before TEMPLATES
anchor = "TEMPLATES = {"
if anchor in src:
    src = src.replace(anchor, NEW_BLOCK + "\n\n" + anchor, 1)
    print("Appended EXTRA_WRITTEN_ANALOGUES with 40 new entries")
else:
    print("WARN: TEMPLATES anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)