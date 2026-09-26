"""Replace the empty EXTRA_WRITTEN_ANALOGUES stub with the full version."""
from pathlib import Path
import ast
import re

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# Find the existing stub and get its exact text
idx = src.find("EXTRA_WRITTEN_ANALOGUES")
if idx < 0:
    print("Not found")
    raise SystemExit(1)

# Find the full assignment (up to closing brace)
start = idx
brace = src.find("{", idx)
depth = 0
end = brace
for i in range(brace, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

old_block = src[start:end]
print("Old block:", repr(old_block))

# New content — reuse the big dict from the earlier patch
NEW = '''EXTRA_WRITTEN_ANALOGUES = {
    "trig_written": [
        {"problem": "Prove that cos 2x = 1 - 2 sin^2 x.", "steps": ["cos 2x = cos^2 x - sin^2 x.", "Replace cos^2 x with 1 - sin^2 x.", "= 1 - 2 sin^2 x."], "note": "Always remember: cos 2x has three forms."},
        {"problem": "Prove that sin^2 x + cos^2 x = 1.", "steps": ["Right triangle: sin = y/r, cos = x/r.", "sin^2 + cos^2 = (y^2 + x^2)/r^2 = 1."], "note": "Always remember: the Pythagorean identity."},
        {"problem": "Prove that sin(A+B) + sin(A-B) = 2 sin A cos B.", "steps": ["sin(A+B) = sin A cos B + cos A sin B.", "sin(A-B) = sin A cos B - cos A sin B.", "Add: 2 sin A cos B."], "note": "Always remember: expand both, add."},
        {"problem": "Prove that sin(A+B) - sin(A-B) = 2 cos A sin B.", "steps": ["sin(A+B) = sin A cos B + cos A sin B.", "sin(A-B) = sin A cos B - cos A sin B.", "Subtract: 2 cos A sin B."], "note": "Always remember: subtract instead of add."},
        {"problem": "Prove that cos(A+B) + cos(A-B) = 2 cos A cos B.", "steps": ["cos(A+B) = cos A cos B - sin A sin B.", "cos(A-B) = cos A cos B + sin A sin B.", "Add: 2 cos A cos B."], "note": "Always remember: cos of a sum minus sin of a product."},
        {"problem": "Prove that 1 + tan^2 x = sec^2 x.", "steps": ["Divide sin^2 + cos^2 = 1 by cos^2.", "tan^2 x + 1 = sec^2 x."], "note": "Always remember: divide by cos^2."},
        {"problem": "Prove that 1 + cot^2 x = cosec^2 x.", "steps": ["Divide sin^2 + cos^2 = 1 by sin^2.", "1 + cot^2 x = cosec^2 x."], "note": "Always remember: divide by sin^2."},
        {"problem": "Prove that cos 2x = 2 cos^2 x - 1.", "steps": ["cos 2x = cos^2 x - sin^2 x.", "Replace sin^2 x with 1 - cos^2 x.", "= 2 cos^2 x - 1."], "note": "Always remember: the cos-only form of cos 2x."},
        {"problem": "Prove that sin 2x = 2 tan x / (1 + tan^2 x).", "steps": ["Substitute tan x and 1 + tan^2 x = sec^2 x.", "= 2 sin x cos x = sin 2x."], "note": "Always remember: converting to sin/cos unlocks the proof."},
    ],
    "trig_graph_written": [
        {"problem": "Sketch y = sin 2x. State the period.", "steps": ["Period = 360/2 = 180.", "Amplitude = 1.", "Two cycles between 0 and 360."], "note": "Always remember: period = 360 / coefficient."},
        {"problem": "Sketch y = 3 sin x. State amplitude and range.", "steps": ["Amplitude = 3.", "Range = [-3; 3]."], "note": "Always remember: number in front is amplitude."},
        {"problem": "Sketch y = cos(x - 90). Describe the transformation.", "steps": ["Shifted 90 right.", "cos(x - 90) = sin x."], "note": "Always remember: shift cos 90 gives sin."},
        {"problem": "Sketch y = tan x. State asymptotes and period.", "steps": ["Period = 180.", "Asymptotes at 90 and 270."], "note": "Always remember: tan has asymptotes where cos = 0."},
        {"problem": "Sketch y = -cos x.", "steps": ["Reflection in x-axis.", "Key: (0; -1), (90; 0), (180; 1), (270; 0)."], "note": "Always remember: negative reflects vertically."},
        {"problem": "Sketch y = sin x + 2.", "steps": ["Shifted up by 2.", "Range = [1; 3]."], "note": "Always remember: constant shifts vertically."},
        {"problem": "Sketch y = 2 cos 2x.", "steps": ["Amplitude 2, period 180."], "note": "Always remember: amplitude and period change independently."},
        {"problem": "Sketch y = sin(x + 30).", "steps": ["Shifted 30 left."], "note": "Always remember: plus inside shifts left."},
        {"problem": "Sketch y = -2 sin x.", "steps": ["Amplitude 2, range [-2; 2].", "Reflected."], "note": "Always remember: reflection flips peaks and troughs."},
    ],
    "trig_3d_written": [
        {"problem": "Triangle ABC: AB = 8, AC = 6, angle A = 60. Find BC.", "steps": ["Cosine rule: BC^2 = 64 + 36 - 48 = 52.", "BC = sqrt(52)."], "note": "Always remember: cosine rule for two sides and included angle."},
        {"problem": "Pole 10 m casts shadow 8 m. Angle of elevation?", "steps": ["tan(theta) = 10/8 = 1.25.", "theta = 51.34."], "note": "Always remember: draw the right triangle first."},
        {"problem": "From 50 m, angle of elevation to tower top is 35. Find height.", "steps": ["tan 35 = h/50.", "h = 35.01 m."], "note": "Always remember: right triangle."},
        {"problem": "Two observers 100 m apart. Angles of elevation 30 and 45. Find height.", "steps": ["tan 45 = h/x, so h = x.", "tan 30 = h/(100-x).", "x(1 + sqrt(3)) = 100.", "x = 36.6, h = 36.6."], "note": "Always remember: two triangles."},
        {"problem": "Triangle ABC: AB = 7, BC = 9, angle B = 120. Find AC.", "steps": ["cos 120 = -0.5, so third term positive.", "AC^2 = 130 + 63 = 193.", "AC = 13.89."], "note": "Always remember: cos of obtuse angle is negative."},
        {"problem": "Triangle ABC: a = 10, b = 12, angle C = 45. Find area.", "steps": ["Area = (1/2)(10)(12)sin 45 = 42.43."], "note": "Always remember: (1/2)ab sin C."},
        {"problem": "Ship sails 20 km on bearing 060, then 15 km on bearing 150. Distance?", "steps": ["Angle between legs = 90.", "d^2 = 625.", "d = 25 km."], "note": "Always remember: bearings measured from north clockwise."},
        {"problem": "Ladder 8 m long makes angle 65. Height up wall?", "steps": ["sin 65 = h/8.", "h = 7.25."], "note": "Always remember: ladder is the hypotenuse."},
        {"problem": "Buildings 40 m apart. Angles of elevation 20 from top of shorter (12 m). Find taller height.", "steps": ["Difference = 40 tan 20 = 14.56.", "Taller = 26.56 m."], "note": "Always remember: difference is opposite side."},
        {"problem": "Triangle ABC: AB = 6, AC = 5, BC = 7. Find angle A.", "steps": ["cos A = 12/60 = 0.2.", "A = 78.46 degrees."], "note": "Always remember: rearranged cosine rule for angle."},
    ],
    "stats_written": [
        {"problem": "Box plot: Q1 = 20, median = 22, Q3 = 30. Comment.", "steps": ["Median closer to Q1.", "Box wider on right.", "Right-skewed."], "note": "Always remember: median closer to Q1 means skewed right."},
        {"problem": "Is 95 an outlier given Q1 = 20, Q3 = 40?", "steps": ["IQR = 20.", "Upper fence = 70.", "95 > 70, so outlier."], "note": "Always remember: state fences first."},
        {"problem": "Describe correlation if r = -0.85.", "steps": ["r close to -1.", "Negative means opposite directions.", "Strong negative."], "note": "Always remember: strength AND direction."},
        {"problem": "Is 3 an outlier given Q1 = 10, Q3 = 25?", "steps": ["IQR = 15.", "Lower fence = -12.5.", "3 > -12.5, so not an outlier."], "note": "Always remember: check both fences."},
        {"problem": "Histogram: long left tail. Describe.", "steps": ["Long tail left = left-skewed.", "Negatively skewed."], "note": "Always remember: tail points to skew direction."},
        {"problem": "Compare SD = 2 vs SD = 8.", "steps": ["Larger SD = more spread.", "SD = 8 is more spread."], "note": "Always remember: SD measures spread."},
        {"problem": "x-bar = 50, sigma = 5. Is 62 within one SD?", "steps": ["Range 45 to 55.", "62 > 55, not within."], "note": "Always remember: state interval first."},
        {"problem": "Compare z-scores: Student 1: 80% (mean 70, SD 10). Student 2: 60% (mean 40, SD 15).", "steps": ["Student 1: +1 SD.", "Student 2: +1.33 SD.", "Student 2 relatively better."], "note": "Always remember: compare z-scores, not raw marks."},
        {"problem": "Scatter plot widely scattered. Comment on r.", "steps": ["No pattern = weak correlation.", "r close to 0."], "note": "Always remember: r close to 0 means weak."},
        {"problem": "Histogram symmetric. Comment.", "steps": ["Symmetric means mirror halves.", "Mean close to median."], "note": "Always remember: symmetric data has mean close to median."},
    ],
}'''

src = src[:start] + NEW + src[end:]
ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Replaced stub with 39 entries across 4 templates")
print("Syntax OK")