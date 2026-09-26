import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tutor.analogue_library import _refine_template

CASES = [
    ("algebra.quadratic.solve", "Solve x^2+x-12=0"),
    ("algebra.quadratic.solve", "Solve for x: (x+5)(x-2)=0"),
    ("algebra.quadratic.solve", "Solve 2x^2-4x+1=0"),
    ("algebra.quadratic.solve", "Solve x^2-2x-3 > 0"),
    ("sequences.gp.term", "Calculate the value of T25"),
    ("sequences.ap.sum", "Find the sum of the first 20 terms"),
    ("sequences.quadratic.general", "Find the general term"),
    ("functions.parabola.range", "State the range of f"),
    ("functions.hyperbola.domain", "Write down the domain of g"),
    ("functions.exponential.value", "Solve for x"),
    ("finance.compound", "Calculate the final amount"),
    ("finance.annuity.future", "Future value of the annuity"),
    ("calculus.derivative.first_principles", "First principles"),
    ("calculus.derivative.rules", "Differentiate"),
    ("calculus.cubic.turning", "Find the turning points"),
    ("probability.independence", "Are A and B independent?"),
    ("probability.union", "Calculate P(A or B)"),
    ("stats.median", "Find the median"),
    ("stats.regression.equation", "Least squares regression line"),
    ("analytical_geom.distance", "Distance between A and B"),
    ("analytical_geom.gradient", "Find the gradient"),
    ("trig.reduction.simplify", "Simplify sin(180 - x)"),
    ("trig.double_angle", "Find sin(2x)"),
    ("euclidean.semicircle.prove", "Prove angle ACB = 90"),
    ("euclidean.similarity.ratio", "Find the ratio"),
]

print(f"{'skill_id':<42s} {'prompt':<40s} -> template")
print("=" * 130)
for skill, prompt in CASES:
    t = _refine_template(skill, prompt)
    marker = ""
    if t is None:
        marker = "  [NONE]"
    elif t == "UNMAPPED":
        marker = "  [UNMAPPED]"
    elif t and t.endswith("_written"):
        marker = "  [WRITTEN]"
    print(f"{skill:<42s} {prompt[:40]:<40s} -> {t}{marker}")