"""
Analogue generators.

Each generator produces a list of worked analogues for one template.
Called once at library load; results are cached. Analogue selection
picks a random one, excluding those already shown in the session.

All generators return list[dict] with keys:
    problem : str      the worked problem statement
    steps   : list[str] the solution steps
    note    : str      the takeaway
"""
import random


def _x_term(v):
    if v > 0:
        return f"x + {v}"
    if v < 0:
        return f"x - {abs(v)}"
    return "x"


def gen_quadratic_factored(count=200, seed=11):
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
        a = rng.randint(-9, 9)
        b = rng.randint(-9, 9)
        if a == 0 or b == 0 or a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        r1, r2 = -a, -b
        out.append({
            "problem": f"Solve ({_x_term(a)})({_x_term(b)}) = 0",
            "steps": [
                "When a product is zero, at least one factor is zero.",
                f"{_x_term(a)} = 0  gives  x = {r1}",
                f"{_x_term(b)} = 0  gives  x = {r2}",
                f"Answer:  x = {r1}  or  x = {r2}",
            ],
            "note": "Always remember: The sign inside the bracket is not the root. Flip it.",
        })
    return out


def gen_quadratic_inequality(count=50, seed=13):
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
        r1 = rng.randint(-8, 8)
        r2 = rng.randint(-8, 8)
        if r1 == r2:
            continue
        lo, hi = min(r1, r2), max(r1, r2)
        key = (lo, hi)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "problem": f"Solve x^2 - {(r1 + r2)}x + {r1 * r2} > 0",
            "steps": [
                f"Factorise: (x - {r1})(x - {r2}) > 0",
                f"Critical values: x = {r1} and x = {r2}",
                "Sketch a quick parabola or number line.",
                f"Outside the roots: x < {lo} or x > {hi}",
            ],
            "note": "For '> 0', the answer is outside the roots. For '< 0', between them.",
        })
    return out


def gen_exponential_quadratic(count=50, seed=14):
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
        p = rng.choice([2, 3])
        x1 = rng.randint(-3, 3)
        x2 = rng.randint(-3, 3)
        if x1 == x2:
            continue
        key = (p, min(x1, x2), max(x1, x2))
        if key in seen:
            continue
        seen.add(key)
        s = (p ** x1) + (p ** x2)
        prod = p ** (x1 + x2)
        out.append({
            "problem": f"Solve {p}^(2x) - {s}.{p}^x + {prod} = 0",
            "steps": [
                f"Let k = {p}^x. Then {p}^(2x) = k^2.",
                f"k^2 - {s}k + {prod} = 0",
                f"Factorise: (k - {p ** x1})(k - {p ** x2}) = 0",
                f"So {p}^x = {p ** x1}  or  {p}^x = {p ** x2}",
                f"Answer:  x = {x1}  or  x = {x2}",
            ],
            "note": "Always remember: Substitute k to turn an exponential equation into a quadratic. Reject negative k.",
        })
    return out


def gen_ap_term(count=200, seed=21):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.randint(-9, 15)
        d = rng.randint(2, 9)
        n = rng.randint(5, 40)
        t_n = a + (n - 1) * d
        out.append({
            "problem": f"An arithmetic sequence has a = {a} and d = {d}. Find T_{n}.",
            "steps": [
                "Formula: T_n = a + (n - 1)d",
                f"Substitute: a = {a}, d = {d}, n = {n}",
                f"T_{n} = {a} + ({n} - 1)({d})",
                f"T_{n} = {a} + {(n - 1) * d}",
                f"Answer:  T_{n} = {t_n}",
            ],
            "note": "Always remember: The exponent is (n - 1), not n. Off-by-one is the common error.",
        })
    return out


def gen_ap_sum(count=200, seed=22):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.randint(1, 10)
        d = rng.randint(2, 8)
        n = rng.randint(5, 30)
        s_n = n * (2 * a + (n - 1) * d) // 2
        out.append({
            "problem": f"An arithmetic sequence has a = {a} and d = {d}. Find S_{n}.",
            "steps": [
                "Formula: S_n = (n/2)[2a + (n - 1)d]",
                f"S_{n} = ({n}/2)[2({a}) + ({n} - 1)({d})]",
                f"S_{n} = ({n}/2)[{2 * a + (n - 1) * d}]",
                f"Answer:  S_{n} = {s_n}",
            ],
            "note": "Always remember: Substitute into the formula before simplifying. Method marks depend on the substitution line.",
        })
    return out


def gen_gp_term(count=200, seed=23):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([2, 3, 4, 5, 6, 8])
        r = rng.choice([-3, -2, -1, 2, 3])
        n = rng.randint(4, 12)
        out.append({
            "problem": f"A geometric sequence has a = {a} and r = {r}. Find T_{n}.",
            "steps": [
                "Formula: T_n = a.r^(n - 1)",
                f"T_{n} = {a}.({r})^{n - 1}",
                "Leave in exponential form unless the question asks for a value.",
            ],
            "note": "Always remember: The exponent is (n - 1). For negative r, watch the sign of the power.",
        })
    return out


def gen_gp_sum(count=50, seed=25):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, 2, 3, 4, 6, 8])
        r = rng.choice([2, 3, -2, -3])
        n = rng.randint(4, 10)
        out.append({
            "problem": f"A geometric sequence has a = {a} and r = {r}. Find S_{n}.",
            "steps": [
                "Formula: S_n = a(r^n - 1) / (r - 1)",
                f"S_{n} = {a}(({r})^{n} - 1) / ({r} - 1)",
                "Simplify carefully, especially when r is negative.",
            ],
            "note": "Always remember: The denominator is (r - 1), not (1 - r). Getting this backwards flips the sign.",
        })
    return out


def gen_gp_infinite(count=50, seed=26):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([2, 3, 4, 6, 8, 12])
        r_num = rng.choice([1, 1, 1, 2])
        r_den = rng.choice([2, 3, 4])
        if r_num >= r_den:
            continue
        out.append({
            "problem": f"A geometric sequence has a = {a} and r = {r_num}/{r_den}. Find S_inf.",
            "steps": [
                "Condition: |r| < 1, so the series converges.",
                "Formula: S_inf = a / (1 - r)",
                f"S_inf = {a} / (1 - {r_num}/{r_den})",
                "Simplify the denominator before dividing.",
            ],
            "note": "Always remember: State the condition |r| < 1 before using the formula. It earns a mark.",
        })
    return out


def gen_quadratic_sequence_general(count=50, seed=27):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, -1, 2, -2])
        b = rng.randint(-6, 6)
        c = rng.randint(-8, 8)
        t1 = a + b + c
        t2 = 4 * a + 2 * b + c
        t3 = 9 * a + 3 * b + c
        out.append({
            "problem": f"A quadratic sequence starts {t1}; {t2}; {t3}; ... Find T_n.",
            "steps": [
                f"First differences: {t2 - t1}; {t3 - t2}; ...",
                f"Second difference = {2 * a}, so a = {a}.",
                f"Use 3a + b = first difference to get b = {b}.",
                f"Use a + b + c = T_1 to get c = {c}.",
                f"Answer:  T_n = {a}n^2 {b:+d}n {c:+d}",
            ],
            "note": "Always remember: Second difference = 2a. Do not forget to divide by 2.",
        })
    return out


def gen_quadratic_sequence_term(count=50, seed=28):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, -1])
        b = rng.randint(-6, 6)
        c = rng.randint(-8, 8)
        n = rng.randint(5, 15)
        t_n = a * n * n + b * n + c
        out.append({
            "problem": f"Quadratic sequence T_n = {a}n^2 {b:+d}n {c:+d}. Find T_{n}.",
            "steps": [
                f"Substitute n = {n}",
                f"T_{n} = {a}({n})^2 {b:+d}({n}) {c:+d}",
                "Compute the square first, then multiply, then add.",
                f"Answer:  T_{n} = {t_n}",
            ],
            "note": "Always remember: Substitute n on its own line before computing.",
        })
    return out


def gen_gp_ratio(count=50, seed=24):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        r = rng.choice([-3, -2, -1, 2, 3, 4])
        a = rng.randint(2, 12)
        t1, t2, t3 = a, a * r, a * r * r
        out.append({
            "problem": f"A geometric sequence has terms {t1}; {t2}; {t3}; ... Find r.",
            "steps": [
                "Formula: r = T_2 / T_1",
                f"r = {t2} / {t1}",
                f"Answer:  r = {r}",
            ],
            "note": "Always remember: Divide the second term by the first.",
        })
    return out

def gen_derivative_rules(count=200, seed=31):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.randint(-9, 9) or 1
        b = rng.randint(-9, 9) or 1
        c = rng.randint(-9, 9)
        n = rng.randint(2, 5)
        m = rng.randint(1, 4)
        out.append({
            "problem": f"Differentiate f(x) = {a}x^{n} {b:+d}x^{m} {c:+d}",
            "steps": [
                "Differentiate each term using the power rule: d/dx[x^n] = n.x^(n-1).",
                f"d/dx[{a}x^{n}] = {a * n}x^{n - 1}",
                f"d/dx[{b}x^{m}] = {b * m}x^{m - 1}" if m != 1 else f"d/dx[{b}x] = {b}",
                f"d/dx[{c}] = 0",
                f"Answer:  f'(x) = {a * n}x^{n - 1} {b * m:+d}x^{m - 1}",
            ],
            "note": "Always remember: The derivative of a constant is zero. Do not forget the last term drops out.",
        })
    return out


def gen_derivative_first_principles(count=50, seed=32):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([-8, -6, -4, -2, 2, 4, 6, 8])
        out.append({
            "problem": f"Differentiate f(x) = {a}x^2 from first principles.",
            "steps": [
                "Formula: f'(x) = lim_{h->0} [f(x + h) - f(x)] / h",
                f"f(x + h) = {a}(x + h)^2 = {a}x^2 + {2 * a}xh + {a}h^2",
                f"f(x + h) - f(x) = {2 * a}xh + {a}h^2",
                f"Divide by h: {2 * a}x + {a}h",
                f"Take limit as h -> 0:  f'(x) = {2 * a}x",
            ],
            "note": "Always remember: Write the full formula on its own line. That is the method mark.",
        })
    return out


def gen_calculus_tangent(count=50, seed=34):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.randint(1, 4)
        x0 = rng.randint(-3, 3)
        out.append({
            "problem": f"Find the equation of the tangent to f(x) = {a}x^2 at x = {x0}.",
            "steps": [
                f"Differentiate: f'(x) = {2 * a}x",
                f"Gradient: m = f'({x0}) = {2 * a * x0}",
                f"Point of contact: ({x0}; {a * x0 * x0})",
                f"Equation: y - {a * x0 * x0} = {2 * a * x0}(x - ({x0}))",
                "Simplify to y = mx + c form.",
            ],
            "note": "Always remember: Write the point of contact on its own line. Method marks depend on it.",
        })
    return out


def gen_cubic_turning(count=50, seed=33):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        r1 = rng.randint(-4, 4)
        r2 = rng.randint(-4, 4)
        if r1 == r2:
            continue
        out.append({
            "problem": f"Find the x-coordinates of the turning points of f where f'(x) = 3(x - {r1})(x - {r2}).",
            "steps": [
                "Turning points occur where f'(x) = 0.",
                f"Set (x - {r1})(x - {r2}) = 0",
                f"x = {r1}  or  x = {r2}",
                "Substitute each x back into f(x) for the y-coordinate.",
            ],
            "note": "Always remember: Set f'(x) = 0 on its own line before factorising.",
        })
    return out


def gen_parabola_turning(count=200, seed=41):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([-2, -1, 1, 2])
        h = rng.randint(-6, 6)
        k = rng.randint(-9, 9)
        out.append({
            "problem": f"Find the turning point of f(x) = {a}(x - ({h}))^2 + {k}.",
            "steps": [
                "Form f(x) = a(x - h)^2 + k has turning point (h; k).",
                f"Compare: h = {h}, k = {k}",
                f"Answer:  turning point is ({h}; {k})",
            ],
            "note": "Always remember: The sign inside the bracket flips. x = h, not -h.",
        })
    return out


def gen_parabola_range(count=50, seed=42):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([-2, -1, 1, 2])
        h = rng.randint(-6, 6)
        k = rng.randint(-9, 9)
        op = ">=" if a > 0 else "<="
        direction = "upward" if a > 0 else "downward"
        out.append({
            "problem": f"State the range of f(x) = {a}(x - ({h}))^2 + {k}.",
            "steps": [
                f"The turning point is ({h}; {k}).",
                f"a = {a}, so the parabola opens {direction}.",
                f"Range:  y {op} {k}",
            ],
            "note": "Always remember: Range depends on the y-value of the turning point and the sign of a.",
        })
    return out


def gen_parabola_intercept(count=50, seed=43):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        r1 = rng.randint(-6, 6)
        r2 = rng.randint(-6, 6)
        if r1 == r2:
            continue
        a = rng.choice([-2, -1, 1, 2])
        out.append({
            "problem": f"Find the x-intercepts of f(x) = {a}(x - {r1})(x - {r2}).",
            "steps": [
                "Set f(x) = 0.",
                f"(x - {r1})(x - {r2}) = 0",
                f"x = {r1}  or  x = {r2}",
                f"Answer:  ({r1}; 0) and ({r2}; 0)",
            ],
            "note": "Always remember: The x-intercepts are where y = 0. Write them as coordinates.",
        })
    return out


def gen_parabola_equation(count=50, seed=44):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([-2, -1, 1, 2])
        h = rng.randint(-4, 4)
        k = rng.randint(-9, 9)
        out.append({
            "problem": f"A parabola has turning point ({h}; {k}) and passes through ({h + 1}; {k + a}). Find its equation.",
            "steps": [
                "Use form y = a(x - h)^2 + k.",
                f"Substitute turning point: y = a(x - ({h}))^2 + {k}",
                f"Substitute the other point: {k + a} = a({h + 1} - ({h}))^2 + {k}",
                f"Solve for a: a = {a}",
                f"Answer:  y = {a}(x - ({h}))^2 + {k}",
            ],
            "note": "Always remember: Two pieces of info: turning point gives h and k, one point gives a.",
        })
    return out


def gen_hyperbola_domain(count=50, seed=45):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        p = rng.randint(-9, 9)
        if p == 0:
            continue
        out.append({
            "problem": f"Write down the domain of g(x) = 1 / (x - ({p})).",
            "steps": [
                "The denominator cannot be zero.",
                f"x - ({p}) = 0  gives  x = {p}",
                f"Exclude:  x in R, x not equal to {p}",
            ],
            "note": "Always remember: The vertical asymptote is the value that makes the denominator zero.",
        })
    return out


def gen_hyperbola_equation(count=50, seed=46):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([-6, -4, -2, 2, 4, 6])
        p = rng.randint(-5, 5)
        q = rng.randint(-5, 5)
        out.append({
            "problem": f"Find the hyperbola with asymptotes x = {p} and y = {q}, passing through x = 0.",
            "steps": [
                "Form: y = a/(x - p) + q",
                f"From asymptotes: y = a/(x - ({p})) + {q}",
                "Substitute a given point to solve for a.",
                f"Answer:  y = {a}/(x - ({p})) + {q}",
            ],
            "note": "Always remember: Asymptotes give p and q directly. One point on the curve gives a.",
        })
    return out


def gen_line_equation(count=50, seed=47):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
        if x1 == x2 or y1 == y2:
            continue
        m = (y2 - y1) / (x2 - x1)
        out.append({
            "problem": f"Find the equation of the line through ({x1}; {y1}) and ({x2}; {y2}).",
            "steps": [
                f"Gradient: m = (y2 - y1)/(x2 - x1) = ({y2} - ({y1}))/({x2} - ({x1}))",
                f"m = {m:.2f}",
                f"Point-gradient form: y - ({y1}) = m(x - ({x1}))",
                "Simplify to y = mx + c.",
            ],
            "note": "Always remember: Write the gradient formula on its own line.",
        })
    return out


def gen_exponential_value(count=50, seed=48):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([2, 3, 5])
        k = rng.randint(1, 4)
        out.append({
            "problem": f"Solve {a}^x = {a ** k}.",
            "steps": [
                f"Write RHS as a power of {a}: {a ** k} = {a}^{k}",
                f"Same base: equate exponents. x = {k}",
            ],
            "note": "Always remember: Same base on both sides: exponents are equal.",
        })
    return out


def gen_finance_compound(count=200, seed=51):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        p = rng.choice([1000, 2000, 5000, 10000, 20000])
        r = rng.choice([5, 6, 7, 8, 9, 10, 12])
        n = rng.randint(3, 15)
        out.append({
            "problem": f"R{p} invested at {r}% per year compounded annually for {n} years. Find the final amount.",
            "steps": [
                "Formula: A = P(1 + i)^n",
                f"P = {p}, i = {r}/100 = {r / 100}, n = {n}",
                f"A = {p}(1 + {r / 100})^{n}",
                "Compute with full accuracy, round at the end.",
            ],
            "note": "Always remember: Convert the percentage to a decimal before substituting.",
        })
    return out


def gen_finance_simple(count=50, seed=52):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        p = rng.choice([1000, 2000, 5000, 10000])
        r = rng.choice([5, 6, 7, 8, 10])
        n = rng.randint(2, 8)
        out.append({
            "problem": f"R{p} invested at {r}% per year simple interest for {n} years. Find the interest earned.",
            "steps": [
                "Formula: I = P.i.n",
                f"P = {p}, i = {r / 100}, n = {n}",
                f"I = {p} x {r / 100} x {n}",
                "Round money to two decimal places.",
            ],
            "note": "Always remember: Simple interest uses i.n, not (1+i)^n.",
        })
    return out


def gen_finance_annuity_future(count=50, seed=53):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x = rng.choice([500, 1000, 1500, 2000, 2500])
        r = rng.choice([6, 7, 8, 9, 10])
        n = rng.randint(5, 20)
        out.append({
            "problem": f"R{x} paid monthly into an account at {r}% p.a. compounded monthly for {n} years. Find the future value.",
            "steps": [
                "Formula: F = x[((1 + i)^n - 1) / i]",
                f"i = {r}/1200, n = {n * 12}",
                f"F = {x}[((1 + {r / 1200})^{n * 12} - 1) / {r / 1200}]",
                "Keep full accuracy, round at the end.",
            ],
            "note": "Always remember: Monthly rate = annual / 12. Periods = years x 12.",
        })
    return out


def gen_finance_loan_n(count=50, seed=54):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        p = rng.choice([10000, 20000, 50000, 100000])
        x = rng.choice([500, 1000, 1500, 2000])
        r = rng.choice([7, 8, 9, 10, 11, 12])
        out.append({
            "problem": f"Loan R{p}, monthly payment R{x}, rate {r}% p.a. compounded monthly. Find n.",
            "steps": [
                "Formula: P = x[1 - (1 + i)^(-n)] / i",
                f"i = {r}/1200, x = {x}",
                "Substitute and solve for n using logs.",
                "Round n UP to the next whole month.",
            ],
            "note": "Use logs to solve for n. Always round up.",
        })
    return out


def gen_finance_effective(count=50, seed=55):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        r = rng.choice([6, 7, 8, 9, 10, 12])
        m = rng.choice([2, 4, 12])
        out.append({
            "problem": f"Nominal {r}% p.a. compounded {m} times per year. Find the effective annual rate.",
            "steps": [
                "Formula: 1 + i_eff = (1 + i_nom/m)^m",
                f"i_nom = {r / 100}, m = {m}",
                f"1 + i_eff = (1 + {r / 100}/{m})^{m}",
                "Subtract 1, multiply by 100 for the percentage.",
            ],
            "note": "Always remember: Effective is higher than nominal when m > 1.",
        })
    return out

def gen_analytical_distance(count=200, seed=61):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        x2, y2 = rng.randint(-8, 8), rng.randint(-8, 8)
        if x1 == x2 and y1 == y2:
            continue
        dx, dy = x2 - x1, y2 - y1
        sq = dx * dx + dy * dy
        out.append({
            "problem": f"Find the distance between A({x1}; {y1}) and B({x2}; {y2}).",
            "steps": [
                "Formula: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)",
                f"d = sqrt(({x2} - ({x1}))^2 + ({y2} - ({y1}))^2)",
                f"d = sqrt(({dx})^2 + ({dy})^2)",
                f"d = sqrt({sq})",
                "Leave in surd form unless a decimal is asked.",
            ],
            "note": "Always remember: Brackets around negative coordinates. Method mark for the substitution line.",
        })
    return out


def gen_analytical_gradient(count=200, seed=62):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
        if x1 == x2 or y1 == y2:
            continue
        out.append({
            "problem": f"Find the gradient of the line through A({x1}; {y1}) and B({x2}; {y2}).",
            "steps": [
                "Formula: m = (y2 - y1) / (x2 - x1)",
                f"m = ({y2} - ({y1})) / ({x2} - ({x1}))",
                f"m = {y2 - y1} / {x2 - x1}",
                "Simplify the fraction if possible.",
            ],
            "note": "Always remember: Brackets around negative coordinates. Wrong order flips the sign.",
        })
    return out


def gen_analytical_midpoint(count=50, seed=63):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        x2, y2 = rng.randint(-8, 8), rng.randint(-8, 8)
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        out.append({
            "problem": f"Find the midpoint of A({x1}; {y1}) and B({x2}; {y2}).",
            "steps": [
                "Formula: M = ((x1 + x2)/2 ; (y1 + y2)/2)",
                f"M = (({x1} + {x2})/2 ; ({y1} + {y2})/2)",
                f"Answer:  M({mx}; {my})",
            ],
            "note": "Always remember: Write the formula first. It earns a method mark.",
        })
    return out


def gen_analytical_line_equation(count=200, seed=64):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
        if x1 == x2:
            continue
        out.append({
            "problem": f"Find the equation of the line through A({x1}; {y1}) and B({x2}; {y2}).",
            "steps": [
                f"Gradient: m = ({y2} - ({y1})) / ({x2} - ({x1}))",
                f"Point-gradient form: y - ({y1}) = m(x - ({x1}))",
                "Substitute m and one point.",
                "Simplify to y = mx + c.",
            ],
            "note": "Always remember: Substitute the gradient and one point into y - y1 = m(x - x1).",
        })
    return out


def gen_analytical_circle_equation(count=50, seed=65):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        h = rng.randint(-8, 8)
        k = rng.randint(-8, 8)
        r = rng.randint(2, 8)
        out.append({
            "problem": f"Find the equation of the circle with centre ({h}; {k}) and radius {r}.",
            "steps": [
                "Standard form: (x - h)^2 + (y - k)^2 = r^2",
                f"h = {h}, k = {k}, r = {r}",
                f"Answer:  (x - ({h}))^2 + (y - ({k}))^2 = {r * r}",
                "Expand if the question asks for general form.",
            ],
            "note": "Always remember: The signs inside brackets flip. Centre (-3; 5) gives (x + 3) and (y - 5).",
        })
    return out


def gen_analytical_circle_radius(count=50, seed=66):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        h = rng.randint(-6, 6)
        k = rng.randint(-6, 6)
        r = rng.randint(2, 8)
        out.append({
            "problem": f"A circle has centre ({h}; {k}). A point on it is ({h + r}; {k}). Find the radius.",
            "steps": [
                "Radius = distance from centre to any point on the circle.",
                f"r = sqrt(({h + r} - ({h}))^2 + ({k} - ({k}))^2)",
                f"r = sqrt({r}^2) = {r}",
            ],
            "note": "Always remember: Radius is the distance from centre to any point on the circle.",
        })
    return out


def gen_analytical_tangent_equation(count=50, seed=67):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        h = rng.randint(-6, 6)
        k = rng.randint(-6, 6)
        r = rng.randint(2, 6)
        px, py = h + r, k
        out.append({
            "problem": f"Circle with centre ({h}; {k}) passes through ({px}; {py}). Find the tangent at that point.",
            "steps": [
                f"Gradient of radius: m_radius = ({py} - {k}) / ({px} - {h}) = 0",
                "Tangent is perpendicular to radius: m_tangent x m_radius = -1",
                "Radius is horizontal, so tangent is vertical.",
                f"Answer:  x = {px}",
            ],
            "note": "Always remember: Tangent is perpendicular to radius at point of contact.",
        })
    return out


def gen_analytical_area(count=50, seed=68):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = rng.randint(-6, 6), rng.randint(-6, 6)
        if x1 == x2 or y1 == y2:
            continue
        out.append({
            "problem": f"Find the area of triangle with vertices A(0; 0), B({x1}; {y1}), C({x2}; {y2}).",
            "steps": [
                "Area = 1/2 |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|",
                "Or use 1/2 x base x height if the triangle is right-angled.",
                "Substitute and simplify.",
                "Answer in square units.",
            ],
            "note": "Always remember: Area is always positive. Take the absolute value.",
        })
    return out


def gen_analytical_inclination(count=50, seed=69):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        dx = rng.randint(1, 5)
        dy = rng.randint(1, 8)
        out.append({
            "problem": f"A line has gradient m = {dy}/{dx}. Find its angle of inclination theta.",
            "steps": [
                "Formula: tan(theta) = m",
                f"tan(theta) = {dy}/{dx}",
                f"theta = arctan({dy}/{dx})",
                "Round to two decimals if needed.",
            ],
            "note": "Always remember: Angle of inclination is measured from the positive x-axis, in [0; 180).",
        })
    return out


def gen_trig_reduction(count=50, seed=71):
    rng = random.Random(seed)
    angles = [90, 180, 270, 360, 450, 540]
    funcs = ["sin", "cos", "tan"]
    out = []
    for _ in range(count):
        f = rng.choice(funcs)
        a = rng.choice(angles)
        out.append({
            "problem": f"Simplify {f}({a} - x)",
            "steps": [
                f"Identify the quadrant for {a} - x.",
                "Use the CAST diagram to determine the sign.",
                "Reduce to a ratio of x.",
            ],
            "note": "Always remember: Reduce the angle first, then the function. Match the quadrant.",
        })
    return out


def gen_trig_double_angle(count=50, seed=72):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        out.append({
            "problem": "Given sin(x) = 0.6 and x is acute, find sin(2x).",
            "steps": [
                "Formula: sin(2x) = 2 sin(x) cos(x)",
                "Find cos(x) using sin^2 + cos^2 = 1",
                "cos(x) = sqrt(1 - 0.36) = 0.8 (acute, so positive)",
                "sin(2x) = 2(0.6)(0.8) = 0.96",
            ],
            "note": "Never write sin(2x) = 2 sin(x). Use the double-angle identity.",
        })
    return out


def gen_trig_compound(count=50, seed=73):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        out.append({
            "problem": "Expand sin(A + B).",
            "steps": [
                "Formula: sin(A + B) = sin A cos B + cos A sin B",
                "Identify A and B from the given expression.",
                "Substitute and simplify.",
            ],
            "note": "Always remember: Compound angle formulas: sin(A +/- B), cos(A +/- B). Learn both directions.",
        })
    return out


def gen_trig_equation(count=50, seed=74):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        k = rng.choice([0.5, -0.5, 1, -1, 0])
        out.append({
            "problem": f"Solve sin(x) = {k} for x in [0; 360].",
            "steps": [
                f"Reference angle: sin^-1({abs(k)})",
                "Determine the quadrants where sin has the required sign.",
                "Write both solutions in the given interval.",
            ],
            "note": "Always remember: Sine is positive in Q1 and Q2; negative in Q3 and Q4.",
        })
    return out


def gen_probability_union(count=50, seed=81):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        pa = rng.choice([0.2, 0.3, 0.4, 0.5])
        pb = rng.choice([0.3, 0.4, 0.5, 0.6])
        pab = rng.choice([0.1, 0.15, 0.2])
        out.append({
            "problem": f"P(A) = {pa}, P(B) = {pb}, P(A and B) = {pab}. Find P(A or B).",
            "steps": [
                "Formula: P(A or B) = P(A) + P(B) - P(A and B)",
                f"= {pa} + {pb} - {pab}",
                f"= {pa + pb - pab}",
            ],
            "note": "Always remember: Subtract P(A and B) once. Do not double-count the overlap.",
        })
    return out


def gen_probability_independence(count=50, seed=82):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        pa = rng.choice([0.3, 0.4, 0.5, 0.6])
        pb = rng.choice([0.3, 0.4, 0.5, 0.6])
        prod = pa * pb
        out.append({
            "problem": f"P(A) = {pa}, P(B) = {pb}. Are A and B independent?",
            "steps": [
                "Independent if P(A and B) = P(A) x P(B)",
                f"P(A) x P(B) = {pa} x {pb} = {prod:.4f}",
                "Compare with the given P(A and B).",
                "If equal, independent. If not, not independent.",
            ],
            "note": "Always remember: The test is P(A and B) = P(A) x P(B).",
        })
    return out


def _factorial(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def gen_probability_counting(count=50, seed=83):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.randint(4, 8)
        out.append({
            "problem": f"How many ways can {n} distinct objects be arranged in a row?",
            "steps": [
                f"Number of arrangements = {n}!",
                f"= {_factorial(n)}",
            ],
            "note": "Always remember: n! counts the arrangements. If some objects repeat, divide by the factorial of each repetition.",
        })
    return out


def gen_stats_mean(count=50, seed=91):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        data = [rng.randint(1, 20) for _ in range(rng.randint(5, 8))]
        m = sum(data) / len(data)
        out.append({
            "problem": f"Find the mean of: {data}",
            "steps": [
                f"Sum = {sum(data)}",
                f"Count = {len(data)}",
                f"Mean = {sum(data)} / {len(data)} = {m:.2f}",
            ],
            "note": "Always remember: Mean = sum / count. Round to two decimals if it does not divide evenly.",
        })
    return out


def gen_stats_median(count=50, seed=92):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.choice([5, 7, 9])
        data = sorted([rng.randint(1, 30) for _ in range(n)])
        med = data[n // 2]
        out.append({
            "problem": f"Find the median of: {data}",
            "steps": [
                "Order the data from smallest to largest (already done).",
                f"Position of median = (n + 1)/2 = ({n} + 1)/2 = {(n + 1) // 2}",
                f"Median = {med}",
            ],
            "note": "Always remember: State the position of the median before finding the value.",
        })
    return out


def gen_stats_quartile(count=50, seed=93):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.choice([5, 7, 9])
        data = sorted([rng.randint(1, 40) for _ in range(n)])
        q1 = data[n // 4]
        q3 = data[3 * n // 4]
        out.append({
            "problem": f"Find Q1 and Q3 of: {data}",
            "steps": [
                "Q1 = median of lower half.",
                "Q3 = median of upper half.",
                f"Q1 = {q1}",
                f"Q3 = {q3}",
            ],
            "note": "Always remember: Q1 is the 25th percentile, Q3 the 75th. State the position first.",
        })
    return out


def gen_stats_iqr(count=50, seed=94):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        q1 = rng.randint(3, 15)
        q3 = q1 + rng.randint(4, 20)
        out.append({
            "problem": f"A dataset has Q1 = {q1} and Q3 = {q3}. Find the IQR.",
            "steps": [
                "Formula: IQR = Q3 - Q1",
                f"IQR = {q3} - {q1}",
                f"IQR = {q3 - q1}",
            ],
            "note": "Always remember: IQR is Q3 - Q1, not the range (max - min).",
        })
    return out


# ------------------------------------------------------------------
# Written analogues for proof / interpretive templates.
# These are hand-authored, not generated. ~3-5 per template, enough
# for variety on any given session.
# ------------------------------------------------------------------

WRITTEN_ANALOGUES = {
    "euclidean_written": [
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
    ],
    "trig_written": [
        {
            "problem": "Prove that sin(180 - x) = sin x.",
            "steps": [
                "sin(180 - x) is in the second quadrant.",
                "In Q2, sine is positive.",
                "So sin(180 - x) = sin x.",
            ],
            "note": "Use the CAST diagram to determine the sign. Reduce the angle first.",
        },
        {
            "problem": "Prove that sin 2x = 2 sin x cos x.",
            "steps": [
                "Use the compound angle formula: sin(A + B) = sin A cos B + cos A sin B.",
                "Let A = B = x.",
                "Then sin(2x) = sin x cos x + cos x sin x = 2 sin x cos x.",
            ],
            "note": "Always remember: Double-angle formulas are derived from compound angle formulas.",
        },
    ],
    "trig_graph_written": [
        {
            "problem": "Sketch y = sin x for x in [0; 360]. State the amplitude and period.",
            "steps": [
                "Amplitude = 1 (coefficient of sin).",
                "Period = 360 (standard for sin x).",
                "Key points: (0; 0), (90; 1), (180; 0), (270; -1), (360; 0).",
            ],
            "note": "Always remember: State amplitude and period before drawing. They are often marks on their own.",
        },
        {
            "problem": "Sketch y = 2 cos x. State the range and period.",
            "steps": [
                "Amplitude = 2, so range is [-2; 2].",
                "Period = 360.",
                "Key points: (0; 2), (90; 0), (180; -2), (270; 0), (360; 2).",
            ],
            "note": "Always remember: Amplitude is the multiplier. Range follows directly from amplitude.",
        },
    ],
    "trig_3d_written": [
        {
            "problem": "In triangle ABC, AB = 5 cm, angle A = 30, angle B = 45. Find BC.",
            "steps": [
                "Use sine rule: BC / sin A = AB / sin C.",
                "Find angle C = 180 - 30 - 45 = 105.",
                "BC = 5 sin 30 / sin 105.",
            ],
            "note": "Always remember: Name the rule. Write the formula line before substituting.",
        },
    ],
    "stats_regression_written": [
        {
            "problem": "A least-squares regression line is y = 2.5 + 0.8x. Predict y when x = 10.",
            "steps": [
                "Substitute x = 10 into the equation.",
                "y = 2.5 + 0.8(10) = 2.5 + 8 = 10.5.",
            ],
            "note": "Always remember: Substitute before computing. Show the substitution line.",
        },
        {
            "problem": "Correlation coefficient r = 0.92. Describe the relationship.",
            "steps": [
                "r is close to 1, so there is a strong positive correlation.",
                "Use the words: strong, positive, correlation.",
            ],
            "note": "Always comment on strength AND direction. r close to 1 = strong positive.",
        },
    ],
    "stats_sd_written": [
        {
            "problem": "Data: 4, 6, 8, 10, 12. Find the standard deviation.",
            "steps": [
                "Mean = (4 + 6 + 8 + 10 + 12) / 5 = 8.",
                "Deviations: -4, -2, 0, 2, 4. Squared: 16, 4, 0, 4, 16. Sum = 40.",
                "Variance = 40 / 5 = 8.",
                "Standard deviation = sqrt(8) = 2.83.",
            ],
            "note": "Always remember: Show the mean first, then the deviations, then the variance, then the SD.",
        },
    ],
    "stats_written": [
        {
            "problem": "A box plot has minimum = 5, Q1 = 12, median = 20, Q3 = 28, maximum = 40. Describe the shape.",
            "steps": [
                "IQR = Q3 - Q1 = 28 - 12 = 16.",
                "Median is not in the middle of Q1 and Q3, so the data is skewed.",
                "Longer upper whisker (28 to 40 = 12) than lower (5 to 12 = 7), so skewed right.",
            ],
            "note": "Always remember: Compare the whisker lengths and the position of the median within the box.",
        },
    ],
}



def gen_simultaneous_linear_quadratic(count=50, seed=15):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        p = rng.randint(1, 4)
        q = rng.randint(-5, 5)
        x1 = rng.randint(-4, 4)
        x2 = rng.randint(-4, 4)
        if x1 == x2 or q == 0:
            continue
        y1 = p * x1 + q
        y2 = p * x2 + q
        out.append({
            "problem": f"Solve y = {p}x {q:+d} and y^2 + xy = {y1 * y1 + x1 * y1}",
            "steps": [
                "Substitute y from the linear equation into the second equation.",
                "Expand and collect like terms to get a quadratic in x.",
                "Factorise the quadratic.",
                f"Answer:  x = {x1}, y = {y1}  or  x = {x2}, y = {y2}",
                "Substitute each x back to find the matching y.",
            ],
            "note": "Always substitute, never guess. Show the substitution step on its own line.",
        })
    return out


# ==================================================================
# Re-added generators (git checkout had reverted these)
# ==================================================================

def gen_cubic_concave_v2(count=50, seed=201):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, 2, -1, -2])
        b = rng.randint(-9, 9)
        if b == 0:
            continue
        cv = -2 * b / (6 * a)
        if a > 0:
            interval = f"x < {cv:.2f}"
        else:
            interval = f"x > {cv:.2f}"
        out.append({
            "problem": f"Find where f(x) = {a}x^3 + {b}x^2 is concave down.",
            "steps": [
                f"f'(x) = {3*a}x^2 + {2*b}x",
                f"f''(x) = {6*a}x + {2*b}",
                "Concave down when f''(x) < 0.",
                f"Critical value: x = {cv:.2f}",
                f"Answer: {interval}",
            ],
            "note": "Always remember: concave down means f''(x) < 0.",
        })
    return out


def gen_cubic_increasing_v2(count=50, seed=202):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
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
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line.",
        })
    return out


def gen_cubic_intercept_v2(count=50, seed=203):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        r1, r2, r3 = rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6)
        if r1 == r2 or r1 == r3 or r2 == r3:
            continue
        key = tuple(sorted([r1, r2, r3]))
        if key in seen:
            continue
        seen.add(key)
        terms = []
        for r in (r1, r2, r3):
            if r > 0:
                terms.append(f"(x - {r})")
            elif r < 0:
                terms.append(f"(x + {abs(r)})")
            else:
                terms.append("x")
        expr = "*".join(terms)
        out.append({
            "problem": f"Find the x-intercepts of f(x) = {expr}.",
            "steps": [
                "Set f(x) = 0.",
                f"x = {r1}",
                f"x = {r2}",
                f"x = {r3}",
                f"Answer: ({r1}; 0), ({r2}; 0), ({r3}; 0)",
            ],
            "note": "Always remember: cubic has at most 3 x-intercepts.",
        })
    return out


def gen_probability_conditional_v2(count=50, seed=204):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        pa = rng.choice([0.2, 0.3, 0.4, 0.5, 0.6])
        pab = rng.choice([0.05, 0.1, 0.15, 0.2, 0.25])
        if pab >= pa:
            continue
        out.append({
            "problem": f"P(A) = {pa}, P(A and B) = {pab}. Find P(B | A).",
            "steps": [
                "Formula: P(B | A) = P(A and B) / P(A)",
                f"= {pab} / {pa}",
                f"Answer: {pab/pa:.4f}",
            ],
            "note": "Always remember: divide by the given event.",
        })
    return out


def gen_quadratic_sequence_n_v2(count=50, seed=205):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        b = rng.randint(-8, 8)
        c = rng.randint(-20, 20)
        n_target = rng.randint(3, 15)
        T = n_target * n_target + b * n_target + c
        out.append({
            "problem": f"Quadratic sequence T_n = n^2 {b:+d}n {c:+d}. Find n if T_n = {T}.",
            "steps": [
                f"Set n^2 {b:+d}n {c:+d} = {T}",
                f"n^2 {b:+d}n {c - T:+d} = 0",
                "Factorise.",
                f"Positive integer solution: n = {n_target}",
            ],
            "note": "Always remember: reject non-positive n.",
        })
    return out


def gen_analytical_translation_v2(count=50, seed=206):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        dx, dy = rng.randint(-6, 6), rng.randint(-6, 6)
        if dx == 0 and dy == 0:
            continue
        x2, y2 = x1 + dx, y1 + dy
        out.append({
            "problem": f"Point A({x1}; {y1}) is translated by ({dx}; {dy}). Find A'.",
            "steps": [
                f"x' = {x1} + ({dx}) = {x2}",
                f"y' = {y1} + ({dy}) = {y2}",
                f"Answer: A'({x2}; {y2})",
            ],
            "note": "Always remember: right/up positive, left/down negative.",
        })
    return out


def gen_stats_sd_v2(count=50, seed=207):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.choice([5, 7, 9])
        data = [rng.randint(1, 20) for _ in range(n)]
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / n
        sd = var ** 0.5
        out.append({
            "problem": f"Data: {', '.join(str(x) for x in data)}. Find the standard deviation.",
            "steps": [
                f"Mean = {sum(data)} / {n} = {mean:.2f}",
                "Compute squared deviations.",
                f"Variance = {var:.2f}",
                f"SD = sqrt(variance) = {sd:.2f}",
            ],
            "note": "Always remember: mean, deviations, variance, SD.",
        })
    return out


def gen_stats_regression_predict_v2(count=50, seed=208):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = round(rng.uniform(5, 50), 2)
        b = round(rng.uniform(-3, 3), 2)
        x = rng.randint(5, 50)
        y = round(a + b * x, 2)
        out.append({
            "problem": f"A least-squares regression line is y = {a} + {b}x. Predict y when x = {x}.",
            "steps": [
                f"y = {a} + ({b})({x})",
                f"Answer: y = {y}",
            ],
            "note": "Always remember: substitute before computing.",
        })
    return out



# ==================================================================
# Re-added generators (git checkout had reverted these)
# ==================================================================

def gen_cubic_concave_v2(count=50, seed=201):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = rng.choice([1, 2, -1, -2])
        b = rng.randint(-9, 9)
        if b == 0:
            continue
        cv = -2 * b / (6 * a)
        if a > 0:
            interval = f"x < {cv:.2f}"
        else:
            interval = f"x > {cv:.2f}"
        out.append({
            "problem": f"Find where f(x) = {a}x^3 + {b}x^2 is concave down.",
            "steps": [
                f"f'(x) = {3*a}x^2 + {2*b}x",
                f"f''(x) = {6*a}x + {2*b}",
                "Concave down when f''(x) < 0.",
                f"Critical value: x = {cv:.2f}",
                f"Answer: {interval}",
            ],
            "note": "Always remember: concave down means f''(x) < 0.",
        })
    return out


def gen_cubic_increasing_v2(count=50, seed=202):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 30:
        tries += 1
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
                f"Critical values: x = -{a} and x = {a}",
                f"Answer: x < -{a} or x > {a}",
            ],
            "note": "Always remember: increasing means f'(x) > 0. Use a sign line.",
        })
    return out


def gen_cubic_intercept_v2(count=50, seed=203):
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 10:
        tries += 1
        r1, r2, r3 = rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6)
        if r1 == r2 or r1 == r3 or r2 == r3:
            continue
        key = tuple(sorted([r1, r2, r3]))
        if key in seen:
            continue
        seen.add(key)
        terms = []
        for r in (r1, r2, r3):
            if r > 0:
                terms.append(f"(x - {r})")
            elif r < 0:
                terms.append(f"(x + {abs(r)})")
            else:
                terms.append("x")
        expr = "*".join(terms)
        out.append({
            "problem": f"Find the x-intercepts of f(x) = {expr}.",
            "steps": [
                "Set f(x) = 0.",
                f"x = {r1}",
                f"x = {r2}",
                f"x = {r3}",
                f"Answer: ({r1}; 0), ({r2}; 0), ({r3}; 0)",
            ],
            "note": "Always remember: cubic has at most 3 x-intercepts.",
        })
    return out


def gen_probability_conditional_v2(count=50, seed=204):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        pa = rng.choice([0.2, 0.3, 0.4, 0.5, 0.6])
        pab = rng.choice([0.05, 0.1, 0.15, 0.2, 0.25])
        if pab >= pa:
            continue
        out.append({
            "problem": f"P(A) = {pa}, P(A and B) = {pab}. Find P(B | A).",
            "steps": [
                "Formula: P(B | A) = P(A and B) / P(A)",
                f"= {pab} / {pa}",
                f"Answer: {pab/pa:.4f}",
            ],
            "note": "Always remember: divide by the given event.",
        })
    return out


def gen_quadratic_sequence_n_v2(count=50, seed=205):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        b = rng.randint(-8, 8)
        c = rng.randint(-20, 20)
        n_target = rng.randint(3, 15)
        T = n_target * n_target + b * n_target + c
        out.append({
            "problem": f"Quadratic sequence T_n = n^2 {b:+d}n {c:+d}. Find n if T_n = {T}.",
            "steps": [
                f"Set n^2 {b:+d}n {c:+d} = {T}",
                f"n^2 {b:+d}n {c - T:+d} = 0",
                "Factorise.",
                f"Positive integer solution: n = {n_target}",
            ],
            "note": "Always remember: reject non-positive n.",
        })
    return out


def gen_analytical_translation_v2(count=50, seed=206):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        dx, dy = rng.randint(-6, 6), rng.randint(-6, 6)
        if dx == 0 and dy == 0:
            continue
        x2, y2 = x1 + dx, y1 + dy
        out.append({
            "problem": f"Point A({x1}; {y1}) is translated by ({dx}; {dy}). Find A'.",
            "steps": [
                f"x' = {x1} + ({dx}) = {x2}",
                f"y' = {y1} + ({dy}) = {y2}",
                f"Answer: A'({x2}; {y2})",
            ],
            "note": "Always remember: right/up positive, left/down negative.",
        })
    return out


def gen_stats_sd_v2(count=50, seed=207):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.choice([5, 7, 9])
        data = [rng.randint(1, 20) for _ in range(n)]
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / n
        sd = var ** 0.5
        out.append({
            "problem": f"Data: {', '.join(str(x) for x in data)}. Find the standard deviation.",
            "steps": [
                f"Mean = {sum(data)} / {n} = {mean:.2f}",
                "Compute squared deviations.",
                f"Variance = {var:.2f}",
                f"SD = sqrt(variance) = {sd:.2f}",
            ],
            "note": "Always remember: mean, deviations, variance, SD.",
        })
    return out


def gen_stats_regression_predict_v2(count=50, seed=208):
    import random
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        a = round(rng.uniform(5, 50), 2)
        b = round(rng.uniform(-3, 3), 2)
        x = rng.randint(5, 50)
        y = round(a + b * x, 2)
        out.append({
            "problem": f"A least-squares regression line is y = {a} + {b}x. Predict y when x = {x}.",
            "steps": [
                f"y = {a} + ({b})({x})",
                f"Answer: y = {y}",
            ],
            "note": "Always remember: substitute before computing.",
        })
    return out




def gen_quadratic_standard_factorable(count=50, seed=101):
    """x^2 + bx + c = 0 with integer roots."""
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        r1 = rng.randint(-9, 9)
        r2 = rng.randint(-9, 9)
        if r1 == 0 or r2 == 0 or r1 == r2:
            continue
        key = tuple(sorted((r1, r2)))
        if key in seen:
            continue
        seen.add(key)
        b = -(r1 + r2)
        c = r1 * r2
        parts = ["x^2"]
        if b != 0:
            if b == 1:
                parts.append("+ x")
            elif b == -1:
                parts.append("- x")
            else:
                parts.append(f"{b:+d}x")
        if c != 0:
            parts.append(f"{c:+d}")
        expr = " ".join(parts)
        out.append({
            "problem": f"Solve {expr} = 0",
            "steps": [
                f"Standard form: {expr} = 0",
                f"Find two numbers that multiply to {c} and add to {b}.",
                f"That gives (x - ({r1}))(x - ({r2})) = 0",
                f"x = {r1}",
                f"x = {r2}",
                f"Answer: x = {r1} or x = {r2}",
            ],
            "note": "Always remember: b = -(sum of roots) and c = (product of roots).",
        })
    return out


def gen_quadratic_formula(count=50, seed=102):
    """ax^2 + bx + c = 0 with a > 1 — needs the formula."""
    import random
    rng = random.Random(seed)
    out, seen = [], set()
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        a = rng.choice([2, 3, 4, 5])
        b = rng.randint(-9, 9)
        c = rng.randint(-9, 9)
        if b == 0 or c == 0:
            continue
        disc = b * b - 4 * a * c
        if disc <= 0 or int(disc ** 0.5) ** 2 == disc:
            continue
        key = (a, b, c)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "problem": f"Solve {a}x^2 {b:+d}x {c:+d} = 0 (correct to TWO decimal places)",
            "steps": [
                f"Standard form: {a}x^2 {b:+d}x {c:+d} = 0",
                "Formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a",
                f"Substitute: a = {a}, b = {b}, c = {c}",
                f"Discriminant: b^2 - 4ac = {disc}",
                "Keep full accuracy until the final two-decimal answer.",
            ],
            "note": "Always remember: write the formula, then substitute, then compute. Brackets around every negative.",
        })
    return out


TEMPLATES = {
    "quadratic_factored":            (gen_quadratic_factored, 200),
    "quadratic_inequality":          (gen_quadratic_inequality, 50),
    "exponential_quadratic":         (gen_exponential_quadratic, 50),
    "ap_term":                       (gen_ap_term, 200),
    "ap_sum":                        (gen_ap_sum, 200),
    "gp_term":                       (gen_gp_term, 200),
    "gp_ratio":                      (gen_gp_ratio, 50),
    "gp_sum":                        (gen_gp_sum, 50),
    "gp_infinite":                   (gen_gp_infinite, 50),
    "quadratic_sequence_general":    (gen_quadratic_sequence_general, 50),
    "quadratic_sequence_term":       (gen_quadratic_sequence_term, 50),
    "derivative_rules":              (gen_derivative_rules, 200),
    "derivative_first_principles":   (gen_derivative_first_principles, 50),
    "calculus_tangent":              (gen_calculus_tangent, 50),
    "cubic_turning":                 (gen_cubic_turning, 50),
    "parabola_turning":              (gen_parabola_turning, 200),
    "parabola_range":                (gen_parabola_range, 50),
    "parabola_intercept":            (gen_parabola_intercept, 50),
    "parabola_equation":             (gen_parabola_equation, 50),
    "hyperbola_domain":              (gen_hyperbola_domain, 50),
    "hyperbola_equation":            (gen_hyperbola_equation, 50),
    "line_equation":                 (gen_line_equation, 50),
    "exponential_value":             (gen_exponential_value, 50),
    "finance_compound":              (gen_finance_compound, 200),
    "finance_simple":                (gen_finance_simple, 50),
    "finance_annuity_future":        (gen_finance_annuity_future, 50),
    "finance_loan_n":                (gen_finance_loan_n, 50),
    "finance_effective":             (gen_finance_effective, 50),
    "analytical_distance":           (gen_analytical_distance, 200),
    "analytical_gradient":           (gen_analytical_gradient, 200),
    "analytical_midpoint":           (gen_analytical_midpoint, 50),
    "analytical_line_equation":      (gen_analytical_line_equation, 200),
    "analytical_circle_equation":    (gen_analytical_circle_equation, 50),
    "analytical_circle_radius":      (gen_analytical_circle_radius, 50),
    "analytical_tangent_equation":   (gen_analytical_tangent_equation, 50),
    "analytical_area":               (gen_analytical_area, 50),
    "analytical_inclination":        (gen_analytical_inclination, 50),
    "trig_reduction":                (gen_trig_reduction, 50),
    "trig_double_angle":             (gen_trig_double_angle, 50),
    "trig_compound":                 (gen_trig_compound, 50),
    "trig_equation":                 (gen_trig_equation, 50),
    "probability_union":             (gen_probability_union, 50),
    "probability_independence":      (gen_probability_independence, 50),
    "probability_counting":          (gen_probability_counting, 50),
    "stats_mean":                    (gen_stats_mean, 50),
    "stats_median":                  (gen_stats_median, 50),
    "stats_quartile":                (gen_stats_quartile, 50),
    "stats_iqr":                     (gen_stats_iqr, 50),
    "cubic_concave":                 (gen_cubic_concave_v2, 50),
    "cubic_increasing":              (gen_cubic_increasing_v2, 50),
    "cubic_intercept":               (gen_cubic_intercept_v2, 50),
    "probability_conditional":       (gen_probability_conditional_v2, 50),
    "quadratic_sequence_n":          (gen_quadratic_sequence_n_v2, 50),
    "analytical_translation":        (gen_analytical_translation_v2, 50),
    "stats_sd_written":              (gen_stats_sd_v2, 50),
    "stats_regression_written":      (gen_stats_regression_predict_v2, 50),
    "quadratic_standard_factorable": (gen_quadratic_standard_factorable, 50),
    "quadratic_formula":             (gen_quadratic_formula, 50),
}


def generate_all(verbose=False):
    # Ensure the simultaneous generator is registered even if TEMPLATES
    # was authored before it existed.
    if "simultaneous_linear_quadratic" not in TEMPLATES:
        TEMPLATES["simultaneous_linear_quadratic"] = (gen_simultaneous_linear_quadratic, 50)

    """Return dict template_id -> list of analogues."""
    pool = {}
    for tid, (fn, count) in TEMPLATES.items():
        pool[tid] = fn(count=count)
        if verbose:
            print(f"  {tid}: {len(pool[tid])} variants")
    # Merge written analogues (add to generated, do not overwrite)
    for tid, entries in WRITTEN_ANALOGUES.items():
        if tid in pool and pool[tid]:
            existing = {a.get("problem", "") for a in pool[tid]}
            extra = [e for e in entries if e.get("problem", "") not in existing]
            pool[tid] = list(pool[tid]) + extra
        else:
            pool[tid] = list(entries)
        if verbose:
            print(f"  {tid}: {len(pool[tid])} total ({len(entries)} written merged)")
    try:
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
        pass
    return pool


EXTRA_WRITTEN_ANALOGUES = {
    "analytical_translation": [
        {
            "problem": "Point A(2; 3) is translated 4 units right and 2 units down. Find A'.",
            "steps": [
                "Right adds to x. Down subtracts from y.",
                "x' = 2 + 4 = 6",
                "y' = 3 - 2 = 1",
                "Answer:  A'(6; 1)",
            ],
            "note": "Always remember: Right and up are positive; left and down are negative.",
        },
        {
            "problem": "A(-1; 5) is translated to A'(3; 1). Describe the translation.",
            "steps": [
                "x-shift: 3 - (-1) = 4 units right.",
                "y-shift: 1 - 5 = -4, so 4 units down.",
                "Answer:  4 units right and 4 units down.",
            ],
            "note": "Always remember: Describe as: x units right/left, then y units up/down.",
        },
    ],
    "cubic_concave": [
        {
            "problem": "Find where f(x) = x^3 - 3x^2 is concave down.",
            "steps": [
                "f'(x) = 3x^2 - 6x",
                "f''(x) = 6x - 6",
                "Concave down when f''(x) < 0:  6x - 6 < 0  =>  x < 1",
            ],
            "note": "Always remember: Concave down means f''(x) < 0.",
        },
    ],
    "cubic_increasing": [
        {
            "problem": "Find where f(x) = x^3 - 3x is increasing.",
            "steps": [
                "f'(x) = 3x^2 - 3",
                "Increasing when f'(x) > 0:  x^2 > 1",
                "Critical values: x = -1 and x = 1",
                "Answer:  x < -1 or x > 1",
            ],
            "note": "Always remember: Increasing means f'(x) > 0.",
        },
    ],
    "cubic_intercept": [
        {
            "problem": "Find the x-intercepts of f(x) = (x - 2)(x + 3)(x - 1).",
            "steps": [
                "Set f(x) = 0. Each factor gives one root.",
                "x = 2, x = -3, x = 1",
                "Answer:  (2; 0), (-3; 0), (1; 0)",
            ],
            "note": "Always remember: Cubic has at most 3 x-intercepts.",
        },
    ],
    "probability_conditional": [
        {
            "problem": "P(A) = 0.4, P(A and B) = 0.15. Find P(B | A).",
            "steps": [
                "Formula: P(B | A) = P(A and B) / P(A)",
                "= 0.15 / 0.4 = 0.375",
            ],
            "note": "Always remember: Conditional probability divides by the given event.",
        },
    ],
    "quadratic_sequence_n": [
        {
            "problem": "Quadratic sequence T_n = n^2 + 3n - 1. Find n if T_n = 69.",
            "steps": [
                "n^2 + 3n - 1 = 69",
                "n^2 + 3n - 70 = 0",
                "(n + 10)(n - 7) = 0",
                "Reject n = -10.  Answer:  n = 7",
            ],
            "note": "Always remember: Reject non-positive n.",
        },
    ],

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
}


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

