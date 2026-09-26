"""Expand remaining hand-authored templates to 10+ each."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# ============================================================
# EXPAND — trig_written
# ============================================================
old = '''    "trig_written": [
        {
            "problem": "Prove that sin(180 - x) = sin x.",
            "steps": [
                "sin(180 - x) is in the second quadrant.",
                "In Q2, sine is positive.",
                "So sin(180 - x) = sin x.",
            ],
            "note": "Always remember: use the CAST diagram to determine the sign. Reduce the angle first.",
        },
        {
            "problem": "Prove that sin 2x = 2 sin x cos x.",
            "steps": [
                "Use the compound angle formula: sin(A + B) = sin A cos B + cos A sin B.",
                "Let A = B = x.",
                "Then sin(2x) = sin x cos x + cos x sin x = 2 sin x cos x.",
            ],
            "note": "Always remember: double-angle formulas are derived from compound angle formulas.",
        },
    ],'''

new = '''    "trig_written": [
        {
            "problem": "Prove that sin(180 - x) = sin x.",
            "steps": [
                "sin(180 - x) is in the second quadrant.",
                "In Q2, sine is positive.",
                "So sin(180 - x) = sin x.",
            ],
            "note": "Always remember: use the CAST diagram. Reduce the angle first.",
        },
        {
            "problem": "Prove that sin 2x = 2 sin x cos x.",
            "steps": [
                "Use the compound formula: sin(A + B) = sin A cos B + cos A sin B.",
                "Let A = B = x.",
                "Then sin(2x) = sin x cos x + cos x sin x = 2 sin x cos x.",
            ],
            "note": "Always remember: double-angle formulas come from compound angle formulas.",
        },
        {
            "problem": "Prove that cos 2x = 1 - 2 sin^2 x.",
            "steps": [
                "cos 2x = cos(x + x) = cos x cos x - sin x sin x.",
                "= cos^2 x - sin^2 x.",
                "Replace cos^2 x with 1 - sin^2 x.",
                "= (1 - sin^2 x) - sin^2 x = 1 - 2 sin^2 x.",
            ],
            "note": "Always remember: cos 2x has three forms. Choose the one that fits the question.",
        },
        {
            "problem": "Prove that (sin x)/(cos x) = tan x.",
            "steps": [
                "This is the definition of tan x.",
                "tan x = sin x / cos x by definition.",
            ],
            "note": "Always remember: tan x = sin x / cos x. This is not a theorem to prove, it is the definition.",
        },
        {
            "problem": "Prove that sin^2 x + cos^2 x = 1.",
            "steps": [
                "Consider a right-angled triangle with hypotenuse r and legs x, y.",
                "sin theta = y/r, cos theta = x/r.",
                "sin^2 + cos^2 = (y^2 + x^2) / r^2 = r^2 / r^2 = 1.",
            ],
            "note": "Always remember: this is the Pythagorean identity. It follows from Pythagoras' theorem.",
        },
        {
            "problem": "Prove that sin(A + B) + sin(A - B) = 2 sin A cos B.",
            "steps": [
                "sin(A + B) = sin A cos B + cos A sin B.",
                "sin(A - B) = sin A cos B - cos A sin B.",
                "Add the two: 2 sin A cos B.",
            ],
            "note": "Always remember: expand both compound angles, then add. The opposite terms cancel.",
        },
        {
            "problem": "Prove that sin(A + B) - sin(A - B) = 2 cos A sin B.",
            "steps": [
                "sin(A + B) = sin A cos B + cos A sin B.",
                "sin(A - B) = sin A cos B - cos A sin B.",
                "Subtract: 2 cos A sin B.",
            ],
            "note": "Always remember: the same expansion, but subtract instead of add.",
        },
        {
            "problem": "Prove that cos(A + B) + cos(A - B) = 2 cos A cos B.",
            "steps": [
                "cos(A + B) = cos A cos B - sin A sin B.",
                "cos(A - B) = cos A cos B + sin A sin B.",
                "Add: 2 cos A cos B.",
            ],
            "note": "Always remember: cos of a sum minus sin of a product.",
        },
        {
            "problem": "Prove that cos 2x = cos^2 x - sin^2 x.",
            "steps": [
                "cos 2x = cos(x + x).",
                "cos(x + x) = cos x cos x - sin x sin x.",
                "= cos^2 x - sin^2 x.",
            ],
            "note": "Always remember: this is the base form of cos 2x. The other two come from Pythagorean substitution.",
        },
        {
            "problem": "Prove that 1 + tan^2 x = sec^2 x.",
            "steps": [
                "Divide sin^2 x + cos^2 x = 1 by cos^2 x.",
                "sin^2 / cos^2 + cos^2 / cos^2 = 1 / cos^2.",
                "tan^2 x + 1 = sec^2 x.",
            ],
            "note": "Always remember: divide the Pythagorean identity by cos^2 or sin^2 to get the other two.",
        },
        {
            "problem": "Prove that 1 + cot^2 x = cosec^2 x.",
            "steps": [
                "Divide sin^2 x + cos^2 x = 1 by sin^2 x.",
                "sin^2 / sin^2 + cos^2 / sin^2 = 1 / sin^2.",
                "1 + cot^2 x = cosec^2 x.",
            ],
            "note": "Always remember: three Pythagorean identities come from dividing by 1, cos^2, or sin^2.",
        },
    ],'''

if old in src:
    src = src.replace(old, new, 1)
    print("Expanded trig_written to 11")
else:
    print("WARN: trig_written block not found")

# ============================================================
# EXPAND — trig_graph_written
# ============================================================
old2 = '''    "trig_graph_written": [
        {
            "problem": "Sketch y = sin x for x in [0; 360]. State the amplitude and period.",
            "steps": [
                "Amplitude = 1 (coefficient of sin).",
                "Period = 360 (standard for sin x).",
                "Key points: (0; 0), (90; 1), (180; 0), (270; -1), (360; 0).",
            ],
            "note": "Always remember: state amplitude and period before drawing. They are often marks on their own.",
        },
        {
            "problem": "Sketch y = 2 cos x. State the range and period.",
            "steps": [
                "Amplitude = 2, so range is [-2; 2].",
                "Period = 360.",
                "Key points: (0; 2), (90; 0), (180; -2), (270; 0), (360; 2).",
            ],
            "note": "Always remember: amplitude is the multiplier. Range follows directly from amplitude.",
        },
    ],'''

new2 = '''    "trig_graph_written": [
        {
            "problem": "Sketch y = sin x for x in [0; 360]. State the amplitude and period.",
            "steps": [
                "Amplitude = 1.",
                "Period = 360.",
                "Key points: (0; 0), (90; 1), (180; 0), (270; -1), (360; 0).",
            ],
            "note": "Always remember: state amplitude and period before drawing. They earn marks on their own.",
        },
        {
            "problem": "Sketch y = 2 cos x. State the range and period.",
            "steps": [
                "Amplitude = 2, range is [-2; 2].",
                "Period = 360.",
                "Key points: (0; 2), (90; 0), (180; -2), (270; 0), (360; 2).",
            ],
            "note": "Always remember: amplitude is the multiplier. Range comes from amplitude.",
        },
        {
            "problem": "Sketch y = sin 2x for x in [0; 360]. State the period.",
            "steps": [
                "Period = 360 / 2 = 180.",
                "Amplitude = 1.",
                "Two full cycles between 0 and 360.",
                "Key points: (0; 0), (45; 1), (90; 0), (135; -1), (180; 0), then repeat.",
            ],
            "note": "Always remember: period = 360 / coefficient of x. The 2 doubles the number of cycles.",
        },
        {
            "problem": "Sketch y = 3 sin x for x in [0; 360]. State the amplitude and range.",
            "steps": [
                "Amplitude = 3.",
                "Range = [-3; 3].",
                "Period = 360.",
                "Key points: (0; 0), (90; 3), (180; 0), (270; -3), (360; 0).",
            ],
            "note": "Always remember: the number in front of sin is the amplitude.",
        },
        {
            "problem": "Sketch y = cos(x - 90) for x in [0; 360]. Describe the transformation.",
            "steps": [
                "Amplitude = 1, period = 360.",
                "This is cos x shifted 90 to the right.",
                "cos(x - 90) = sin x.",
                "Sketch looks like sin x.",
            ],
            "note": "Always remember: shifting cos by 90 gives sin. This is the co-function identity.",
        },
        {
            "problem": "Sketch y = tan x for x in [0; 360]. State the asymptotes and period.",
            "steps": [
                "Period = 180.",
                "Asymptotes at x = 90 and x = 270.",
                "tan 0 = 0, tan 45 = 1, tan 135 = -1, tan 180 = 0.",
                "Curve rises to +infinity approaching 90 from below.",
            ],
            "note": "Always remember: tan has asymptotes where cos = 0. Period is 180, not 360.",
        },
        {
            "problem": "Sketch y = -cos x for x in [0; 360].",
            "steps": [
                "Reflection of cos x in the x-axis.",
                "Key points: (0; -1), (90; 0), (180; 1), (270; 0), (360; -1).",
            ],
            "note": "Always remember: negative in front reflects the graph vertically.",
        },
        {
            "problem": "Sketch y = sin x + 2 for x in [0; 360].",
            "steps": [
                "Amplitude = 1, period = 360.",
                "Shifted up by 2.",
                "Range = [1; 3].",
                "Key points: (0; 2), (90; 3), (180; 2), (270; 1), (360; 2).",
            ],
            "note": "Always remember: adding a constant shifts the graph vertically.",
        },
        {
            "problem": "Sketch y = 2 cos(2x) for x in [0; 360]. State amplitude and period.",
            "steps": [
                "Amplitude = 2.",
                "Period = 360 / 2 = 180.",
                "Two cycles between 0 and 360.",
                "Key points: (0; 2), (45; 0), (90; -2), (135; 0), (180; 2), then repeat.",
            ],
            "note": "Always remember: amplitude and period change independently.",
        },
        {
            "problem": "Sketch y = sin(x + 30) for x in [0; 360].",
            "steps": [
                "Amplitude = 1, period = 360.",
                "Shifted 30 to the left.",
                "Key points shift by 30: (-30; 0), (60; 1), (150; 0), (240; -1), (330; 0).",
            ],
            "note": "Always remember: plus inside bracket shifts left, minus shifts right.",
        },
        {
            "problem": "Sketch y = -2 sin x for x in [0; 360]. State amplitude and range.",
            "steps": [
                "Amplitude = 2, range = [-2; 2].",
                "Reflected in x-axis (negative sign).",
                "Key points: (0; 0), (90; -2), (180; 0), (270; 2), (360; 0).",
            ],
            "note": "Always remember: the reflection flips which points are peaks and which are troughs.",
        },
    ],'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Expanded trig_graph_written to 11")
else:
    print("WARN: trig_graph_written block not found")

# ============================================================
# EXPAND — trig_3d_written
# ============================================================
old3 = '''    "trig_3d_written": [
        {
            "problem": "In triangle ABC, AB = 5 cm, angle A = 30, angle B = 45. Find BC.",
            "steps": [
                "Use sine rule: BC / sin A = AB / sin C.",
                "Find angle C = 180 - 30 - 45 = 105.",
                "BC = 5 sin 30 / sin 105.",
            ],
            "note": "Always remember: name the rule. Write the formula line before substituting.",
        },
    ],'''

new3 = '''    "trig_3d_written": [
        {
            "problem": "In triangle ABC, AB = 5 cm, angle A = 30, angle B = 45. Find BC.",
            "steps": [
                "Use sine rule: BC / sin A = AB / sin C.",
                "Angle C = 180 - 30 - 45 = 105.",
                "BC = 5 sin 30 / sin 105.",
            ],
            "note": "Always remember: name the rule. Write the formula line before substituting.",
        },
        {
            "problem": "In triangle ABC, AB = 8, AC = 6, angle A = 60. Find BC.",
            "steps": [
                "Use cosine rule: BC^2 = AB^2 + AC^2 - 2(AB)(AC)cos A.",
                "= 64 + 36 - 2(8)(6)(0.5)",
                "= 100 - 48 = 52.",
                "BC = sqrt(52).",
            ],
            "note": "Always remember: cosine rule when you have two sides and the included angle.",
        },
        {
            "problem": "A vertical pole of height 10 m casts a shadow 8 m long. Find the angle of elevation of the sun.",
            "steps": [
                "Sketch: right triangle with vertical = 10, horizontal = 8.",
                "tan(theta) = 10 / 8 = 1.25.",
                "theta = arctan(1.25) = 51.34 degrees.",
            ],
            "note": "Always remember: draw the right triangle first. Angle of elevation is measured from horizontal.",
        },
        {
            "problem": "From point P on level ground, the angle of elevation to the top of a tower is 35 degrees. P is 50 m from the base. Find the tower height.",
            "steps": [
                "tan(35) = h / 50.",
                "h = 50 tan(35).",
                "h = 35.01 m.",
            ],
            "note": "Always remember: the tower, the ground, and the line of sight form a right triangle.",
        },
        {
            "problem": "Two observers 100 m apart both see a hot-air balloon directly between them. Their angles of elevation are 30 and 45. Find the balloon height.",
            "steps": [
                "Let h be the height and x be the distance to the 45-degree observer.",
                "tan 45 = h / x gives h = x.",
                "tan 30 = h / (100 - x) gives h = (100 - x)/sqrt(3).",
                "x = (100 - x)/sqrt(3).",
                "x sqrt(3) = 100 - x, so x(1 + sqrt(3)) = 100.",
                "x = 100 / (1 + sqrt(3)) = 36.6.",
                "Height h = 36.6 m.",
            ],
            "note": "Always remember: two triangles. Write both tan equations before solving.",
        },
        {
            "problem": "In triangle ABC, AB = 7, BC = 9, angle B = 120. Find AC.",
            "steps": [
                "Cosine rule: AC^2 = AB^2 + BC^2 - 2(AB)(BC)cos B.",
                "= 49 + 81 - 2(7)(9)(-0.5).",
                "= 130 + 63 = 193.",
                "AC = sqrt(193) = 13.89.",
            ],
            "note": "Always remember: cos 120 = -0.5, so the third term becomes positive.",
        },
        {
            "problem": "In triangle ABC, a = 10, b = 12, angle C = 45. Find the area.",
            "steps": [
                "Area = (1/2) ab sin C.",
                "= (1/2)(10)(12) sin 45.",
                "= 60 x 0.7071 = 42.43.",
            ],
            "note": "Always remember: area with two sides and included angle uses (1/2)ab sin C.",
        },
        {
            "problem": "A ship sails 20 km on bearing 060 then 15 km on bearing 150. How far is it from the start?",
            "steps": [
                "Sketch the two legs. The angle between them is 90 degrees.",
                "Distance^2 = 20^2 + 15^2.",
                "= 400 + 225 = 625.",
                "Distance = 25 km.",
            ],
            "note": "Always remember: bearings are measured clockwise from north. Draw north lines.",
        },
        {
            "problem": "A ladder 8 m long leans against a wall making an angle of 65 with the ground. How high up the wall does it reach?",
            "steps": [
                "sin(65) = height / 8.",
                "height = 8 sin(65).",
                "height = 7.25 m.",
            ],
            "note": "Always remember: the ladder is the hypotenuse. Opposite is the height.",
        },
        {
            "problem": "Two buildings are 40 m apart. From the top of the shorter one (12 m tall), the angle of elevation to the top of the taller one is 20. Find the taller building height.",
            "steps": [
                "Difference in height = 40 tan(20).",
                "= 40 x 0.3640 = 14.56.",
                "Taller building = 12 + 14.56 = 26.56 m.",
            ],
            "note": "Always remember: the difference in heights is the opposite side of the elevation triangle.",
        },
        {
            "problem": "In triangle ABC, AB = 6, AC = 5, BC = 7. Find angle A.",
            "steps": [
                "Cosine rule: cos A = (AB^2 + AC^2 - BC^2) / (2 x AB x AC).",
                "= (36 + 25 - 49) / (2 x 6 x 5).",
                "= 12 / 60 = 0.2.",
                "A = arccos(0.2) = 78.46 degrees.",
            ],
            "note": "Always remember: cosine rule rearranged solves for the angle when all three sides are known.",
        },
    ],'''

if old3 in src:
    src = src.replace(old3, new3, 1)
    print("Expanded trig_3d_written to 11")
else:
    print("WARN: trig_3d_written block not found")

# ============================================================
# EXPAND — stats_written
# ============================================================
old4 = '''    "stats_written": [
        {
            "problem": "A box plot has minimum = 5, Q1 = 12, median = 20, Q3 = 28, maximum = 40. Describe the shape.",
            "steps": [
                "IQR = Q3 - Q1 = 28 - 12 = 16.",
                "Median is not in the middle of Q1 and Q3, so the data is skewed.",
                "Longer upper whisker (28 to 40 = 12) than lower (5 to 12 = 7), so skewed right.",
            ],
            "note": "Always remember: compare the whisker lengths and the position of the median within the box.",
        },
    ],'''

new4 = '''    "stats_written": [
        {
            "problem": "A box plot has minimum = 5, Q1 = 12, median = 20, Q3 = 28, maximum = 40. Describe the shape.",
            "steps": [
                "IQR = Q3 - Q1 = 16.",
                "Upper whisker = 40 - 28 = 12. Lower whisker = 12 - 5 = 7.",
                "Upper whisker is longer, so the data is skewed right.",
            ],
            "note": "Always remember: compare the whisker lengths and the median position inside the box.",
        },
        {
            "problem": "A box plot has Q1 = 20, median = 22, Q3 = 30. Comment on the distribution.",
            "steps": [
                "Median is closer to Q1 than Q3.",
                "The box is wider on the right side.",
                "This suggests a right-skewed distribution.",
            ],
            "note": "Always remember: median closer to Q1 means the data is skewed to the right.",
        },
        {
            "problem": "Comment on whether the value 95 is an outlier given Q1 = 20, Q3 = 40.",
            "steps": [
                "IQR = 40 - 20 = 20.",
                "Upper fence = Q3 + 1.5 x IQR = 40 + 30 = 70.",
                "95 > 70, so 95 is an outlier.",
            ],
            "note": "Always remember: the outlier rule uses 1.5 x IQR. State the fences before deciding.",
        },
        {
            "problem": "Describe the correlation if r = -0.85.",
            "steps": [
                "r is close to -1.",
                "The negative sign means the variables move in opposite directions.",
                "The magnitude 0.85 indicates a strong correlation.",
                "Answer: strong negative correlation.",
            ],
            "note": "Always remember: comment on strength AND direction. r close to 1 = strong.",
        },
        {
            "problem": "Comment on whether the value 3 is an outlier given Q1 = 10, Q3 = 25.",
            "steps": [
                "IQR = 25 - 10 = 15.",
                "Lower fence = Q1 - 1.5 x IQR = 10 - 22.5 = -12.5.",
                "3 > -12.5, so 3 is NOT an outlier.",
            ],
            "note": "Always remember: outliers can only exist below the lower fence or above the upper fence.",
        },
        {
            "problem": "A histogram of exam marks is heavily concentrated on the right side with a long tail on the left. Describe the distribution.",
            "steps": [
                "Long tail on the left = left-skewed.",
                "Most of the data is at higher values.",
                "Answer: negatively skewed (left-skewed).",
            ],
            "note": "Always remember: the tail points in the direction of the skew.",
        },
        {
            "problem": "Comment on the standard deviation if two datasets have SD = 2 and SD = 8 respectively.",
            "steps": [
                "Larger SD means the data is more spread out from the mean.",
                "SD = 8 data is more spread than SD = 2 data.",
            ],
            "note": "Always remember: SD measures spread, not location. Higher SD = more variation.",
        },
        {
            "problem": "A dataset has x̄ = 50, σ = 5. Comment on whether 62 lies within one standard deviation of the mean.",
            "steps": [
                "One SD range: x̄ - σ to x̄ + σ = 45 to 55.",
                "62 > 55.",
                "So 62 does not lie within one standard deviation.",
            ],
            "note": "Always remember: state the interval x̄ ± σ before deciding.",
        },
        {
            "problem": "Two students compare their marks: 80% in a test with mean 70% and SD 10, versus 60% in a test with mean 40% and SD 15. Comment on who did relatively better.",
            "steps": [
                "Student 1: (80 - 70) / 10 = +1 SD above the mean.",
                "Student 2: (60 - 40) / 15 = +1.33 SD above the mean.",
                "Student 2 is relatively further above the mean.",
            ],
            "note": "Always remember: compare z-scores (how many SDs above or below the mean) to compare across different tests.",
        },
        {
            "problem": "A scatter plot shows the data points widely scattered with no clear pattern. Comment on the correlation coefficient.",
            "steps": [
                "No pattern suggests weak or zero correlation.",
                "r would be close to 0.",
            ],
            "note": "Always remember: r close to 0 = weak or no correlation. r close to ±1 = strong.",
        },
    ],'''

if old4 in src:
    src = src.replace(old4, new4, 1)
    print("Expanded stats_written to 10")
else:
    print("WARN: stats_written block not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)