"""
question_diagrams.py — DBE-style diagram renderers.

Each renderer takes a set of parameters and writes a PNG to
data/processed/tutor/question_diagrams/. It follows the same DBE
conventions we validated earlier: full Cartesian plane, arrowheads on
axes, minimal labels, dotted asymptotes, small point markers.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "tutor" / "question_diagrams"
OUT.mkdir(parents=True, exist_ok=True)


def _setup_plane(lim):
    fig, ax = plt.subplots(figsize=(6.0, 6.0), dpi=110)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.annotate("", xy=(lim, 0), xytext=(-lim, 0),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1,
                                mutation_scale=12))
    ax.annotate("", xy=(0, lim), xytext=(0, -lim),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1,
                                mutation_scale=12))
    ax.text(lim - 0.35, -0.65, "x", fontsize=13, fontstyle="italic",
            ha="center", va="top")
    ax.text(0.55, lim - 0.35, "y", fontsize=13, fontstyle="italic",
            ha="left", va="top")
    ax.text(-0.35, -0.5, "O", fontsize=11, ha="right", va="top")
    return fig, ax


def _tick(ax, x=None, y=None, label=None, side="x"):
    if side == "x" and x is not None:
        ax.plot([x, x], [-0.13, 0.13], color="black", lw=0.9)
        ax.text(x, -0.35, label if label is not None else str(x),
                fontsize=10, ha="center", va="top")
    if side == "y" and y is not None:
        ax.plot([-0.13, 0.13], [y, y], color="black", lw=0.9)
        ax.text(-0.35, y, label if label is not None else str(y),
                fontsize=10, ha="right", va="center")


def _dot(ax, x, y):
    ax.plot(x, y, "o", color="black", markersize=4, zorder=5)


# ---------- Hyperbola solo (Q5) ----------

def render_hyperbola_solo(a, p, q, yint, sig):
    """f(x) = a/(x+p) + q. Points on the y-axis. Dotted asymptotes."""
    vert = -p
    lim = 8
    fig, ax = _setup_plane(lim)

    ax.plot([vert, vert], [-lim, lim], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)
    ax.plot([-lim, lim], [q, q], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)

    eps = 0.06; step = 0.02
    xs_left = np.arange(-lim, vert - eps, step)
    ys_left = a / (xs_left + p) + q
    mask = (ys_left >= -lim) & (ys_left <= lim)
    if mask.any():
        ax.plot(xs_left[mask], ys_left[mask], color="black", lw=1.5, zorder=3)

    xs_right = np.arange(vert + eps, lim, step)
    ys_right = a / (xs_right + p) + q
    mask = (ys_right >= -lim) & (ys_right <= lim)
    if mask.any():
        ax.plot(xs_right[mask], ys_right[mask], color="black", lw=1.5, zorder=3)

    _dot(ax, 0, yint)
    ax.text(0.35, yint + 0.15, str(yint), fontsize=10, ha="left", va="bottom")

    ax.text((vert + lim) / 2 if vert < 0 else (vert - lim) / 2,
            q + 1.0, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ---------- Parabola + line (Q6) ----------

def render_parabola_line(a, p, q, m, c, xa, xc, sig):
    """f(x) = a(x-p)^2 + q and g(x) = mx + c. Frame fits the actual points."""
    # Frame sized to the interesting region (intersections + turning point)
    x_min = min(xa, xc, p) - 3
    x_max = max(xa, xc, p) + 3
    # y-range: intersection y-values and turning point
    yc = m * xc + c
    y_vals = [0, yc, q]
    y_min = min(y_vals) - 4
    y_max = max(y_vals) + 4

    # Symmetric-ish plane: use the max absolute extent so axes look balanced
    lim = max(abs(x_min), abs(x_max), abs(y_min), abs(y_max))
    lim = int(lim) + 2

    fig, ax = _setup_plane(lim)

    # --- Parabola ---
    xs = np.linspace(-lim, lim, 900)
    ys = a * (xs - p) ** 2 + q
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    # --- Line g, clipped to the frame ---
    xs_line = np.array([-lim, lim])
    ys_line = m * xs_line + c
    # Clip the segment to the visible y-range
    if ys_line[0] < -lim:
        xs_line[0] = (-lim - c) / m
        ys_line[0] = -lim
    elif ys_line[0] > lim:
        xs_line[0] = (lim - c) / m
        ys_line[0] = lim
    if ys_line[1] < -lim:
        xs_line[1] = (-lim - c) / m
        ys_line[1] = -lim
    elif ys_line[1] > lim:
        xs_line[1] = (lim - c) / m
        ys_line[1] = lim
    ax.plot(xs_line, ys_line, color="black", lw=1.3, zorder=2)

    # --- Points A and C ---
    _dot(ax, xa, 0)
    ax.text(xa + 0.3, 0.4, "A", fontsize=11, ha="left", va="bottom")
    _dot(ax, xc, yc)
    ax.text(xc + 0.3, yc + 0.4, f"C({xc}; {yc})", fontsize=10,
            ha="left", va="bottom")

    # --- Curve labels ---
    # f near the turning point
    ax.text(p + 0.6, q + 0.3, "f", fontsize=14, fontstyle="italic",
            ha="left", va="bottom")
    # g at one end of the visible line
    if m != 0:
        gx = xs_line[1] - 0.5
        gy = m * gx + c
        ax.text(gx, gy + 0.4, "g", fontsize=14, fontstyle="italic",
                ha="right", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ---------- Cubic (Q9) ----------

def render_cubic(a, xa, ya, xb, yb, yc, sig):
    """Cubic with two turning points A(xa, ya), B(xb, yb) and y-intercept yc."""
    lim = 12
    fig, ax = _setup_plane(lim)

    # fit cubic through given turning points and y-intercept
    # f(x) = k3 x^3 + k2 x^2 + k1 x + k0
    # k0 = yc;  f'(xa)=0; f'(xb)=0  => 3k3 xa^2 + 2k2 xa + k1 = 0
    #                    y at xa = ya, at xb = yb
    # solve with numpy
    A_mat = np.array([
        [xa ** 3, xa ** 2, xa, 1],
        [xb ** 3, xb ** 2, xb, 1],
        [3 * xa ** 2, 2 * xa, 1, 0],
        [3 * xb ** 2, 2 * xb, 1, 0],
    ])
    b_vec = np.array([ya, yb, 0, 0])
    try:
        k3, k2, k1, k0 = np.linalg.solve(A_mat, b_vec)
    except Exception:
        return None
    xs = np.linspace(-lim, lim, 900)
    ys = k3 * xs ** 3 + k2 * xs ** 2 + k1 * xs + k0
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    _dot(ax, xa, ya); _dot(ax, xb, yb); _dot(ax, 0, yc)
    ax.text(xa, ya + 0.6, f"A({xa}; {ya})", fontsize=10, ha="center", va="bottom")
    ax.text(xb, yb + 0.6, f"B({xb}; {yb})", fontsize=10, ha="center", va="bottom")
    ax.text(0.35, yc + 0.3, str(yc), fontsize=10, ha="left", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)

# ---------- Exponential solo (Q4 2023 style) ----------

def render_exponential_solo(a_base, q, x_pt, y_pt, sig):
    """f(x) = a^x + q, plot with horizontal asymptote and a labelled point."""
    lim_x = 4.5
    lim_y = 10
    fig, ax = _setup_plane(max(lim_x, lim_y))

    xs = np.linspace(-lim_x, lim_x, 500)
    ys = a_base ** xs + q
    mask = (ys >= -lim_y) & (ys <= lim_y)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    ax.plot([-lim_y, lim_y], [q, q], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)

    _dot(ax, x_pt, y_pt)
    ax.text(x_pt + 0.3, y_pt + 0.4, f"({x_pt}; {y_pt})",
            fontsize=10, ha="left", va="bottom")

    ax.text(lim_y * 0.6, q + 1.0, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ---------- Log solo (Q4 2025 style) ----------

def render_log_solo(base_frac, x_pt, y_pt, sig):
    """f(x) = log_(base_frac)(x). base_frac is (num, den) e.g. (1, 2)."""
    num, den = base_frac
    base = num / den
    lim = 8
    fig, ax = _setup_plane(lim)

    xs = np.linspace(0.05, lim, 500)
    ys = np.log(xs) / np.log(base)
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    ax.plot([-lim, lim], [0, 0], color="black", lw=0.6, zorder=1)
    ax.plot([0, 0], [-lim, lim], color="black", lw=0.6, zorder=1)

    # x-intercept (1; 0)
    _dot(ax, 1, 0)
    ax.text(1 + 0.2, 0.4, "A", fontsize=11, ha="left", va="bottom")

    _dot(ax, x_pt, y_pt)
    ax.text(x_pt + 0.3, y_pt - 0.5, f"({x_pt}; t)",
            fontsize=10, ha="left", va="top")

    ax.text(lim * 0.55, 2.5, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ---------- Cylinder (Q10 2025) ----------

def render_cylinder(x, h, sig):
    """Rendered cylinder with dimensions labelled."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=110)
    ax.set_xlim(-2.5, 3.5); ax.set_ylim(-2.5, 2.8)
    ax.set_aspect("equal"); ax.axis("off")

    cx, cy = 0.0, 0.0
    rx, ry = 1.2, 0.35
    # Back ellipse (top)
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(cx + rx * np.cos(theta), cy + 1.5 + ry * np.sin(theta),
            color="black", lw=1.0)
    # Front ellipse (bottom)
    ax.plot(cx + rx * np.cos(theta), cy - 1.5 + ry * np.sin(theta),
            color="black", lw=1.0)
    # Bottom front arc only
    ax.plot(cx + rx * np.cos(theta), cy - 1.5 + ry * np.sin(theta),
            color="black", lw=1.0)
    # Sides
    ax.plot([cx - rx, cx - rx], [cy - 1.5, cy + 1.5], color="black", lw=1.0)
    ax.plot([cx + rx, cx + rx], [cy - 1.5, cy + 1.5], color="black", lw=1.0)

    ax.text(cx + rx + 0.25, cy, f"h = {h}", fontsize=12,
            ha="left", va="center")
    ax.text(cx, cy - 1.5 - ry - 0.3, f"x = {x}", fontsize=12,
            ha="center", va="top")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


# ---------- Poster rectangle (Q9 2023) ----------

def render_poster(x, y_dim, sig):
    """Poster with rectangle ABCD inside the outer page, showing
    4 cm margins on the left/right and 3 cm margins on top/bottom."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=110)
    # Coordinates: outer page occupies (0,0) to (W, H)
    W = x + 8   # 4 cm margin each side
    H = y_dim + 6  # 3 cm margin each side
    ax.set_xlim(-2, W + 2); ax.set_ylim(-2, H + 2)
    ax.set_aspect("equal"); ax.axis("off")

    # Outer page
    ax.add_patch(Rectangle((0, 0), W, H, fill=False,
                            edgecolor="black", lw=1.4))
    # Inner shaded rectangle ABCD
    ax.add_patch(Rectangle((4, 3), x, y_dim, facecolor="lightgrey",
                            edgecolor="black", lw=1.2))

    # Vertex labels
    ax.text(4, 3 + y_dim + 0.5, "A", fontsize=12, ha="center", va="bottom")
    ax.text(4 + x, 3 + y_dim + 0.5, "D", fontsize=12, ha="center", va="bottom")
    ax.text(4, 3 - 0.5, "B", fontsize=12, ha="center", va="top")
    ax.text(4 + x, 3 - 0.5, "C", fontsize=12, ha="center", va="top")

    # AD = x (top edge of ABCD)
    ax.annotate("", xy=(4, 3 + y_dim + 1.5), xytext=(4 + x, 3 + y_dim + 1.5),
                arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax.text(4 + x / 2, 3 + y_dim + 1.9, f"AD = x", fontsize=11,
            ha="center", va="bottom")

    # 4 cm margin — left
    ax.annotate("", xy=(0, 3 + y_dim / 2), xytext=(4, 3 + y_dim / 2),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="darkred"))
    ax.text(2, 3 + y_dim / 2 + 0.5, "4 cm", fontsize=10, color="darkred",
            ha="center", va="bottom")

    # 4 cm margin — right
    ax.annotate("", xy=(4 + x, 3 + y_dim / 2), xytext=(W, 3 + y_dim / 2),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="darkred"))
    ax.text(4 + x + 2, 3 + y_dim / 2 + 0.5, "4 cm", fontsize=10,
            color="darkred", ha="center", va="bottom")

    # 3 cm margin — bottom
    ax.annotate("", xy=(4 + x / 2, 0), xytext=(4 + x / 2, 3),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="darkblue"))
    ax.text(4 + x / 2 + 0.4, 1.5, "3 cm", fontsize=10, color="darkblue",
            ha="left", va="center")

    # 3 cm margin — top
    ax.annotate("", xy=(4 + x / 2, 3 + y_dim), xytext=(4 + x / 2, H),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="darkblue"))
    ax.text(4 + x / 2 + 0.4, 3 + y_dim + 1.5, "3 cm", fontsize=10,
            color="darkblue", ha="left", va="center")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)



def render_parabola_hyperbola(a_par, p_par, q_par, a_hyp, p_hyp, q_hyp, sig,
                               x_par_range=None):
    """f(x) = a_par (x - p_par)^2 + q_par and g(x) = a_hyp/(x + p_hyp) + q_hyp.

    The two curves intersect where f(x) = g(x); we draw both across a window
    that shows the interesting region.
    """
    lim = 10
    fig, ax = _setup_plane(lim)

    # --- Parabola ---
    xs = np.linspace(-lim, lim, 700)
    ys = a_par * (xs - p_par) ** 2 + q_par
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    # --- Hyperbola: vertical asymptote at x = -p_hyp ---
    vert = -p_hyp
    # dotted asymptotes
    ax.plot([vert, vert], [-lim, lim], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)
    ax.plot([-lim, lim], [q_hyp, q_hyp], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)

    eps = 0.06; step = 0.02
    xs_left = np.arange(-lim, vert - eps, step)
    ys_left = a_hyp / (xs_left + p_hyp) + q_hyp
    m_l = (ys_left >= -lim) & (ys_left <= lim)
    if m_l.any():
        ax.plot(xs_left[m_l], ys_left[m_l], color="black", lw=1.5, zorder=3)
    xs_right = np.arange(vert + eps, lim, step)
    ys_right = a_hyp / (xs_right + p_hyp) + q_hyp
    m_r = (ys_right >= -lim) & (ys_right <= lim)
    if m_r.any():
        ax.plot(xs_right[m_r], ys_right[m_r], color="black", lw=1.5, zorder=3)

    # Labels
    ax.text(p_par + 0.6, q_par + 0.4, "f", fontsize=14, fontstyle="italic",
            ha="left", va="bottom")
    probe_x = vert + 1.5 if vert < 0 else vert - 1.5
    probe_y = a_hyp / (probe_x + p_hyp) + q_hyp
    if abs(probe_y) < lim - 1:
        ax.text(probe_x, probe_y + 0.6, "g", fontsize=14, fontstyle="italic",
                ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def render_log_solo_fixed(base_num, base_den, x_pt, sig):
    """f(x) = log_(base_num/base_den) x. Point at (x_pt, log value)."""
    base = base_num / base_den
    lim = 8
    fig, ax = _setup_plane(lim)

    xs = np.linspace(0.05, lim, 500)
    ys = np.log(xs) / np.log(base)
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    # x-intercept
    _dot(ax, 1, 0)
    ax.text(1 + 0.2, 0.4, "A", fontsize=11, ha="left", va="bottom")

    # Point (x_pt, log value)
    y_pt = np.log(x_pt) / np.log(base)
    _dot(ax, x_pt, y_pt)
    ax.text(x_pt + 0.3, y_pt - 0.5, f"({x_pt}; t)", fontsize=10,
            ha="left", va="top")

    ax.text(lim * 0.55, 2.5, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def render_exponential_two_points(base, q, sig):
    """f(x) = base^x + q. Labels A (y-intercept) and B (x-intercept)."""
    lim = 8
    fig, ax = _setup_plane(lim)

    xs = np.linspace(-lim, lim, 500)
    ys = base ** xs + q
    mask = (ys >= -lim) & (ys <= lim)
    if mask.any():
        ax.plot(xs[mask], ys[mask], color="black", lw=1.5, zorder=3)

    # horizontal asymptote
    ax.plot([-lim, lim], [q, q], color="black",
            linestyle=(0, (1, 3)), lw=0.9, zorder=1)

    # A: y-intercept (0, 1 + q)
    yint = 1 + q
    _dot(ax, 0, yint)
    ax.text(0.3, yint + 0.4, f"A(0; {yint})", fontsize=10,
            ha="left", va="bottom")

    # B: x-intercept where base^x = -q
    if -q > 0:
        x_b = math.log(-q) / math.log(base)
        if abs(x_b) < lim:
            _dot(ax, x_b, 0)
            ax.text(x_b + 0.3, 0.4, f"B({round(x_b,2)}; 0)",
                    fontsize=10, ha="left", va="bottom")

    ax.text(lim * 0.55, q + 1.5, "f", fontsize=14, fontstyle="italic",
            ha="center", va="bottom")

    path = OUT / f"{sig}.png"
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


