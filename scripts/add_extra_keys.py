"""Add 4 keys to existing EXTRA_WRITTEN_ANALOGUES without replacing the dict."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

# Check if our keys already exist
if '"trig_written"' in src.split("EXTRA_WRITTEN_ANALOGUES = {")[1].split("}")[0] if "EXTRA_WRITTEN_ANALOGUES = {" in src else False:
    print("Keys already present")
    raise SystemExit(0)

# Find the start of the dict
start_marker = "EXTRA_WRITTEN_ANALOGUES = {"
start = src.find(start_marker)
if start < 0:
    print("Dict not found")
    raise SystemExit(1)

# Find matching closing brace
brace_start = src.find("{", start)
depth = 0
brace_end = brace_start
for i in range(brace_start, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            brace_end = i
            break

# Extract existing content between braces
existing = src[brace_start+1:brace_end]

# New keys to append
NEW_KEYS = '''
    "trig_written": [
        {"problem": "Prove that cos 2x = 1 - 2 sin^2 x.", "steps": ["cos 2x = cos^2 x - sin^2 x.", "Replace cos^2 x with 1 - sin^2 x.", "= 1 - 2 sin^2 x."], "note": "Always remember: cos 2x has three forms."},
        {"problem": "Prove that sin^2 x + cos^2 x = 1.", "steps": ["Right triangle: sin = y/r, cos = x/r.", "sin^2 + cos^2 = (y^2 + x^2)/r^2 = 1."], "note": "Always remember: the Pythagorean identity."},
        {"problem": "Prove that sin(A+B) + sin(A-B) = 2 sin A cos B.", "steps": ["sin(A+B) = sin A cos B + cos A sin B.", "sin(A-B) = sin A cos B - cos A sin B.", "Add: 2 sin A cos B."], "note": "Always remember: expand both, add."},
        {"problem": "Prove that sin(A+B) - sin(A-B) = 2 cos A sin B.", "steps": ["sin(A+B) = sin A cos B + cos A sin B.", "sin(A-B) = sin A cos B - cos A sin B.", "Subtract: 2 cos A sin B."], "note": "Always remember: subtract instead of add."},
        {"problem": "Prove that cos(A+B) + cos(A-B) = 2 cos A cos B.", "steps": ["cos(A+B) = cos A cos B - sin A sin B.", "cos(A-B) = cos A cos B + sin A sin B.", "Add: 2 cos A cos B."], "note": "Always remember: cos sum minus sin product."},
        {"problem": "Prove that 1 + tan^2 x = sec^2 x.", "steps": ["Divide sin^2 + cos^2 = 1 by cos^2.", "tan^2 x + 1 = sec^2 x."], "note": "Always remember: divide by cos^2."},
        {"problem": "Prove that 1 + cot^2 x = cosec^2 x.", "steps": ["Divide sin^2 + cos^2 = 1 by sin^2.", "1 + cot^2 x = cosec^2 x."], "note": "Always remember: divide by sin^2."},
        {"problem": "Prove that cos 2x = 2 cos^2 x - 1.", "steps": ["cos 2x = cos^2 x - sin^2 x.", "Replace sin^2 x with 1 - cos^2 x.", "= 2 cos^2 x - 1."], "note": "Always remember: cos-only form."},
        {"problem": "Prove that sin 2x = 2 tan x / (1 + tan^2 x).", "steps": ["Substitute tan x and 1 + tan^2 x = sec^2 x.", "= 2 sin x cos x = sin 2x."], "note": "Always remember: convert to sin/cos."},
    ],
    "trig_graph_written": [
        {"problem": "Sketch y = sin 2x. State the period.", "steps": ["Period = 180.", "Amplitude = 1.", "Two cycles."], "note": "Always remember: period = 360 / coefficient."},
        {"problem": "Sketch y = 3 sin x.", "steps": ["Amplitude = 3.", "Range = [-3; 3]."], "note": "Always remember: number in front is amplitude."},
        {"problem": "Sketch y = cos(x - 90).", "steps": ["Shifted 90 right.", "cos(x - 90) = sin x."], "note": "Always remember: shift cos 90 gives sin."},
        {"problem": "Sketch y = tan x.", "steps": ["Period = 180.", "Asymptotes at 90 and 270."], "note": "Always remember: tan asymptotes where cos = 0."},
        {"problem": "Sketch y = -cos x.", "steps": ["Reflection in x-axis."], "note": "Always remember: negative reflects vertically."},
        {"problem": "Sketch y = sin x + 2.", "steps": ["Shifted up by 2.", "Range = [1; 3]."], "note": "Always remember: constant shifts vertically."},
        {"problem": "Sketch y = 2 cos 2x.", "steps": ["Amplitude 2, period 180."], "note": "Always remember: amplitude and period independent."},
        {"problem": "Sketch y = sin(x + 30).", "steps": ["Shifted 30 left."], "note": "Always remember: plus inside shifts left."},
        {"problem": "Sketch y = -2 sin x.", "steps": ["Amplitude 2, range [-2; 2].", "Reflected."], "note": "Always remember: reflection flips peaks."},
    ],
    "trig_3d_written": [
        {"problem": "Triangle ABC: AB = 8, AC = 6, angle A = 60. Find BC.", "steps": ["Cosine rule: BC^2 = 64 + 36 - 48 = 52.", "BC = sqrt(52)."], "note": "Always remember: cosine rule for two sides and included angle."},
        {"problem": "Pole 10 m casts shadow 8 m. Angle of elevation?", "steps": ["tan(theta) = 10/8 = 1.25.", "theta = 51.34."], "note": "Always remember: draw right triangle first."},
        {"problem": "From 50 m, angle of elevation to tower top is 35. Find height.", "steps": ["tan 35 = h/50.", "h = 35.01 m."], "note": "Always remember: right triangle."},
        {"problem": "Two observers 100 m apart. Angles of elevation 30 and 45. Find height.", "steps": ["tan 45 = h/x, so h = x.", "tan 30 = h/(100-x).", "x(1+sqrt(3)) = 100.", "x = 36.6."], "note": "Always remember: two triangles."},
        {"problem": "Triangle ABC: AB = 7, BC = 9, angle B = 120. Find AC.", "steps": ["cos 120 = -0.5.", "AC^2 = 193.", "AC = 13.89."], "note": "Always remember: cos obtuse is negative."},
        {"problem": "Triangle ABC: a = 10, b = 12, angle C = 45. Find area.", "steps": ["Area = (1/2)(10)(12)sin 45 = 42.43."], "note": "Always remember: (1/2)ab sin C."},
        {"problem": "Ship 20 km on 060 then 15 km on 150. Distance?", "steps": ["Angle between = 90.", "d^2 = 625.", "d = 25 km."], "note": "Always remember: bearings clockwise from north."},
        {"problem": "Ladder 8 m makes angle 65. Height?", "steps": ["sin 65 = h/8.", "h = 7.25."], "note": "Always remember: ladder is the hypotenuse."},
        {"problem": "Buildings 40 m apart. Angle 20 from shorter (12 m). Find taller.", "steps": ["Difference = 40 tan 20 = 14.56.", "Taller = 26.56."], "note": "Always remember: difference is opposite."},
        {"problem": "Triangle ABC: AB = 6, AC = 5, BC = 7. Find angle A.", "steps": ["cos A = 12/60 = 0.2.", "A = 78.46."], "note": "Always remember: rearranged cosine rule."},
    ],
    "stats_written": [
        {"problem": "Box plot: Q1 = 20, median = 22, Q3 = 30. Comment.", "steps": ["Median closer to Q1.", "Box wider on right.", "Right-skewed."], "note": "Always remember: median closer to Q1 = right skew."},
        {"problem": "Is 95 an outlier given Q1 = 20, Q3 = 40?", "steps": ["IQR = 20.", "Upper fence = 70.", "Outlier."], "note": "Always remember: state fences first."},
        {"problem": "Describe r = -0.85.", "steps": ["r close to -1.", "Strong negative."], "note": "Always remember: strength AND direction."},
        {"problem": "Is 3 an outlier given Q1 = 10, Q3 = 25?", "steps": ["Lower fence = -12.5.", "Not an outlier."], "note": "Always remember: check both fences."},
        {"problem": "Histogram: long left tail.", "steps": ["Left-skewed."], "note": "Always remember: tail points to skew."},
        {"problem": "Compare SD = 2 vs SD = 8.", "steps": ["SD = 8 more spread."], "note": "Always remember: SD measures spread."},
        {"problem": "x-bar = 50, sigma = 5. Is 62 within one SD?", "steps": ["Range 45-55.", "No."], "note": "Always remember: state interval."},
        {"problem": "Compare z: 80% (mean 70 SD 10) vs 60% (mean 40 SD 15).", "steps": ["Z1 = +1.", "Z2 = +1.33.", "Student 2 better."], "note": "Always remember: compare z-scores."},
        {"problem": "Scatter widely scattered.", "steps": ["Weak correlation.", "r close to 0."], "note": "Always remember: r near 0 = weak."},
        {"problem": "Histogram symmetric.", "steps": ["Mirror halves.", "Mean = median."], "note": "Always remember: symmetric = mean near median."},
    ],
'''

# Insert new keys just before the closing brace
new_src = src[:brace_end] + NEW_KEYS + src[brace_end:]

try:
    ast.parse(new_src)
    P.write_text(new_src, encoding="utf-8")
    print("Added 4 keys to EXTRA_WRITTEN_ANALOGUES")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)
    print(f"Line {e.lineno}: {e.msg}")