"""
Scenario generators — composed DBE-style questions.

Each generator produces whole questions with:
  - A rendered DBE-style diagram (PNG)
  - 4-6 sub-questions, each with prompt, expected answer, MEMO STEPS,
    marks, and skill_id

Currently available:
  - gen_scenario_hyperbola_line   — f = a/(x-p) + q meets a straight line
  - gen_scenario_parabola_line    — f = a(x-p)^2 + q meets a straight line

Patterns for future scenarios:
  - gen_scenario_exponential_line (2020 P1 Q5 shape)
  - gen_scenario_cubic            (2020 P1 Q8 shape)
"""
from __future__ import annotations
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
DIAGRAM_DIR = ROOT / "data" / "processed" / "tutor" / "scenario_diagrams"


# ============================================================
# Number formatting helpers
# ============================================================

def _factor_from_root(r):
    """Given a root r, return the factor string:
       r = 3  -> '(x - 3)'
       r = -1 -> '(x + 1)'
       r = 0  -> '(x)'
    """
    if r == 0:
        return "(x)"
    if r > 0:
        return f"(x - {r})"
    return f"(x + {abs(r)})"


def _factor_display(root, value_at_root):
    """Show the substitution: 'x - (-1)' style cleaned.
       Useful for evaluating (0 - r) in memo steps.
    """
    if root == 0:
        return f"({value_at_root})"
    return f"({value_at_root} {'+' if root < 0 else '-'} {abs(root)})"


def _fnum(v):
    """Format a number: 'int' if integer, else trimmed float."""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, int):
        return str(v)
    return str(v)


def _signed_term(coefficient, variable=""):
    """Return '+ 3x' or '- 4' style string (without leading sign if negative
    handled by caller). Always returns with a sign so concatenation reads
    cleanly: 'f(x) = 2/(x) + 3' or 'f(x) = 2/(x) - 5'."""
    if coefficient == 0:
        return ""
    sign = "+" if coefficient > 0 else "-"
    mag = abs(coefficient)
    if variable:
        if mag == 1:
            return f"{sign} {variable}"
        return f"{sign} {mag}{variable}"
    return f"{sign} {mag}"


def _poly_display(m, c):
    """Return '2x + 3' or '-x - 5' style string for mx + c."""
    if m == 0:
        return f"{c}"
    if m == 1:
        head = "x"
    elif m == -1:
        head = "-x"
    else:
        head = f"{m}x"
    if c == 0:
        return head
    return f"{head} {_signed_term(c)}"


# ============================================================
# DBE plane setup and drawing primitives
# ============================================================

def _setup_plane(lim):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=110)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    ax.annotate("", xy=(lim, 0), xytext=(-lim, 0),
                arrowprops=dict(arrowstyle="-|>", color="black",
                                lw=1.1, mutation_scale=12))
    ax.annotate("", xy=(0, lim), xytext=(0, -lim),
                arrowprops=dict(arrowstyle="-|>", color="black",
                                lw=1.1, mutation_scale=12))

    ax.text(lim - 0.35, -0.65, "x", fontsize=13, fontstyle="italic",
            ha="center", va="top")
    ax.text(0.55, lim - 0.35, "y", fontsize=13, fontstyle="italic",
            ha="left", va="top")
    ax.text(-0.35, -0.5, "O", fontsize=11, ha="right", va="top")
    return fig, ax


def _draw_axes_ticks(ax, x_ticks, y_ticks):
    for xv in x_ticks:
        if xv == 0:
            continue
        ax.plot([xv, xv], [-0.13, 0.13], color="black", lw=0.9)
        ax.text(xv, -0.35, _fnum(xv), fontsize=10, ha="center", va="top")
    for yv in y_ticks:
        if yv == 0:
            continue
        ax.plot([-0.13, 0.13], [yv, yv], color="black", lw=0.9)
        ax.text(-0.35, yv, _fnum(yv), fontsize=10, ha="right", va="center")


def _draw_hyperbola(ax, a, p, q, lim, label=None):
    import numpy as np
    eps = 0.06
    step = 0.02
    xs_left = np.arange(-lim, p - eps, step)
    ys_left = a / (xs_left - p) + q
    m_l = (ys_left >= -lim) & (ys_left <= lim)
    if m_l.any():
        ax.plot(xs_left[m_l], ys_left[m_l], color="black", lw=1.5, zorder=3)
    xs_right = np.arange(p + eps, lim, step)
    ys_right = a / (xs_right - p) + q
    m_r = (ys_right >= -lim) & (ys_right <= lim)
    if m_r.any():
        ax.plot(xs_right[m_r], ys_right[m_r], color="black", lw=1.5, zorder=3)
    if label:
        probe_x = (p + lim) / 2 if p < 0 else (p - lim) / 2
        probe_y = a / (probe_x - p) + q
        if abs(probe_y) < lim - 1:
            ax.text(probe_x, probe_y + 0.6, label, fontsize=14,
                    fontstyle="italic", ha="center", va="bottom")


def _draw_parabola(ax, a, p, q, lim, label=None):
    import numpy as np
    xs = np.linspace(-lim, lim, 700)
    ys = a * (xs - p) ** 2 + q
    mask = (ys >= -lim) & (ys <= lim)
    ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)
    if label:
        # Place label on the branch side away from the vertex
        for probe_x in (p + 3, p - 3):
            if abs(probe_x) >= lim - 0.5:
                continue
            probe_y = a * (probe_x - p) ** 2 + q
            if abs(probe_y) < lim - 1:
                ax.text(probe_x + (0.4 if probe_x > p else -0.4),
                        probe_y + 0.6, label,
                        fontsize=14, fontstyle="italic",
                        ha="left" if probe_x > p else "right", va="bottom")
                break


def _draw_line(ax, m, c, lim, label=None):
    if m == 0:
        x0, x1 = -lim, lim
        y0 = y1 = c
    else:
        x0, x1 = -lim, lim
        y0, y1 = m * x0 + c, m * x1 + c
        if y0 < -lim:
            x0 = (-lim - c) / m
            y0 = -lim
        if y0 > lim:
            x0 = (lim - c) / m
            y0 = lim
        if y1 < -lim:
            x1 = (-lim - c) / m
            y1 = -lim
        if y1 > lim:
            x1 = (lim - c) / m
            y1 = lim
    ax.plot([x0, x1], [y0, y1], color="black", lw=1.3, zorder=2)
    if m != 0:
        ax.annotate("",
                    xy=(x1, y1),
                    xytext=(x0 + 0.75 * (x1 - x0), y0 + 0.75 * (y1 - y0)),
                    arrowprops=dict(arrowstyle="-|>", color="black",
                                    lw=1.3, mutation_scale=11))
    if label:
        for px in (0.7 * lim, -0.7 * lim):
            py = m * px + c
            if abs(py) < lim - 1:
                ax.text(px + (0.4 if px > 0 else -0.4), py + 0.4, label,
                        fontsize=14, fontstyle="italic",
                        ha="left" if px > 0 else "right")
                break


def _draw_vertical_asymptote(ax, p, lim):
    ax.plot([p, p], [-lim, lim], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)


def _draw_horizontal_asymptote(ax, q, lim):
    ax.plot([-lim, lim], [q, q], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)


def _draw_point(ax, x, y, label=None, show_coords=False, offset="auto"):
    ax.plot(x, y, "o", color="black", markersize=4, zorder=5)
    if label is None:
        return
    txt = f"{label}({_fnum(x)}; {_fnum(y)})" if show_coords else label
    dx, dy, ha, va = 0.35, 0.55, "left", "bottom"
    if offset == "up-left":
        dx, dy, ha, va = -0.35, 0.55, "right", "bottom"
    elif offset == "down-right":
        dx, dy, ha, va = 0.35, -0.55, "left", "top"
    elif offset == "down-left":
        dx, dy, ha, va = -0.35, -0.55, "right", "top"
    ax.text(x + dx, y + dy, txt, fontsize=11, ha=ha, va=va)


# ============================================================
# Hyperbola + line scenario
# ============================================================

def _try_hyperbola_params(rng):
    p = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    q = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    m = rng.choice([-2, -1, 1, 2])
    cands = [x for x in range(-6, 7) if x != p]
    x1 = rng.choice(cands)
    x2_cands = [x for x in cands if abs(x - x1) >= 2]
    if not x2_cands:
        return None
    x2 = rng.choice(x2_cands)
    if (x1 - p) * (x2 - p) <= 0:
        return None
    a = m * (x1 - p) * (p - x2)
    if a == 0 or abs(a) > 12 or abs(a) not in (2, 4, 6, 8, 10, 12):
        return None
    c = q + m * (p - (x1 + x2))
    if abs(c) > 10:
        return None
    y1 = a / (x1 - p) + q
    y2 = a / (x2 - p) + q
    if y1 != int(y1) or y2 != int(y2):
        return None
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    return a, p, q, m, c, x1, x2, y1, y2


def _solve_inequality_hyperbola(a, p, q, m, c, x1, x2):
    def sgn(x):
        v = a / (x - p) + q - (m * x + c)
        return 1 if v > 0 else (-1 if v < 0 else 0)
    pts = sorted([x1, p, x2])
    probes = [
        (sgn(pts[0] - 5), f"x < {_fnum(pts[0])}"),
        (sgn((pts[0] + pts[1]) / 2), f"{_fnum(pts[0])} < x < {_fnum(pts[1])}"),
        (sgn((pts[1] + pts[2]) / 2), f"{_fnum(pts[1])} < x < {_fnum(pts[2])}"),
        (sgn(pts[2] + 5), f"x > {_fnum(pts[2])}"),
    ]
    parts = [label for sign, label in probes if sign > 0]
    return " or ".join(parts) if parts else "(no solution)"


def _render_hyperbola_line(a, p, q, m, c, x1, x2, y1, y2, sig):
    import numpy as np
    import matplotlib.pyplot as plt
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    path = DIAGRAM_DIR / f"{sig}.png"
    key_vals = [p, q, x1, x2, y1, y2, 0]
    span = max(abs(v) for v in key_vals) + 3
    lim = int(np.ceil(span / 2) * 2)
    lim = max(lim, 6)
    fig, ax = _setup_plane(lim)
    _draw_vertical_asymptote(ax, p, lim)
    _draw_horizontal_asymptote(ax, q, lim)
    _draw_hyperbola(ax, a, p, q, lim, label="f")
    _draw_line(ax, m, c, lim, label="g")
    _draw_axes_ticks(ax,
                     x_ticks=sorted(set([x1, x2])),
                     y_ticks=sorted(set([y1, y2])))
    _draw_point(ax, x1, y1, label="A", show_coords=False,
                offset="up-left" if m >= 0 else "down-left")
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return path


def gen_scenario_hyperbola_line(count=10, seed=101, render=True):
    rng = random.Random(seed)
    out = []
    attempts = 0
    while len(out) < count and attempts < 20000:
        attempts += 1
        params = _try_hyperbola_params(rng)
        if params is None:
            continue
        a, p, q, m, c, x1, x2, y1, y2 = params
        sig = f"hb_{a}_{p}_{q}_{m}_{c}_{x1}_{x2}"
        dpath = None
        if render:
            try:
                dpath = str(_render_hyperbola_line(
                    a, p, q, m, c, x1, x2, y1, y2, sig))
            except Exception:
                dpath = None

        f_eq_str = (f"f(x) = {a}/(x - ({p}))"
                    + (" " + _signed_term(q) if q != 0 else ""))
        g_eq_str = _poly_display(m, c)
        problem = (
            f"The diagram shows the graph of f(x) = a/(x - p) + q and the "
            f"straight line g(x) = mx + c. "
            f"The graphs intersect at A({x1}; {_fnum(y1)}) and at B. "
            f"The asymptotes of f are x = {p} and y = {q}."
        )
        answer_13 = _solve_inequality_hyperbola(a, p, q, m, c, x1, x2)
        axis_ans = "y = -x" + (" " + _signed_term(p + q) if p + q != 0 else "")

        subs = [
            {"n": "1.1",
             "prompt": "Write down the domain of f.",
             "expected": f"x in R, x != {p}",
             "steps": [
                 "The denominator of f cannot be zero.",
                 f"Set x - ({p}) = 0, giving x = {p}.",
                 f"Domain: x in R, x != {p}.",
             ],
             "marks": 1,
             "skill_id": "functions.hyperbola.domain"},
            {"n": "1.2",
             "prompt": "Determine the equation of f in the form "
                       "f(x) = a/(x - p) + q.",
             "expected": f_eq_str,
             "steps": [
                 f"The asymptotes give p = {p} and q = {q} directly.",
                 f"So f(x) = a/(x - ({p}))"
                 + (" " + _signed_term(q) if q != 0 else "") + ".",
                 f"Substitute A({x1}; {_fnum(y1)}): "
                 f"{_fnum(y1)} = a/({x1} - ({p}))"
                 + (" " + _signed_term(q) if q != 0 else ""),
                 f"Solve for a: a = {a}.",
                 f"Therefore {f_eq_str}.",
             ],
             "marks": 4,
             "skill_id": "functions.hyperbola.equation"},
            {"n": "1.3",
             "prompt": "Calculate the coordinates of B.",
             "expected": f"B({x2}; {_fnum(y2)})",
             "steps": [
                 f"Set f(x) = g(x) to find the intersections.",
                 f"{a}/(x - ({p}))"
                 + (" " + _signed_term(q) if q != 0 else "")
                 + f" = {g_eq_str}",
                 f"Multiply through by (x - ({p})) and simplify to a quadratic.",
                 f"The two roots are x = {x1} (point A) and x = {x2}.",
                 f"Substitute x = {x2} into g: "
                 f"y = {_fnum(y2)}.",
                 f"B({x2}; {_fnum(y2)}).",
             ],
             "marks": 4,
             "skill_id": "functions.hyperbola.intersection"},
            {"n": "1.4",
             "prompt": "For which values of x is f(x) > g(x)?",
             "expected": answer_13,
             "steps": [
                 f"Critical values: the two intersections (x = {x1}, "
                 f"x = {x2}) and the vertical asymptote x = {p}.",
                 "Consider the sign of f(x) - g(x) on each interval.",
                 f"From the sketch: f(x) > g(x) for {answer_13}.",
             ],
             "marks": 2,
             "skill_id": "functions.hyperbola.inequality"},
            {"n": "1.5",
             "prompt": "Write down the equation of the axis of symmetry of f "
                       "with a negative gradient.",
             "expected": axis_ans,
             "steps": [
                 f"The axes of symmetry pass through the point of "
                 f"intersection of the asymptotes: ({p}; {q}).",
                 "They have gradients +1 and -1.",
                 f"Negative gradient line: y = -x + c where c = p + q = "
                 f"{p + q}.",
                 axis_ans + ".",
             ],
             "marks": 2,
             "skill_id": "functions.hyperbola.axis_symmetry"},
        ]
        out.append({
            "scenario": "hyperbola_line",
            "skill_id": "functions.hyperbola",
            "problem": problem,
            "diagram_path": dpath,
            "subquestions": subs,
            "total_marks": sum(s["marks"] for s in subs),
            "parameters": {"a": a, "p": p, "q": q, "m": m, "c": c,
                           "x1": x1, "x2": x2, "y1": y1, "y2": y2},
        })
    return out


# ============================================================
# Parabola + line scenario (NEW)
# ============================================================

def _try_parabola_params_tp(rng):
    """Shape A: turning point + one extra point given."""
    a = rng.choice([-2, -1, -1, 1, 1, 2])
    p = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    q = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    # A point on f, distinct from the turning point
    xtry = [x for x in range(-6, 7) if x != p]
    rng.shuffle(xtry)
    for x_a in xtry:
        y_a = a * (x_a - p) ** 2 + q
        if abs(y_a) > 12 or (x_a == 0 and y_a == q):
            continue
        return a, p, q, x_a, y_a
    return None


def _try_parabola_params_roots(rng):
    """Shape B: two x-intercepts + y-intercept given."""
    # Roots r1 < 0 < r2 gives a nice shape
    r1 = rng.choice([-5, -4, -3, -2, -1])
    r2 = rng.choice([1, 2, 3, 4, 5])
    # a must give integer y-intercept and moderate curvature
    for a in rng.sample([-2, -1, 1, 2, -3, 3], 6):
        c = a * r1 * r2
        if abs(c) <= 12 and c != 0:
            return a, r1, r2, c
    return None


def _render_parabola_shape(shape, a, p, q, r1, r2, lim_extra=3):
    import numpy as np
    import matplotlib.pyplot as plt
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)

    if shape == "turning_point":
        sig = f"ptp_{a}_{p}_{q}_{p}_{q}"
        key_vals = [p, q, 0]
    else:
        sig = f"prt_{a}_{r1}_{r2}"
        key_vals = [r1, r2, 0]

    span = max(abs(v) for v in key_vals) + 4
    lim = int(np.ceil(span / 2) * 2)
    lim = max(lim, 7)

    fig, ax = _setup_plane(lim)

    if shape == "turning_point":
        _draw_parabola(ax, a, p, q, lim, label="f")
        # Label turning point B and given point A
        _draw_point(ax, p, q, label="B", show_coords=False,
                    offset="down-right" if a > 0 else "up-right")
        # A is the extra point on f
        # (we need x_a, y_a — passed via closure? no, we redraw only if needed)
        return fig, ax, sig
    else:
        # Factored form: f(x) = a(x - r1)(x - r2)
        # Expand: a x^2 - a(r1+r2) x + a r1 r2
        # Turning point x = (r1+r2)/2, y = a*((r1+r2)/2 - r1)((r1+r2)/2 - r2)
        p_mid = (r1 + r2) / 2
        q_tp = a * (p_mid - r1) * (p_mid - r2)
        _draw_parabola(ax, a, p_mid, q_tp, lim, label="f")
        _draw_point(ax, r1, 0, label="", show_coords=False)
        _draw_point(ax, r2, 0, label="", show_coords=False)
        _draw_point(ax, 0, a * r1 * r2, label="", show_coords=False)
        return fig, ax, sig


def _solve_inequality_parabola(a, x1, x2):
    if a > 0:
        return f"x < {x1} or x > {x2}"
    return f"{x1} < x < {x2}"


def gen_scenario_parabola(count=10, seed=201, shape="turning_point", render=True):
    """DBE-style parabola questions in one of two shapes.

    Shape 'turning_point':
        Given f(x) = a(x-p)^2 + q with turning point B(p; q) and
        a further point A on f.
        Learner finds a, converts to standard form, then answers
        range/inequality.

    Shape 'two_roots':
        Given that f cuts the x-axis at (r1; 0) and (r2; 0), and the
        y-intercept (0; c).
        Learner writes factored form, finds a, expands to standard
        form, finds turning point, then answers range/inequality.
    """
    rng = random.Random(seed)
    out = []
    attempts = 0
    max_attempts = 40000

    while len(out) < count and attempts < max_attempts:
        attempts += 1

        if shape == "turning_point":
            params = _try_parabola_params_tp(rng)
            if params is None:
                continue
            a, p, q, x_a, y_a = params

            sig = f"ptp_{a}_{p}_{q}_{x_a}"
            dpath = None
            if render:
                try:
                    import numpy as np
                    import matplotlib.pyplot as plt
                    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
                    fpath = DIAGRAM_DIR / f"{sig}.png"
                    key_vals = [p, q, x_a, y_a, 0]
                    span = max(abs(v) for v in key_vals) + 4
                    lim = max(int(np.ceil(span / 2) * 2), 7)
                    fig, ax = _setup_plane(lim)
                    _draw_parabola(ax, a, p, q, lim, label="f")
                    _draw_point(ax, p, q, label="B", show_coords=True,
                                offset="down-right" if a > 0 else "up-right")
                    _draw_point(ax, x_a, y_a, label="A", show_coords=True,
                                offset="down-right" if a > 0 else "up-left")
                    fig.tight_layout(pad=0.2)
                    fig.savefig(fpath, dpi=110, bbox_inches="tight",
                                facecolor="white", edgecolor="none")
                    plt.close(fig)
                    dpath = str(fpath)
                except Exception:
                    dpath = None

            inner = f"(x - {p})" if p > 0 else f"(x + {abs(p)})"
            tp_form = f"f(x) = a{inner}^2" + (" " + _signed_term(q) if q != 0 else "")
            b_coef = -2 * a * p
            c_coef = a * p * p + q
            std_form_parts = [f"{a if a != 1 else ''}x^2" if a != 1 else "x^2"]
            if b_coef != 0:
                std_form_parts.append(_signed_term(b_coef, "x"))
            if c_coef != 0:
                std_form_parts.append(_signed_term(c_coef))
            std_form = "f(x) = " + " ".join(std_form_parts).strip()

            range_op = ">=" if a > 0 else "<="
            problem = (
                f"The diagram shows the graph of a parabola f. "
                f"The turning point of f is B({p}; {q}) and A({x_a}; {_fnum(y_a)}) "
                f"is a point on f."
            )

            subs = [
                {"n": "1.1",
                 "prompt": "Write down the equation of f in the form "
                           "f(x) = a(x - p)^2 + q, showing the values of p and q.",
                 "expected": f"p = {p}, q = {q}",
                 "steps": [
                     f"The turning point is ({p}; {q}).",
                     f"For f(x) = a(x - p)^2 + q, the turning point is (p; q).",
                     f"Therefore p = {p} and q = {q}.",
                 ],
                 "marks": 2,
                 "skill_id": "functions.parabola.parameter"},
                {"n": "1.2",
                 "prompt": "Calculate the value of a.",
                 "expected": f"a = {a}",
                 "steps": [
                     f"Substitute A({x_a}; {_fnum(y_a)}) into "
                     f"f(x) = a{_factor_from_root(p)}^2"
                     + (" " + _signed_term(q) if q != 0 else ""),
                     f"{_fnum(y_a)} = a{_factor_display(p, _fnum(x_a))}^2"
                     + (" " + _signed_term(q) if q != 0 else ""),
                     f"{_fnum(y_a - q)} = a({(x_a - p)**2})",
                     f"a = {a}",
                 ],
                 "marks": 3,
                 "skill_id": "functions.parabola.parameter"},
                {"n": "1.3",
                 "prompt": "Write down the equation of f in the form "
                           "y = ax^2 + bx + c.",
                 "expected": std_form,
                 "steps": [
                     f"Start from f(x) = {'' if a == 1 else (a if a != -1 else '-')}{_factor_from_root(p)}^2"
                     + (" " + _signed_term(q) if q != 0 else ""),
                     f"Expand the square: {_factor_from_root(p)}^2 = x^2 "
                     + _signed_term(int(b_coef / a) if b_coef % a == 0 else b_coef / a, "x") + " " + _signed_term(p * p),
                     f"Multiply by a = {a}: "
                     + f"{a}x^2 " + _signed_term(b_coef, "x") + " "
                     + _signed_term(a * p * p),
                     f"Add q = {q}.",
                     f"{std_form}",
                 ],
                 "marks": 3,
                 "skill_id": "functions.parabola.equation"},
                {"n": "1.4",
                 "prompt": "Write down the range of f.",
                 "expected": f"y {range_op} {q}",
                 "steps": [
                     f"Turning point: ({p}; {q}).",
                     f"a = {a} {'>' if a > 0 else '<'} 0, so f opens "
                     f"{'up' if a > 0 else 'down'}.",
                     f"Range: y {range_op} {q}.",
                 ],
                 "marks": 2,
                 "skill_id": "functions.parabola.range"},
                {"n": "1.5",
                 "prompt": "For which values of x is f(x) decreasing?",
                 "expected": (f"x > {p}" if a > 0 else f"x < {p}"),
                 "steps": [
                     "A parabola is decreasing on the side of the turning "
                     "point where the curve goes down as x increases.",
                     f"Turning point is at x = {p}.",
                     f"a {'>' if a > 0 else '<'} 0, so f is decreasing for "
                     f"{'x > ' + str(p) if a > 0 else 'x < ' + str(p)}.",
                 ],
                 "marks": 2,
                 "skill_id": "functions.parabola.monotone"},
            ]
            out.append({
                "scenario": "parabola_turning_point",
                "skill_id": "functions.parabola",
                "problem": problem,
                "diagram_path": dpath,
                "subquestions": subs,
                "total_marks": sum(s["marks"] for s in subs),
                "parameters": {"a": a, "p": p, "q": q,
                               "x_a": x_a, "y_a": y_a},
            })

        else:  # two_roots
            params = _try_parabola_params_roots(rng)
            if params is None:
                continue
            a, r1, r2, c = params
            if r1 > r2:
                r1, r2 = r2, r1

            sig = f"prt_{a}_{r1}_{r2}"
            dpath = None
            if render:
                try:
                    import numpy as np
                    import matplotlib.pyplot as plt
                    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
                    fpath = DIAGRAM_DIR / f"{sig}.png"
                    key_vals = [r1, r2, 0, c]
                    span = max(abs(v) for v in key_vals) + 4
                    lim = max(int(np.ceil(span / 2) * 2), 7)
                    fig, ax = _setup_plane(lim)
                    p_mid = (r1 + r2) / 2
                    q_tp = a * (p_mid - r1) * (p_mid - r2)
                    _draw_parabola(ax, a, p_mid, q_tp, lim, label="f")
                    _draw_point(ax, r1, 0, label="", show_coords=False)
                    _draw_point(ax, r2, 0, label="", show_coords=False)
                    _draw_point(ax, 0, c, label="", show_coords=False)
                    fig.tight_layout(pad=0.2)
                    fig.savefig(fpath, dpi=110, bbox_inches="tight",
                                facecolor="white", edgecolor="none")
                    plt.close(fig)
                    dpath = str(fpath)
                except Exception:
                    dpath = None

            b_coef = -a * (r1 + r2)
            c_coef = a * r1 * r2
            p_mid = (r1 + r2) / 2
            q_tp = a * (p_mid - r1) * (p_mid - r2)
            std_parts = [f"{a}x^2" if a != 1 else "x^2"]
            if b_coef != 0:
                std_parts.append(_signed_term(b_coef, "x"))
            if c_coef != 0:
                std_parts.append(_signed_term(c_coef))
            std_form = "f(x) = " + " ".join(std_parts)
            range_op = ">=" if a > 0 else "<="
            ineq_ans = _solve_inequality_parabola(a, r1, r2)
            tp_display = _fnum(q_tp) if q_tp == int(q_tp) else f"{q_tp:.2f}"

            problem = (
                f"The diagram shows a parabola f that cuts the x-axis at "
                f"({r1}; 0) and ({r2}; 0). The y-intercept of f is (0; {c})."
            )

            subs = [
                {"n": "1.1",
                 "prompt": "Write down the equation of f in the form "
                           "y = a(x - r1)(x - r2).",
                 "expected": f"y = a{_factor_from_root(r1)}{_factor_from_root(r2)}",
                 "steps": [
                     f"x-intercepts are {r1} and {r2}.",
                     f"So f(x) = a{_factor_from_root(r1)}{_factor_from_root(r2)}.",
                 ],
                 "marks": 2,
                 "skill_id": "functions.parabola.intercepts"},
                {"n": "1.2",
                 "prompt": "Calculate the value of a.",
                 "expected": f"a = {a}",
                 "steps": [
                     f"Substitute the y-intercept (0; {c}) into "
                     f"f(x) = a{_factor_from_root(r1)}{_factor_from_root(r2)}.",
                     f"{c} = a({-r1})({-r2})",
                     f"{c} = a({(-r1) * (-r2)})",
                     f"a = {a}",
                 ],
                 "marks": 3,
                 "skill_id": "functions.parabola.parameter"},
                {"n": "1.3",
                 "prompt": "Write down the equation of f in the form "
                           "y = ax^2 + bx + c.",
                 "expected": std_form,
                 "steps": [
                     f"Start from f(x) = {a}{_factor_from_root(r1)}{_factor_from_root(r2)}.",
                     f"Expand the brackets: {_factor_from_root(r1)}{_factor_from_root(r2)} = "
                     f"x^2 " + _signed_term(-(r1 + r2), "x") + " "
                     + _signed_term(r1 * r2),
                     f"Multiply by a = {a}: "
                     + f"{a}x^2 " + _signed_term(b_coef, "x") + " "
                     + _signed_term(c_coef),
                     f"{std_form}",
                 ],
                 "marks": 3,
                 "skill_id": "functions.parabola.equation"},
                {"n": "1.4",
                 "prompt": "Write down the coordinates of the turning point of f.",
                 "expected": f"({_fnum(p_mid)}; {tp_display})",
                 "steps": [
                     "By symmetry, the x-coordinate of the turning point is "
                     f"the midpoint of {r1} and {r2}.",
                     f"x = ({r1} + {r2}) / 2 = {_fnum(p_mid)}.",
                     f"Substitute into f: y = {tp_display}.",
                     f"Turning point: ({_fnum(p_mid)}; {tp_display}).",
                 ],
                 "marks": 3,
                 "skill_id": "functions.parabola.turning"},
                {"n": "1.5",
                 "prompt": "For which values of x is f(x) > 0?",
                 "expected": ineq_ans,
                 "steps": [
                     "f(x) > 0 means the curve lies above the x-axis.",
                     f"The x-intercepts ({r1} and {r2}) divide the x-axis into "
                     "three regions: left of the smaller root, between the "
                     "roots, and right of the larger root.",
                     f"a = {a} {'>' if a > 0 else '<'} 0, so the parabola "
                     f"opens {'up' if a > 0 else 'down'}.",
                     ("Therefore f(x) > 0 OUTSIDE the roots: "
                      if a > 0 else
                      "Therefore f(x) > 0 BETWEEN the roots: ")
                     + f"{ineq_ans}.",
                 ],
                 "marks": 3,
                 "skill_id": "functions.inequality"},
            ]
            out.append({
                "scenario": "parabola_two_roots",
                "skill_id": "functions.parabola",
                "problem": problem,
                "diagram_path": dpath,
                "subquestions": subs,
                "total_marks": sum(s["marks"] for s in subs),
                "parameters": {"a": a, "r1": r1, "r2": r2, "c": c,
                               "p_mid": p_mid, "q_tp": q_tp},
            })

    return out


# Backward-compatible alias
def gen_scenario_parabola_line(count=10, seed=201, render=True):
    return gen_scenario_parabola(count=count, seed=seed,
                                 shape="turning_point", render=render)

# ============================================================
# Exponential + line scenario (NEW)
# Reference: 2020 P1 Q5 shape.
#   f(x) = a*b^x + q meets the horizontal line y = k at one point B.
#   Subquestions: y-intercept A, coordinate of B, domain of inverse,
#   translation, inequality.
# ============================================================

def _try_exponential_params(rng):
    """Return (base, q, k) where:
       f(x) = base^x + q
       line y = k intersects f at x = x_b such that base^x_b is a
       clean integer.
    """
    # base must be a positive rational > 0, != 1, representable as fraction
    base_options = [
        (2, 1), (3, 1), (4, 1),
        (1, 2), (1, 3),
    ]
    num, den = rng.choice(base_options)
    base = num / den

    # Pick x_b such that base^x_b is a nice value
    # We'll pick x_b integer and let y_b = base^x_b (must be rational, may
    # be fractional for base = 1/2, 1/3)
    x_b_options = [-2, -1, 1, 2]
    x_b = rng.choice(x_b_options)
    y_b = (num ** x_b) / (den ** x_b)
    # Keep y_b moderate
    if not (0.1 <= y_b <= 20):
        return None

    # q must give integer (or clean rational) y-intercept
    q_options = [-2, -1, 1, 2]
    q = rng.choice(q_options)

    # Line y = k where k = y_b + q must be a clean number
    k = y_b + q
    if not (0.1 <= k <= 20):
        return None

    # Also ensure y-intercept base^0 + q = 1 + q is clean
    y_a = 1 + q

    return num, den, q, k, x_b, y_b, y_a


def _base_display(num, den):
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def _render_exponential(num, den, q, k, x_b, y_b, y_a, sig):
    import numpy as np
    import matplotlib.pyplot as plt
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    path = DIAGRAM_DIR / f"{sig}.png"

    base = num / den
    # Pick a range that captures the interesting behaviour
    x_lo, x_hi = -6, 6
    if base < 1:
        # exponential decay: y approaches q as x -> +inf
        pass
    # Y window
    key_y = [q, k, y_a, 0]
    span_y = max(abs(v) for v in key_y) + 3
    lim_y = int(np.ceil(span_y / 2) * 2)
    lim_y = max(lim_y, 6)
    lim = lim_y

    fig, ax = _setup_plane(lim)

    # Draw horizontal asymptote y = q
    _draw_horizontal_asymptote(ax, q, lim)

    # Draw exponential curve
    xs = np.linspace(-lim, lim, 500)
    ys = base ** xs + q
    mask = (ys >= -lim) & (ys <= lim)
    ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    # Draw horizontal line y = k (dotted)
    ax.plot([-lim, lim], [k, k], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)

    # Ticks: y_a on y-axis, k on y-axis
    _draw_axes_ticks(ax, x_ticks=[x_b], y_ticks=sorted(set([y_a, int(k) if k == int(k) else k, q])))

    # Points: A = y-intercept, B = intersection with y=k
    _draw_point(ax, 0, y_a, label="A", show_coords=True, offset="up-left")
    _draw_point(ax, x_b, y_b + q, label="B", show_coords=True, offset="up-right")

    # Curve label
    ax.text(lim * 0.55, q + 1.5, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return path


def gen_scenario_exponential(count=10, seed=301, render=True):
    """DBE-style exponential + horizontal-line questions.

    Reference: 2020 P1 Q5 shape.
    """
    rng = random.Random(seed)
    out = []
    attempts = 0
    while len(out) < count and attempts < 20000:
        attempts += 1
        params = _try_exponential_params(rng)
        if params is None:
            continue
        num, den, q, k, x_b, y_b, y_a = params

        base_str = _base_display(num, den)
        sig = f"exp_{num}_{den}_{q}_{int(k*10)}_{x_b}"
        dpath = None
        if render:
            try:
                dpath = str(_render_exponential(num, den, q, k,
                                                 x_b, y_b, y_a, sig))
            except Exception as e:
                print(f"    render error: {e}")
                dpath = None

        # f(x) = base^x + q
        if den == 1:
            f_eq = f"f(x) = {num}^x" + (" " + _signed_term(q) if q != 0 else "")
        else:
            f_eq = f"f(x) = ({base_str})^x" + (" " + _signed_term(q) if q != 0 else "")

        # Translation h(x) = base^(x - t) + q  (shift right by t)
        t = rng.choice([1, 2, 3])
        h_eq = (f"h(x) = {num}^(x - {t})" if den == 1
                else f"h(x) = ({base_str})^(x - {t})")
        if q != 0:
            h_eq += " " + _signed_term(q)

        # Domain of inverse of f: range of f is (q, +inf) if base > 1
        # and (q, +inf) still if 0 < base < 1 (asymptote at y = q)
        if q == 0:
            inv_domain = "x > 0" if num > den else "x > 0"
        else:
            inv_domain = f"x > {q}" if q > 0 else f"x > {q}"

        problem = (
            f"The graph of {f_eq} is sketched. "
            f"A is the y-intercept of f. "
            f"B is the point of intersection of f and the line y = {_fnum(k)}."
        )

        subs = [
            {"n": "1.1",
             "prompt": "Write down the coordinates of A, the y-intercept of f.",
             "expected": f"A(0; {_fnum(y_a)})",
             "steps": [
                 "The y-intercept is where x = 0.",
                 f"f(0) = {base_str}^0" + (" " + _signed_term(q) if q != 0 else ""),
                 f"= 1" + (" " + _signed_term(q) if q != 0 else ""),
                 f"= {_fnum(y_a)}.",
                 f"A(0; {_fnum(y_a)})",
             ],
             "marks": 1,
             "skill_id": "functions.exponential.intercept"},
            {"n": "1.2",
             "prompt": f"Determine the coordinates of B, the point of "
                       f"intersection of f and the line y = {_fnum(k)}.",
             "expected": f"B({x_b}; {_fnum(k)})",
             "steps": [
                 f"Set f(x) = {_fnum(k)}:",
                 f"{base_str}^x" + (" " + _signed_term(q) if q != 0 else "")
                 + f" = {_fnum(k)}",
                 (f"{base_str}^x = {_fnum(k - q)}" if q != 0
                  else f"{base_str}^x = {_fnum(k)}"),
                 f"Recognise {_fnum(k - q) if q != 0 else _fnum(k)} = "
                 f"{base_str}^{x_b}.",
                 f"So x = {x_b}.",
                 f"Since B is on the line y = {_fnum(k)}, B({x_b}; {_fnum(k)}).",
             ],
             "marks": 3,
             "skill_id": "functions.exponential.intersection"},
            {"n": "1.3",
             "prompt": "Write down the equation of the horizontal asymptote of f.",
             "expected": f"y = {_fnum(q)}",
             "steps": [
                 "The horizontal asymptote of f(x) = a*b^x + q is y = q.",
                 f"From the equation, q = {_fnum(q)}.",
                 f"y = {_fnum(q)}",
             ],
             "marks": 2,
             "skill_id": "functions.exponential.asymptote"},
            {"n": "1.4",
             "prompt": "Write down the domain of f^{-1}, the inverse of f.",
             "expected": inv_domain,
             "steps": [
                 "The domain of f^{-1} is the range of f.",
                 f"The range of f is y > {_fnum(q)} "
                 f"(the curve approaches the asymptote but never reaches it).",
                 f"So the domain of f^{-1} is {inv_domain}.",
             ],
             "marks": 2,
             "skill_id": "functions.exponential.inverse"},
            {"n": "1.5",
             "prompt": f"Describe the transformation that maps f to "
                       f"h(x) = {h_eq.split('= ')[1]}.",
             "expected": f"f translated {t} unit{'s' if t != 1 else ''} to the right",
             "steps": [
                 f"f(x) = {f_eq.split('= ')[1]}",
                 f"h(x) = {h_eq.split('= ')[1]}",
                 f"In h, x has been replaced by (x - {t}).",
                 f"Transformation: {t} unit{'s' if t != 1 else ''} to the right.",
             ],
             "marks": 2,
             "skill_id": "functions.transformation"},
        ]

        out.append({
            "scenario": "exponential_line",
            "skill_id": "functions.exponential",
            "problem": problem,
            "diagram_path": dpath,
            "subquestions": subs,
            "total_marks": sum(s["marks"] for s in subs),
            "parameters": {"num": num, "den": den, "q": q, "k": k,
                           "x_b": x_b, "y_b": y_b, "y_a": y_a, "t": t},
        })
    return out


# Update the registry
ALL_SCENARIOS = {
    "hyperbola_line":          gen_scenario_hyperbola_line,
    "parabola_turning_point":  lambda **kw: gen_scenario_parabola(shape="turning_point", **kw),
    "parabola_two_roots":      lambda **kw: gen_scenario_parabola(shape="two_roots", **kw),
    "exponential_line":        gen_scenario_exponential,
}
