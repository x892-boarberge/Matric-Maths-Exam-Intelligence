# src/tutor/question_diagrams_p2.py
# DBE-style renderers for Paper 2.
# Extends src/tutor/question_diagrams.py (P1 renderers stay untouched).

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
from pathlib import Path
from matplotlib.ticker import FuncFormatter, MultipleLocator

_ROOT = None
for _cand in [Path.cwd()] + list(Path.cwd().parents):
    if (_cand / "src" / "tutor").exists():
        _ROOT = _cand
        break
if _ROOT is None:
    _ROOT = Path(r"C:\Users\Administrator\Desktop\Matric-Maths-Exam-Intelligence")


# ============================================================
# CORE HELPERS
# ============================================================

def _resolve_point(spec, pts):
    # Accept tuple OR list of two numbers as raw (x, y)
    if isinstance(spec, (tuple, list)) and len(spec) == 2 and all(
            isinstance(v, (int, float)) for v in spec):
        return tuple(spec)
    return pts[spec]


def _dbe_axes(ax, xlim, ylim, x_label="", y_label="",
              grid=False, aspect="auto"):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect(aspect, adjustable="box")
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(),
            clip_on=False, markersize=6)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(),
            clip_on=False, markersize=6)
    if x_label:
        ax.set_xlabel(x_label, loc="right", fontsize=10)
    if y_label:
        ax.set_ylabel(y_label, loc="top", fontsize=10)
    if grid:
        ax.grid(True, which="major", color="lightgray",
                linewidth=0.5, alpha=0.7)
    ax.tick_params(labelsize=8, direction="out", length=3, width=0.8)


def _blank_axes(xlim, ylim, figsize=(7, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return fig, ax


def _save(fig, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(out_path)


def _label_radial(ax, x, y, label, away_from, numbered=None, offset=0.32):
    cx, cy = away_from
    dx, dy = x - cx, y - cy
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    tx = x + offset * ux
    ty = y + offset * uy
    ha = "left" if ux > 0.15 else ("right" if ux < -0.15 else "center")
    va = "bottom" if uy > 0.15 else ("top" if uy < -0.15 else "center")
    txt = f"{label}$_{{{numbered}}}$" if numbered else label
    ax.plot(x, y, "ko", markersize=4)
    ax.text(tx, ty, txt, fontsize=11, ha=ha, va=va)


def _angle_arc(ax, vertex, p1, p2, label=None, numbered=None,
               r_arc=None, r_label=None, segment_scale=1.0,
               label_xy=None):
    vx, vy = vertex
    d1 = math.hypot(p1[0] - vx, p1[1] - vy)
    d2 = math.hypot(p2[0] - vx, p2[1] - vy)
    short = min(d1, d2) or 1.0
    if r_arc is None:
        r_arc = 0.15 * short * segment_scale
    if r_label is None:
        r_label = r_arc * 1.55
    a1 = math.atan2(p1[1] - vy, p1[0] - vx)
    a2 = math.atan2(p2[1] - vy, p2[0] - vx)
    delta = a2 - a1
    while delta > math.pi:
        delta -= 2 * math.pi
    while delta < -math.pi:
        delta += 2 * math.pi
    th = np.linspace(a1, a1 + delta, 60)
    ax.plot(vx + r_arc * np.cos(th), vy + r_arc * np.sin(th),
            "k-", linewidth=0.9)
    if label is not None:
        if label_xy is not None:
            lx, ly = label_xy
        else:
            mid = a1 + delta / 2
            lx = vx + r_label * math.cos(mid)
            ly = vy + r_label * math.sin(mid)
        txt = f"{label}$_{{{numbered}}}$" if numbered else label
        ax.text(lx, ly, txt, fontsize=12, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15",
                          facecolor="white", edgecolor="none", alpha=0.85))


def _right_angle(ax, vertex, p1, p2, size=None):
    vx, vy = vertex
    u1 = np.array([p1[0] - vx, p1[1] - vy], dtype=float)
    u2 = np.array([p2[0] - vx, p2[1] - vy], dtype=float)
    d1 = np.linalg.norm(u1)
    d2 = np.linalg.norm(u2)
    if size is None:
        size = 0.12 * min(d1, d2)
    u1 /= d1
    u2 /= d2
    a = np.array([vx, vy])
    pts = np.array([a + size * u1,
                    a + size * u1 + size * u2,
                    a + size * u2])
    ax.plot(pts[:, 0], pts[:, 1], "k-", linewidth=0.9)


def _tick(ax, p1, p2, n=1, size=None):
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return
    if size is None:
        size = 0.06 * L
    nx, ny = -dy / L, dx / L
    tx, ty = dx / L, dy / L
    for k in range(n):
        s = (k - (n - 1) / 2) * 0.11 * size
        cx = mx + tx * s
        cy = my + ty * s
        ax.plot([cx - nx * size / 2, cx + nx * size / 2],
                [cy - ny * size / 2, cy + ny * size / 2],
                "k-", linewidth=1.0)


def _circle_xy(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _edge_label(ax, p1, p2, text, offset=0.25, perpendicular=True,
                fontsize=12):
    """Place text at midpoint of segment p1-p2, offset perpendicular."""
    import math
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    L = math.hypot(dx, dy) or 1
    if perpendicular:
        nx, ny = -dy / L, dx / L
    else:
        nx, ny = 0, 0
    ax.text(mx + offset * nx, my + offset * ny, text,
            fontsize=fontsize, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.2",
                      facecolor="white", edgecolor="none", alpha=0.9),
            zorder=5)


# ============================================================
# STATS
# ============================================================

def render_scatter_regression(points, a, b, xlim=None, ylim=None,
                              x_label="", y_label="",
                              y_tick_step=50000,
                              grid=True, out_path=None):
    points = np.array(points)
    xs, ys = points[:, 0], points[:, 1]
    if xlim is None:
        xlim = (0, xs.max() + 1)
    if ylim is None:
        ylim = (0, ys.max() * 1.1)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    _dbe_axes(ax, xlim, ylim, x_label, y_label, grid=grid, aspect="auto")
    ax.yaxis.set_major_locator(MultipleLocator(y_tick_step))
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", " ")))
    ax.plot(xs, ys, "ko", markersize=5, zorder=3)
    line_x = np.linspace(xlim[0], xlim[1], 100)
    ax.plot(line_x, a + b * line_x, "k-", linewidth=1.2, zorder=2)
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "scatter_regression.png"
    return _save(fig, out_path)


def render_ogive(points, x_label="", y_label="Cumulative frequency",
                 xlim=None, ylim=None, grid=True, out_path=None):
    points = np.array(points)
    xs, ys = points[:, 0], points[:, 1]
    if xlim is None:
        xlim = (xs.min() * 0.9, xs.max() * 1.05)
    if ylim is None:
        ylim = (0, ys.max() * 1.1)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    _dbe_axes(ax, xlim, ylim, x_label, y_label, grid=grid, aspect="auto")
    ax.plot(xs, ys, "k-", linewidth=1.4, zorder=2)
    ax.plot(xs, ys, "ko", markersize=4, zorder=3)
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "ogive.png"
    return _save(fig, out_path)


def render_histogram(boundaries, frequencies, x_label="", y_label="Frequency",
                     grid=True, out_path=None):
    boundaries = list(boundaries)
    frequencies = list(frequencies)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    _dbe_axes(ax,
              (min(boundaries) * 0.9, max(boundaries) * 1.05),
              (0, max(frequencies) * 1.15),
              x_label, y_label, grid=grid, aspect="auto")
    for i, f in enumerate(frequencies):
        ax.bar(boundaries[i], f, width=boundaries[i+1] - boundaries[i],
               align="edge", facecolor="#c8c8c8",
               edgecolor="black", linewidth=1.0)
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "histogram.png"
    return _save(fig, out_path)


def render_bar_chart(categories, series, x_label="", y_label="",
                     title="", y_tick_step=None, grid=True,
                     xlim=None, ylim=None, out_path=None):
    n_cats = len(categories)
    n_series = len(series)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    if ylim is None:
        ylim = (0, max(max(s["values"]) for s in series) * 1.15)
    ax.set_ylim(*ylim)
    bar_width = 0.8 / n_series
    x_positions = np.arange(n_cats)
    for i, s in enumerate(series):
        offset = (i - (n_series - 1) / 2) * bar_width
        shade = 0.25 + 0.35 * i
        color = (shade, shade, shade)
        ax.bar(x_positions + offset, s["values"], width=bar_width,
               label=s.get("label", ""), color=color,
               edgecolor="black", linewidth=0.7)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(categories, fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    if y_tick_step:
        ax.yaxis.set_major_locator(MultipleLocator(y_tick_step))
    if grid:
        ax.grid(True, which="major", axis="y",
                color="lightgray", linewidth=0.5, alpha=0.7)
    if x_label:
        ax.set_xlabel(x_label, fontsize=10)
    if y_label:
        ax.set_ylabel(y_label, fontsize=10)
    if title:
        ax.set_title(title, fontsize=11)
    if n_series > 1:
        ax.legend(fontsize=8, frameon=False)
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "bar_chart.png"
    return _save(fig, out_path)


# ============================================================
# ANALYTICAL GEOMETRY
# ============================================================

def render_analytical_triangle(named_points, theta_label=None,
                               dashed_lines=None, right_angles=None,
                               xlim=None, ylim=None, out_path=None):
    pts = named_points
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    if xlim is None:
        xlim = (min(xs) - 3, max(xs) + 3)
    if ylim is None:
        ylim = (min(ys) - 3, max(ys) + 3)
    fig, ax = plt.subplots(figsize=(7, 6))
    _dbe_axes(ax, xlim, ylim, "x", "y", grid=False, aspect="equal")
    labels = list(pts.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            x1, y1 = pts[labels[i]]
            x2, y2 = pts[labels[j]]
            ax.plot([x1, x2], [y1, y2], "k-", linewidth=1.1)
    if dashed_lines:
        for a, b in dashed_lines:
            x1, y1 = _resolve_point(a, pts)
            x2, y2 = _resolve_point(b, pts)
            ax.plot([x1, x2], [y1, y2], "k--", linewidth=0.9)
    if theta_label:
        v_spec, p1_spec, p2_spec = theta_label
        vx, vy = _resolve_point(v_spec, pts)
        p1x, p1y = _resolve_point(p1_spec, pts)
        p2x, p2y = _resolve_point(p2_spec, pts)
        a1 = math.atan2(p1y - vy, p1x - vx)
        a2 = math.atan2(p2y - vy, p2x - vx)
        if a2 - a1 > math.pi:
            a2 -= 2 * math.pi
        elif a2 - a1 < -math.pi:
            a2 += 2 * math.pi
        radius = 1.2
        th = np.linspace(a1, a2, 40)
        ax.plot(vx + radius * np.cos(th), vy + radius * np.sin(th),
                "k-", linewidth=0.9)
        mid = (a1 + a2) / 2
        ax.text(vx + (radius + 0.6) * np.cos(mid),
                vy + (radius + 0.6) * np.sin(mid),
                "\u03b8", fontsize=12, ha="center", va="center")
    if right_angles:
        for v in right_angles:
            vx, vy = _resolve_point(v, pts)
            ax.plot(vx, vy, marker="s", markersize=8,
                    markerfacecolor="none", markeredgecolor="black")
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for name, (x, y) in pts.items():
        _label_radial(ax, x, y, name, away_from=(cx, cy))
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "analytical_triangle.png"
    return _save(fig, out_path)


def render_analytical_triangle_theta_at_vertex(named_points, theta_vertex,
                                                horizontal_dir="left",
                                                other_point=None,
                                                theta_radius=1.5,
                                                out_path=None):
    pts = named_points
    xs = [p[0] for p in pts.values()]
    ys = [p[1] for p in pts.values()]
    xlim = (min(xs) - 3, max(xs) + 3)
    ylim = (min(ys) - 3, max(ys) + 3)
    fig, ax = plt.subplots(figsize=(8, 6))
    _dbe_axes(ax, xlim, ylim, "x", "y", grid=False, aspect="equal")
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_locator(MultipleLocator(2))
    labels = list(pts.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            x1, y1 = pts[labels[i]]
            x2, y2 = pts[labels[j]]
            ax.plot([x1, x2], [y1, y2], "k-", linewidth=1.1)
    vx, vy = pts[theta_vertex]
    px, py = pts[other_point]
    if horizontal_dir == "left":
        hx, hy = vx - 1, vy
    else:
        hx, hy = vx + 1, vy
    a_h = math.atan2(hy - vy, hx - vx)
    a_p = math.atan2(py - vy, px - vx)
    if a_p - a_h > math.pi:
        a_p -= 2 * math.pi
    elif a_p - a_h < -math.pi:
        a_p += 2 * math.pi
    th = np.linspace(a_h, a_p, 40)
    ax.plot(vx + theta_radius * np.cos(th),
            vy + theta_radius * np.sin(th), "k-", linewidth=0.9)
    mid = (a_h + a_p) / 2
    ax.text(vx + (theta_radius + 0.55) * math.cos(mid),
            vy + (theta_radius + 0.55) * math.sin(mid),
            "\u03b8", fontsize=13, ha="center", va="center")
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for name, (x, y) in pts.items():
        _label_radial(ax, x, y, name, away_from=(cx, cy))
    return _save(fig, out_path)


def render_analytical_circle(centre, radius, named_points,
                             tangents_from=None, tangent_points=None,
                             dashed_lines=None, right_angles=None,
                             xlim=None, ylim=None, out_path=None):
    cx, cy = centre
    if xlim is None:
        xlim = (cx - radius - 3, cx + radius + 3)
    if ylim is None:
        ylim = (cy - radius - 3, cy + radius + 3)
    fig, ax = plt.subplots(figsize=(7, 7))
    _dbe_axes(ax, xlim, ylim, "x", "y", grid=False, aspect="equal")
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx + radius * np.cos(th), cy + radius * np.sin(th),
            "k-", linewidth=1.2)
    if tangents_from and tangent_points:
        tx, ty = named_points[tangents_from]
        for tp in tangent_points:
            px, py = named_points[tp]
            ax.plot([tx, px], [ty, py], "k-", linewidth=1.0)
    if dashed_lines:
        for a, b in dashed_lines:
            x1, y1 = _resolve_point(a, named_points)
            x2, y2 = _resolve_point(b, named_points)
            ax.plot([x1, x2], [y1, y2], "k--", linewidth=0.9)
    if right_angles:
        for spec in right_angles:
            # Support both (v,) and (v, p1, p2)
            if isinstance(spec, (list, tuple)) and len(spec) == 3:
                v, p1, p2 = spec
                _right_angle(ax, _resolve_point(v, named_points),
                             _resolve_point(p1, named_points),
                             _resolve_point(p2, named_points))
            else:
                vx, vy = _resolve_point(spec, named_points)
                ax.plot(vx, vy, marker="s", markersize=8,
                        markerfacecolor="none", markeredgecolor="black")
    for name, (x, y) in named_points.items():
        _label_radial(ax, x, y, name, away_from=(cx, cy))
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "analytical_circle.png"
    return _save(fig, out_path)


def render_point_on_axes(point, radius=None, xlim=None, ylim=None,
                         extra_rays=None, label_point=True,
                         angle_arc=True, out_path=None):
    px, py = point
    if xlim is None:
        xlim = (min(px, 0) - 2, max(px, 0) + 3)
    if ylim is None:
        ylim = (min(py, 0) - 2, max(py, 0) + 2)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(),
            clip_on=False, markersize=6)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(),
            clip_on=False, markersize=6)
    ax.plot([0, px], [0, py], "k-", linewidth=1.2)
    if extra_rays:
        for (ex, ey) in extra_rays:
            ax.plot([0, ex], [0, ey], "k-", linewidth=1.0)
    ax.plot(px, py, "ko", markersize=5)
    if label_point:
        ax.text(px - 0.35, py + 0.35,
                f"P({px}; {py})".replace("-", "\u2013"),
                fontsize=11, ha="right", va="bottom")
    if angle_arc:
        a_end = math.atan2(py, px)
        if px < 0:
            a_end_pos = a_end if a_end > 0 else a_end + 2 * math.pi
        else:
            a_end_pos = a_end
        r_arc = min(2.0, abs(px) / 2 if px < 0 else abs(px) / 3)
        th = np.linspace(0, a_end_pos, 60)
        ax.plot(r_arc * np.cos(th), r_arc * np.sin(th),
                "k-", linewidth=1.0)
        mid = a_end_pos / 2
        r_lab = r_arc * 1.25
        ax.text(r_lab * math.cos(mid), r_lab * math.sin(mid),
                "\u03b8", fontsize=13, ha="center", va="center")
    ax.tick_params(labelsize=8, direction="out", length=3, width=0.8)
    ax.set_aspect("equal", adjustable="box")
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "point_on_axes.png"
    return _save(fig, out_path)


# ============================================================
# TRIG GRAPH
# ============================================================

def render_trig_graph(fn_specs, xlim, ylim, x_label="x", y_label="y",
                      grid=False, out_path=None):
    fig, ax = plt.subplots(figsize=(9, 5))
    _dbe_axes(ax, xlim, ylim, x_label, y_label, grid=grid, aspect="auto")
    x_ticks = np.arange(xlim[0], xlim[1] + 1, 45)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{int(t)}\u00b0" for t in x_ticks], fontsize=8)
    for spec in fn_specs:
        a, b = spec.get("coef", (1, 1))
        fn_name = spec.get("fn", "cos")
        label = spec.get("label", "")
        xr = spec.get("x_range", xlim)
        xs = np.linspace(xr[0], xr[1], 4000)
        rad = np.deg2rad(xs)
        if fn_name.startswith("cos"):
            ys = a * np.cos(b * rad)
        elif fn_name.startswith("sin"):
            ys = a * np.sin(b * rad)
        elif fn_name.startswith("tan"):
            ys = a * np.tan(b * rad)
            ys = np.where(np.abs(np.cos(b * rad)) < 0.008, np.nan, ys)
            ys = np.where((ys > ylim[1] + 1) | (ys < ylim[0] - 1),
                          np.nan, ys)
        else:
            raise ValueError(f"Unknown fn: {fn_name}")
        ax.plot(xs, ys, "k-", linewidth=1.3)
        if label:
            valid_idx = np.where(~np.isnan(ys))[0]
            if len(valid_idx):
                idx = valid_idx[int(len(valid_idx) * 0.75)]
                ax.text(xs[idx] + 3, ys[idx] + 0.15, label,
                        fontsize=11, style="italic")
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "trig_graph.png"
    return _save(fig, out_path)


# ============================================================
# 3D TRIG
# ============================================================

def render_three_d_trig(points_2d, edges, shaded_faces=None,
                        right_angles=None, angle_labels=None,
                        dashed_edges=None, ticks=None,
                        labels_below=None, edge_labels=None,
                        xlim=None, ylim=None, out_path=None):
    P = points_2d
    xs = [p[0] for p in P.values()]
    ys = [p[1] for p in P.values()]
    if xlim is None:
        xlim = (min(xs) - 1.5, max(xs) + 1.5)
    if ylim is None:
        ylim = (min(ys) - 1.5, max(ys) + 1.5)
    fig, ax = _blank_axes(xlim, ylim, figsize=(8, 6))
    if shaded_faces:
        for face in shaded_faces:
            poly = mpatches.Polygon([P[v] for v in face],
                                    closed=True,
                                    facecolor="#d9d9d9",
                                    edgecolor="black",
                                    linewidth=1.0,
                                    zorder=1)
            ax.add_patch(poly)
    if dashed_edges:
        for a, b in dashed_edges:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=0.9, zorder=2)
    if edges:
        for a, b in edges:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.2, zorder=3)
    if right_angles:
        for v, p1, p2 in right_angles:
            _right_angle(ax, P[v], P[p1], P[p2])
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"),
                       r_label=spec.get("r_label"),
                       label_xy=spec.get("label_xy"))
    if ticks:
        for p1, p2, n in ticks:
            _tick(ax, P[p1], P[p2], n=n)
    if edge_labels:
        for key, txt in edge_labels.items():
            if isinstance(key, str) and "-" in key:
                a, b = key.split("-", 1)
            else:
                a, b = key
            _edge_label(ax, P[a], P[b], txt)
    labels_below = labels_below or []
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for name, (x, y) in P.items():
        if name in labels_below:
            ax.plot(x, y, "ko", markersize=4)
            ax.text(x, y - 0.5, name, fontsize=10, ha="center", va="top")
        else:
            _label_radial(ax, x, y, name, away_from=(cx, cy))
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "three_d_trig.png"
    return _save(fig, out_path)


# ============================================================
# EUCLIDEAN CIRCLE RENDERERS
# ============================================================

def render_circle_centre_angle(centre, radius, points_on_circle,
                               chords=None, angle_labels=None,
                               dashed_lines=None, construction=None,
                               produce=None,
                               xlim=None, ylim=None, out_path=None):
    cx, cy = centre
    pad = 1.4
    if xlim is None:
        xlim = (cx - radius - pad, cx + radius + pad)
    if ylim is None:
        ylim = (cy - radius - pad, cy + radius + pad)
    fig, ax = _blank_axes(xlim, ylim, figsize=(6, 6))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx + radius * np.cos(th), cy + radius * np.sin(th),
            "k-", linewidth=1.3)
    P = {}
    for name, deg in points_on_circle.items():
        P[name] = _circle_xy(cx, cy, radius, deg)
    P["O"] = (cx, cy)
    if chords:
        for a, b in chords:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.1)
    if dashed_lines:
        for a, b in dashed_lines:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=0.9)
    if produce:
        a, b, frac = produce
        ax_, ay_ = P[a]
        bx_, by_ = P[b]
        ex = bx_ + (bx_ - ax_) * frac
        ey = by_ + (by_ - ay_) * frac
        ax.plot([ax_, ex], [ay_, ey], "k-", linewidth=1.0)
    if construction:
        a, b = construction
        ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                "k--", linewidth=1.0)
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"),
                       r_label=spec.get("r_label"))
    for name in points_on_circle:
        _label_radial(ax, P[name][0], P[name][1], name,
                      away_from=(cx, cy))
    if "O" not in points_on_circle:
        ax.plot(cx, cy, "ko", markersize=4)
        ax.text(cx - 0.3, cy, "O", fontsize=11, ha="right", va="center")
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "circle_centre_angle.png"
    return _save(fig, out_path)


def render_circle_tangent(centre, radius, points_on_circle,
                          external_points=None,
                          tangents=None, chords=None,
                          right_angles=None, angle_labels=None,
                          dashed_lines=None, ticks=None, edge_labels=None,
                          xlim=None, ylim=None, out_path=None):
    cx, cy = centre
    if xlim is None:
        xlim = (cx - radius - 4, cx + radius + 4)
    if ylim is None:
        ylim = (cy - radius - 3, cy + radius + 3)
    fig, ax = _blank_axes(xlim, ylim, figsize=(7, 6))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx + radius * np.cos(th), cy + radius * np.sin(th),
            "k-", linewidth=1.3)
    P = {}
    for name, deg in points_on_circle.items():
        P[name] = _circle_xy(cx, cy, radius, deg)
    P["O"] = (cx, cy)
    if external_points:
        P.update(external_points)
    if chords:
        for a, b in chords:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.1)
    if tangents:
        for ext, touch in tangents:
            ax.plot([P[ext][0], P[touch][0]],
                    [P[ext][1], P[touch][1]], "k-", linewidth=1.1)
    if dashed_lines:
        for a, b in dashed_lines:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=0.9)
    if right_angles:
        for v, p1, p2 in right_angles:
            _right_angle(ax, P[v], P[p1], P[p2])
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"),
                       r_label=spec.get("r_label"),
                       label_xy=spec.get("label_xy"))
    if ticks:
        for p1, p2, n in ticks:
            _tick(ax, P[p1], P[p2], n=n)
    if edge_labels:
        for key, txt in edge_labels.items():
            if isinstance(key, str) and "-" in key:
                a, b = key.split("-", 1)
            else:
                a, b = key
            _edge_label(ax, P[a], P[b], txt)
    for name in points_on_circle:
        _label_radial(ax, P[name][0], P[name][1], name,
                      away_from=(cx, cy))
    if external_points:
        for name, (x, y) in external_points.items():
            _label_radial(ax, x, y, name, away_from=(cx, cy))
    if "O" not in points_on_circle:
        ax.plot(cx, cy, "ko", markersize=4)
        ax.text(cx - 0.3, cy, "O", fontsize=11, ha="right", va="center")
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "circle_tangent.png"
    return _save(fig, out_path)


def render_circle_cyclic_quad(centre, radius, points_on_circle,
                              chords=None, diagonals=None,
                              external_points=None, right_angles=None,
                              angle_labels=None, dashed_lines=None,
                              ticks=None, edge_labels=None,
                              xlim=None, ylim=None, out_path=None):
    cx, cy = centre
    if xlim is None:
        xlim = (cx - radius - 2, cx + radius + 2)
    if ylim is None:
        ylim = (cy - radius - 2, cy + radius + 2)
    fig, ax = _blank_axes(xlim, ylim, figsize=(7, 6))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx + radius * np.cos(th), cy + radius * np.sin(th),
            "k-", linewidth=1.3)
    P = {}
    for name, deg in points_on_circle.items():
        P[name] = _circle_xy(cx, cy, radius, deg)
    P["O"] = (cx, cy)
    if external_points:
        P.update(external_points)
    if chords:
        for a, b in chords:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.1)
    if diagonals:
        for a, b in diagonals:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.1)
    if dashed_lines:
        for a, b in dashed_lines:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=0.9)
    if right_angles:
        for v, p1, p2 in right_angles:
            _right_angle(ax, P[v], P[p1], P[p2])
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"),
                       r_label=spec.get("r_label"),
                       label_xy=spec.get("label_xy"))
    if ticks:
        for p1, p2, n in ticks:
            _tick(ax, P[p1], P[p2], n=n)
    if edge_labels:
        for key, txt in edge_labels.items():
            if isinstance(key, str) and "-" in key:
                a, b = key.split("-", 1)
            else:
                a, b = key
            _edge_label(ax, P[a], P[b], txt)
    for name in points_on_circle:
        _label_radial(ax, P[name][0], P[name][1], name,
                      away_from=(cx, cy))
    if external_points:
        for name, (x, y) in external_points.items():
            _label_radial(ax, x, y, name, away_from=(cx, cy))
    if "O" not in points_on_circle:
        ax.plot(cx, cy, "ko", markersize=4)
        ax.text(cx - 0.3, cy, "O", fontsize=11, ha="right", va="center")
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "circle_cyclic_quad.png"
    return _save(fig, out_path)


def render_circle_similarity(circle_a, circle_b, points,
                             segments=None, dashed_lines=None,
                             angle_labels=None, ticks=None,
                             external_points=None,
                             xlim=None, ylim=None, out_path=None):
    if xlim is None:
        minx = min(circle_a[0] - circle_a[2], circle_b[0] - circle_b[2]) - 2
        maxx = max(circle_a[0] + circle_a[2], circle_b[0] + circle_b[2]) + 2
        xlim = (minx, maxx)
    if ylim is None:
        miny = min(circle_a[1] - circle_a[2], circle_b[1] - circle_b[2]) - 2
        maxy = max(circle_a[1] + circle_a[2], circle_b[1] + circle_b[2]) + 2
        ylim = (miny, maxy)
    fig, ax = _blank_axes(xlim, ylim, figsize=(8, 6))
    for (cx, cy, r) in (circle_a, circle_b):
        th = np.linspace(0, 2 * np.pi, 400)
        ax.plot(cx + r * np.cos(th), cy + r * np.sin(th),
                "k-", linewidth=1.2)
    P = dict(points)
    if external_points:
        P.update(external_points)
    if segments:
        for a, b in segments:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.1)
    if dashed_lines:
        for a, b in dashed_lines:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=0.9)
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"))
    if ticks:
        for p1, p2, n in ticks:
            _tick(ax, P[p1], P[p2], n=n)
    if circle_a and circle_b:
        ax_c = (circle_a[0] + circle_b[0]) / 2
        ay_c = (circle_a[1] + circle_b[1]) / 2
    else:
        ax_c = ay_c = 0
    for name, (x, y) in P.items():
        _label_radial(ax, x, y, name, away_from=(ax_c, ay_c))
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "circle_similarity.png"
    return _save(fig, out_path)


def render_triangle_proportion(points, segments=None, dashed_lines=None,
                               external_points=None,
                               angle_labels=None, ticks=None,
                               right_angles=None,
                               parallel_marks=None,
                               xlim=None, ylim=None, out_path=None):
    P = dict(points)
    if external_points:
        P.update(external_points)
    xs = [p[0] for p in P.values()]
    ys = [p[1] for p in P.values()]
    if xlim is None:
        xlim = (min(xs) - 1.5, max(xs) + 1.5)
    if ylim is None:
        ylim = (min(ys) - 1.5, max(ys) + 1.5)
    fig, ax = _blank_axes(xlim, ylim, figsize=(8, 6))
    if segments:
        for a, b in segments:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k-", linewidth=1.2)
    if dashed_lines:
        for a, b in dashed_lines:
            ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                    "k--", linewidth=1.0)
    if parallel_marks:
        for a, b in parallel_marks:
            mx = (P[a][0] + P[b][0]) / 2
            my = (P[a][1] + P[b][1]) / 2
            ax.plot(mx, my, marker=">", markersize=6,
                    markerfacecolor="black", markeredgecolor="black")
    if right_angles:
        for v, p1, p2 in right_angles:
            _right_angle(ax, P[v], P[p1], P[p2])
    if angle_labels:
        for spec in angle_labels:
            _angle_arc(ax, P[spec["vertex"]],
                       P[spec["p1"]], P[spec["p2"]],
                       label=spec.get("label"),
                       numbered=spec.get("numbered"),
                       r_arc=spec.get("r_arc"))
    if ticks:
        for p1, p2, n in ticks:
            _tick(ax, P[p1], P[p2], n=n)
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for name, (x, y) in P.items():
        _label_radial(ax, x, y, name, away_from=(cx, cy))
    if out_path is None:
        out_path = _ROOT / "data" / "processed" / "diagrams" / "triangle_proportion.png"
    return _save(fig, out_path)
