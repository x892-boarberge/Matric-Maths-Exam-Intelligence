"""
N08 — Build misconception library from the 21 permanent buckets
and 1,111 DBE error narratives.
"""
import pandas as pd
from pathlib import Path

DIAG = Path("data/processed/diagnostics")
OUT = Path("data/processed/tutor/misconceptions_v2.csv")

MISCONCEPTIONS = [
    # ============================================================
    # ALGEBRA (ALG) — procedural + notation
    # ============================================================
    ("M_ALG_SIGN_FLIP_FACTOR", "ALG", "Quadratic equations", "procedural",
     "Learner sets a factor to zero but flips the sign of the root. (x+5)=0 → x=+5 instead of x=-5.",
     r"x\s*=\s*\+?\d+.*or|\(x\s*\+\s*\d+\).*=\s*0", "critical",
     "Flip the sign when moving the constant to the other side. Show the isolating step."),
    ("M_ALG_DIVIDE_BY_X_LOSE_ROOT", "ALG", "Quadratic equations", "procedural",
     "Learner divides both sides by x, losing the root x = 0.",
     r"x\^?2\s*=.*\bx\b.*(divide|/)|\bdivide.*\bby\s+x\b", "high",
     "Never divide an equation by x — factorise instead. Both roots must survive."),
    ("M_ALG_INEQUALITY_DIRECTION", "ALG", "Quadratic inequalities", "notation",
     "Learner writes -1 > x > 3 or reverses the direction when multiplying by a negative.",
     r"[-−]\s*\d+\s*>\s*x\s*>|\band\b.*[-−]\s*\d+", "critical",
     "Show the inequality flip explicitly. Use a number line before writing the answer."),
    ("M_ALG_STANDARD_FORM", "ALG", "Quadratic equations", "procedural",
     "Learner substitutes into the quadratic formula before writing ax²+bx+c=0.",
     r"quadratic\s+formula|b\^?2\s*[-−]\s*4\s*a\s*c", "high",
     "Standard form first. Every time. The coefficient c comes from the standard form line."),
    ("M_ALG_DISCRIMINANT_SIGN", "ALG", "Quadratic equations", "procedural",
     "Learner computes b²-4ac with a sign error on c.",
     r"Δ\s*=|\bdiscriminant\b", "high",
     "Write the discriminant with brackets around every negative coefficient before substituting."),
    ("M_ALG_SURD_NOT_ISOLATED", "ALG", "Surd equations", "procedural",
     "Learner squares both sides without isolating the radical first.",
     r"sqrt.*sqrt|√.*√|\bisolate.*radical", "critical",
     "Isolate the surd on one side. Then square. Then verify."),
    ("M_ALG_SURD_EXTRANEOUS_ROOT", "ALG", "Surd equations", "procedural",
     "Learner keeps all roots without rejecting the extraneous one introduced by squaring.",
     r"surd|extraneous|reject", "critical",
     "After squaring, substitute each root into the original equation. Reject any that fail."),
    ("M_ALG_EXP_NO_COMMON_BASE", "ALG", "Exponential equations", "procedural",
     "Learner 'cancels bases' without justification or factorises incorrectly.",
     r"\b2\^.*\b3\^|prime\s+base|factoris.*exponent", "high",
     "Write both sides with prime bases. Factor out the common factor. Never drop bases silently."),
    ("M_ALG_SET_NOTATION", "ALG", "Inequalities", "notation",
     "Learner uses = instead of ∈, or mixes set and interval notation.",
     r"\bx\s*=\s*[ℝR]\b|\bset\b.*\binterval\b", "medium",
     "Use ∈ ℝ or interval notation consistently. Do not write x = R."),
    ("M_ALG_K_SUBSTITUTION", "ALG", "Exponential equations", "procedural",
     "Learner substitutes k but fails to solve for x after finding k.",
     r"\blet\s+k\s*=|k\s*=\s*\d", "high",
     "After finding k, always reverse-substitute to get x. Reject negative k."),

    # ============================================================
    # SEQUENCES (SEQ)
    # ============================================================
    ("M_SEQ_OFF_BY_ONE", "SEQ", "Arithmetic sequences", "procedural",
     "Learner uses n instead of (n-1) in the term formula.",
     r"T_n\s*=\s*a\s*\+.*\bn\b(?!\s*-)", "high",
     "The exponent is (n-1), not n. This is the most common sequence error."),
    ("M_SEQ_TN_VS_SN", "SEQ", "Sequences", "procedural",
     "Learner confuses Tn (term) with Sn (sum).",
     r"\bT_n\b.*\bS_n\b|\bS_n\b.*\bT_n\b", "high",
     "Term vs sum. Read the question: 'find the term' → Tn. 'find the sum' → Sn."),
    ("M_SEQ_GP_CONVERGE", "SEQ", "Geometric series", "procedural",
     "Learner uses the finite sum formula when |r| < 1 requires the sum-to-infinity formula.",
     r"sum\s+to\s+infinity|S_inf|S_∞|\|-?1\s*<\s*r", "medium",
     "State the convergence condition -1 < r < 1 before using S_inf = a/(1-r)."),
    ("M_SEQ_QUADRATIC_SECOND_DIFF", "SEQ", "Quadratic sequences", "procedural",
     "Learner forgets that the second difference = 2a, and must be halved.",
     r"second\s+difference|2a\b", "high",
     "Second difference = 2a. Halve it to get a. Then use 3a + b = first difference."),
    ("M_SEQ_SIGMA_LIMITS", "SEQ", "Sequences", "procedural",
     "Learner writes the wrong lower or upper limit in sigma notation.",
     r"\\sum|sigma|Σ", "medium",
     "Check the first term corresponds to the lower limit. Expand the first few terms to verify."),

    # ============================================================
    # FUNCTIONS (FUNC)
    # ============================================================
    ("M_FUNC_DOMAIN_ASYMPTOTE", "FUNC", "Hyperbola", "procedural",
     "Learner writes the domain as x = 3 instead of x ≠ 3 (includes the asymptote).",
     r"\bx\s*=\s*\d+.*\bdomain|\bdomain\b.*\bx\s*=\s*\d+", "critical",
     "Domain excludes the asymptote. Write: x ∈ ℝ, x ≠ 3."),
    ("M_FUNC_RANGE_TURNING_POINT", "FUNC", "Parabola", "procedural",
     "Learner writes y < 8 instead of y ≤ 8 (excludes the turning point).",
     r"\by\s*<\s*\d+.*\brange|\brange\b.*<\s*\d+", "high",
     "The turning point IS in the range. Use ≤ or ≥ depending on the direction."),
    ("M_FUNC_INVERSE_DOMAIN", "FUNC", "Inverse functions", "procedural",
     "Learner swaps x and y correctly but forgets to restrict the inverse's domain.",
     r"\binverse\b|f\^-1|f⁻¹", "high",
     "The inverse's domain = the original's range. Restrict it explicitly."),
    ("M_FUNC_PARAMETER_PQ", "FUNC", "Hyperbola", "procedural",
     "Learner identifies p and q in a/(x+p)+q incorrectly.",
     r"a/\s*\(\s*x\s*[+-]|p\s*=|q\s*=", "high",
     "The form is a/(x-p)+q. The sign in the bracket gives p, and q is the vertical shift."),
    ("M_FUNC_ASYMPTOTE_MISSING", "FUNC", "Hyperbola", "procedural",
     "Learner does not draw or state the asymptotes when sketching.",
     r"asymptote|sketch.*hyperbola", "medium",
     "Draw asymptotes as dashed lines and write their equations."),
    ("M_FUNC_EXPONENTIAL_RANGE", "FUNC", "Exponential functions", "procedural",
     "Learner writes y > 0 when there is a vertical shift, or forgets the shift.",
     r"\by\s*>\s*0\b.*exp|exp.*\brange\b", "medium",
     "The range depends on the asymptote. State the asymptote first, then the range."),

    # ============================================================
    # FINANCE (FIN)
    # ============================================================
    ("M_FIN_COMPOUND_FREQUENCY", "FIN", "Compound interest", "procedural",
     "Learner uses n = 5 when the compounding is monthly (should be 5×12 = 60).",
     r"compounded\s+monthly|compounded\s+quarterly|n\s*=\s*\d+", "critical",
     "Monthly means n × 12. Quarterly means n × 4. Convert before substituting."),
    ("M_FIN_SIMPLE_VS_COMPOUND", "FIN", "Finance", "procedural",
     "Learner uses the simple interest formula when the problem requires compound, or vice versa.",
     r"simple\s+interest|compound\s+interest|A\s*=\s*P\s*\(\s*1", "high",
     "Read 'simple' or 'compound'. They use different formulas. Underline the word."),
    ("M_FIN_RATE_DECIMAL", "FIN", "Finance", "procedural",
     "Learner substitutes 7 instead of 0.07 or 7/1200 instead of 0.07/12.",
     r"[5-9]\s*%|1[0-5]\s*%", "high",
     "Convert percent to decimal explicitly. Show the conversion line."),
    ("M_FIN_EARLY_ROUNDING", "FIN", "Finance", "procedural",
     "Learner rounds intermediate values, compounding the error.",
     r"\bround\b|calculator", "medium",
     "Keep full accuracy in the calculator. Round only the final answer."),
    ("M_FIN_LOG_FOR_N", "FIN", "Loan repayment", "procedural",
     "Learner solves for n without logs, or rounds n down.",
     r"\bn\s*=|logs?|log\s*\(", "high",
     "Use logs to solve for n. Round n UP — you cannot make a fraction of a payment."),

    # ============================================================
    # CALCULUS (CALC)
    # ============================================================
    ("M_CALC_FP_FORMULA_WRONG", "CALC", "First principles", "notation",
     "Learner copies the first-principles formula incorrectly from the information sheet.",
     r"first\s+principles|lim|f\(x\+h\)", "critical",
     "Write the full formula: f'(x) = lim_{h→0} [f(x+h) - f(x)]/h. Bracket the numerator."),
    ("M_CALC_LIMIT_DROPPED", "CALC", "First principles", "notation",
     "Learner drops the lim h→0 before taking the limit.",
     r"\blim\b|\bh\s*→\s*0\b", "high",
     "Keep lim h→0 visible until you actually substitute h = 0."),
    ("M_CALC_FPRIME_ZERO", "CALC", "Cubic graphs", "procedural",
     "Learner does not explicitly set f'(x) = 0 when finding turning points.",
     r"turning\s+point|stationary|f'\(x\)", "high",
     "Write 'f'(x) = 0' on its own line. That line is a mark on its own."),
    ("M_CALC_SECOND_DERIV", "CALC", "Concavity", "procedural",
     "Learner uses f'(x) instead of f''(x) for concavity or nature of turning points.",
     r"concave|concavity|f''|second\s+deriv", "high",
     "Concavity uses the second derivative. f''(x) > 0 up, f''(x) < 0 down."),
    ("M_CALC_TANGENT_GRADIENT", "CALC", "Tangents", "procedural",
     "Learner uses f(x₀) as the tangent gradient instead of f'(x₀).",
     r"tangent.*gradient|m\s*=\s*f", "high",
     "Tangent gradient = f'(x₀). Point of contact = (x₀; f(x₀)). Two different values."),
    ("M_CALC_OPTIMISATION_PI", "CALC", "Optimisation", "procedural",
     "Learner treats π as a variable or fails to discard x = 0.",
     r"optimis|maximi|minimi|π", "critical",
     "π is a constant. Discard x = 0 if the context requires a positive dimension."),
    ("M_CALC_NATURE_TABLE", "CALC", "Cubic graphs", "procedural",
     "Learner writes 'it changes' without a sign table for f'(x).",
     r"sign\s+table|nature|f'\s*x", "medium",
     "Draw a sign table. Show f'(x) values either side of each stationary point."),

    # ============================================================
    # PROBABILITY (PROB)
    # ============================================================
    ("M_PROB_INDEPENDENCE_TEST", "PROB", "Independence", "procedural",
     "Learner uses the wrong test — proves independence instead of checking P(A∩B) = P(A)P(B).",
     r"independent|P\(A\s*∩\s*B\)|product", "critical",
     "Test: P(A and B) = P(A) × P(B). Show the multiplication, not a proof."),
    ("M_PROB_AT_LEAST", "PROB", "Probability", "reading",
     "Learner misreads 'at least', 'at most', 'none of', 'at least one'.",
     r"at\s+least|at\s+most|none\s+of|all\s+of", "critical",
     "For 'at least one', use 1 - P(none). Highlight the phrase in the question."),
    ("M_PROB_TREE_MULTIPLY", "PROB", "Tree diagrams", "procedural",
     "Learner adds along a path instead of multiplying, or multiplies final outcomes.",
     r"tree\s+diagram|branch|path", "high",
     "Multiply along a path. Add across paths. Never mix."),
    ("M_PROB_VENN_REGIONS", "PROB", "Venn diagrams", "procedural",
     "Learner does not fill all regions including the outside.",
     r"venn|universal\s+set|outside", "medium",
     "Fill every region including the region outside both sets. Check the total."),
    ("M_PROB_FACTORIAL_MISUSE", "PROB", "Counting", "procedural",
     "Learner inserts factorials where simple products are needed, or vice versa.",
     r"\d+!|factorial|arrange", "high",
     "n! for arrangements of all. Product rule for selections with restrictions."),

    # ============================================================
    # STATISTICS (STAT)
    # ============================================================
    ("M_STAT_CUMULATIVE_AS_FREQ", "STAT", "Frequency tables", "reading",
     "Learner reads cumulative frequency as ordinary frequency.",
     r"cumulative|ogive|freq.*table", "critical",
     "Cumulative frequency is a running total. To find a single class frequency, subtract the previous."),
    ("M_STAT_MEDIAN_POSITION", "STAT", "Median", "procedural",
     "Learner writes a median value without stating its position first.",
     r"median|\(n\+1\)/2|position", "medium",
     "State the position: (n+1)/2. Then find the value at that position."),
    ("M_STAT_LEAST_SQUARES_SWAP", "STAT", "Regression", "procedural",
     "Learner swaps a and b in the least-squares line y = a + bx.",
     r"least\s+squares|regression|y\s*=\s*a\s*\+", "high",
     "a is the y-intercept. b is the gradient. Check units to know which is which."),
    ("M_STAT_SD_INTERVAL", "STAT", "Standard deviation", "procedural",
     "Learner confuses x̄ ± σ with the range or the IQR.",
     r"standard\s+deviation|σ|x̄\s*±", "medium",
     "x̄ ± σ is one standard deviation either side of the mean. Not the range."),
    ("M_STAT_ROUNDING", "STAT", "Statistics", "procedural",
     "Learner does not round to the required number of decimal places.",
     r"round\s+off|decimal\s+place|2\s+decimals", "high",
     "Read the rounding instruction. Round only at the end."),

    # ============================================================
    # TRIGONOMETRY (TRIG)
    # ============================================================
    ("M_TRIG_REDUCTION_SIGN", "TRIG", "Reduction formulae", "procedural",
     "Learner gets the sign wrong when reducing angles > 90° or negative angles.",
     r"sin\s*\(\s*\d{2,3}|cos\s*\(\s*\d{2,3}|tan\s*\(\s*[-−]", "critical",
     "Use the CAST diagram. Identify the quadrant first. Then the sign."),
    ("M_TRIG_COMPOUND_UNRECOGNISED", "TRIG", "Compound angle", "procedural",
     "Learner fails to see the compound-angle pattern and expands tediously.",
     r"sin\s*\(\s*A\s*[+±]\s*B|cos\s*\(\s*A\s*[+±]\s*B", "high",
     "Look for the pattern sin(A+B) or cos(A+B) before expanding. It saves time and marks."),
    ("M_TRIG_GENERAL_SOLUTION", "TRIG", "General solutions", "procedural",
     "Learner gives only one solution, or omits + k·360° / + k·180°.",
     r"general\s+solution|k\s*·\s*360|k\s*·\s*180|k\s*∈\s*ℤ", "critical",
     "General solution includes + k·360° or + k·180°. State k ∈ ℤ."),
    ("M_TRIG_IDENTITY_ONE_SIDE", "TRIG", "Trig identities", "procedural",
     "Learner works on both sides of an identity at once.",
     r"prove\s+that|LHS|RHS|identity", "high",
     "Work on ONE side only. Label LHS and RHS. Never move terms across."),
    ("M_TRIG_SPECIAL_VALUES", "TRIG", "Trig equations", "procedural",
     "Learner uses decimal approximations instead of exact values (½, √3/2).",
     r"sin\s*30|cos\s*60|tan\s*45|exact\s+value", "medium",
     "Write exact values unless a decimal is asked. √3/2, not 0.866."),
    ("M_TRIG_3D_RULE_CHOICE", "TRIG", "3D trigonometry", "procedural",
     "Learner uses the wrong rule (sine vs cosine) in a 3D problem.",
     r"3D|sine\s+rule|cosine\s+rule|area\s+rule", "high",
     "Redraw the right-angled triangles. Name the rule. Write the formula line."),
    ("M_TRIG_AMPLITUDE_PERIOD", "TRIG", "Trig graphs", "procedural",
     "Learner does not state amplitude and period before sketching.",
     r"amplitude|period|sketch.*sin|sketch.*cos", "medium",
     "State amplitude and period first. Then mark intercepts and turning points."),

    # ============================================================
    # ANALYTICAL GEOMETRY (AGEO)
    # ============================================================
    ("M_AGEO_GRADIENT_SWAP", "AGEO", "Gradient", "procedural",
     "Learner swaps x and y in the gradient formula.",
     r"m\s*=|gradient|\(\s*y_2\s*-\s*y_1\s*\)", "critical",
     "Gradient = (y₂-y₁)/(x₂-x₁). The y difference on top. Always. Write the formula first."),
    ("M_AGEO_BRACKETS_NEG", "AGEO", "Analytical geometry", "procedural",
     "Learner omits brackets around negative coordinates, causing sign errors.",
     r"\(\s*[-−]\s*\d+\s*;|substitut", "high",
     "Brackets around every negative coordinate. Every time. No exceptions."),
    ("M_AGEO_TANGENT_RADIUS", "AGEO", "Tangents to circles", "procedural",
     "Learner forgets that the tangent is perpendicular to the radius at the point of contact.",
     r"tangent|radius|perpendicular", "critical",
     "Tangent ⊥ radius at point of contact. State it. Use m₁m₂ = -1."),
    ("M_AGEO_CIRCLE_FORM", "AGEO", "Circle equations", "procedural",
     "Learner identifies the wrong centre or radius from the general form.",
     r"x\^?2\s*\+.*y\^?2|centre|radius", "high",
     "Standard form: (x-h)² + (y-k)² = r². Centre (h; k). Radius r. Complete the square first."),
    ("M_AGEO_ASSUME_QUALITY", "AGEO", "Analytical proofs", "procedural",
     "Learner assumes midpoints, perpendicularity, or parallelity without proof.",
     r"assum|midpoint.*without|assume\s+perpendicular", "critical",
     "Prove it. Equal gradients for parallel. Product -1 for perpendicular. Midpoint for bisected."),

    # ============================================================
    # EUCLIDEAN GEOMETRY (EUCL)
    # ============================================================
    ("M_EUCL_NO_REASON", "EUCL", "Geometry proofs", "presentation",
     "Learner gives a statement with no reason, or an incomplete reason.",
     r"statement|reason|opp\s+angle|angle\s+at\s+centre", "critical",
     "Every statement gets a reason. 'Angle at centre' alone is not enough — 'Angle at centre = 2 × angle at circumference'."),
    ("M_EUCL_THEOREM_CONVERSE", "EUCL", "Circle theorems", "procedural",
     "Learner confuses a theorem with its converse.",
     r"converse|prove.*cyclic|prove.*tangent", "high",
     "Know the direction: forward or converse. 'Prove tangent' needs the converse."),
    ("M_EUCL_ANGLE_NAMING", "EUCL", "Geometry proofs", "notation",
     "Learner writes T̂ when they mean T̂₁ or T̂₂.",
     r"T̂|angle\s+T|∠T", "high",
     "Use numbered angle labels when two angles meet at the same vertex. Match the diagram."),
    ("M_EUCL_MISSING_CONSTRUCTION", "EUCL", "Circle theorems", "procedural",
     "Learner does not state the construction, or does not draw it.",
     r"construct|draw.*diameter|draw.*radius", "high",
     "State the construction: 'Draw KO produced'. Then state what you're proving."),
    ("M_EUCL_UNNECESSARY_CONSTRUCTION", "EUCL", "Geometry proofs", "procedural",
     "Learner makes a construction that isn't needed, losing time and marks.",
     r"unnecessary|unneeded\s+construction", "low",
     "Check whether the proof works without the construction. Only add what you need."),
    ("M_EUCL_ASSUME_FROM_DIAGRAM", "EUCL", "Geometry proofs", "procedural",
     "Learner assumes equal lengths or parallel lines from the visual diagram.",
     r"assum|diagram\s+not\s+to\s+scale|looks\s+equal", "critical",
     "Never assume from a diagram. If it's not given, prove it."),
    ("M_EUCL_SIMILARITY_ORDER", "EUCL", "Similar triangles", "procedural",
     "Learner writes the vertex order incorrectly when stating similarity.",
     r"similar|△.*∽|AAA", "high",
     "Match corresponding vertices. A→P, B→Q, C→R. Order matters."),
    ("M_EUCL_PROOF_ORDER", "EUCL", "Geometry proofs", "procedural",
     "Learner proves the final result before the intermediate steps that support it.",
     r"prove\s+that|first\s+prove|prerequisite", "medium",
     "Prove intermediate results first. Each step supports the next."),

    # ============================================================
    # CROSS-CUTTING PRESENTATION & READING
    # ============================================================
    ("M_READ_INSTRUCTION_MISSED", "GEN", "Reading", "reading",
     "Learner misses key instruction words: 'hence', 'correct to', 'without calculator', 'show that'.",
     r"hence|correct\s+to|without\s+calculator|show\s+that", "high",
     "Underline the instruction word. It changes the required method."),
    ("M_READ_AT_LEAST", "GEN", "Reading", "reading",
     "Learner misses conditional phrases: 'at least', 'deferred', 'part thereof'.",
     r"at\s+least|deferred|part\s+thereof|at\s+most", "medium",
     "Highlight conditional phrases. They change the calculation."),
    ("M_PRES_NO_METHOD", "GEN", "Presentation", "presentation",
     "Learner writes only the answer with no working shown.",
     r"answer\s+only|no\s+working|method\s+line", "critical",
     "Method marks need lines. Show every step. 'Answer only' loses method marks."),
    ("M_PRES_NO_UNITS", "GEN", "Presentation", "presentation",
     "Learner omits units in measurement, money or rate questions.",
     r"units|cm|m²|km/h|R\s*\d", "medium",
     "State the unit. The final answer needs it."),
    ("M_PRES_ROUNDING", "GEN", "Presentation", "presentation",
     "Learner does not round to the required decimal places.",
     r"round|decimal\s+places|2\s+decimals", "high",
     "Read the rounding instruction. Round only at the final step."),
    ("M_PRES_ONE_STEP_ONE_LINE", "GEN", "Presentation", "presentation",
     "Learner chains multiple steps on one line, making reasoning hard to follow.",
     r"multi-step|chain|one\s+line", "medium",
     "One mathematical step per line. The marker needs to see each one."),
]

rows = []
for (mid, topic, subtopic, cls, desc, trigger, severity, intervention) in MISCONCEPTIONS:
    rows.append({
        "misconception_id": mid,
        "topic": topic,
        "subtopic": subtopic,
        "error_class": cls,
        "description": desc,
        "trigger_pattern": trigger,
        "severity": severity,
        "intervention": intervention,
        "source": "N08 v2 from N06 analysis",
    })

df = pd.DataFrame(rows)
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False, encoding="utf-8")

print(f"Wrote {len(df)} misconceptions to {OUT}")
print()
print("By topic:")
print(df["topic"].value_counts().to_string())
print()
print("By error_class:")
print(df["error_class"].value_counts().to_string())
print()
print("By severity:")
print(df["severity"].value_counts().to_string())