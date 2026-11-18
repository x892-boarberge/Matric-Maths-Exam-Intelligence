"""Fix log curve rendering: smoother asymptote, thinner lines, better labels."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# aesthetic fix" in src:
    print("FATAL: patch appears already applied")
    sys.exit(1)

# 1. Thinner lines, smaller points
old_style = '''DBE_STYLE = {
    "figsize": (5, 4.2),
    "wide_figsize": (6.5, 4),
    "dpi": 150,
    "line_width": 1.4,
    "point_size": 5,
    "font_size": 10,
    "label_size": 11,
}'''
new_style = '''DBE_STYLE = {
    # aesthetic fix: thinner lines, smaller markers for DBE exactness
    "figsize": (5, 4.2),
    "wide_figsize": (6.5, 4),
    "dpi": 150,
    "line_width": 1.0,
    "point_size": 4,
    "font_size": 11,
    "label_size": 11,
}'''
if old_style not in src:
    print("FATAL: DBE_STYLE anchor not found")
    sys.exit(1)
src = src.replace(old_style, new_style, 1)

# 2. Axis arrow heads smaller
old_axes = '    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=5)\n    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=5)'
new_axes = '    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=4)\n    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=4)'
if old_axes not in src:
    print("FATAL: _style_axes anchor not found")
    sys.exit(1)
src = src.replace(old_axes, new_axes, 1)

# 3. Replace render_log
old_log = '''def render_log(base, x_marked, var_name, out_path):
    base_f = float(base); x_f = float(x_marked)
    if base_f <= 0 or base_f == 1 or x_f <= 0: return False
    y_marked = float(np.log(x_f) / np.log(base_f))
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    x_max = max(x_f * 1.8, 5)
    xs = np.logspace(np.log10(0.05), np.log10(x_max), 400)
    ys = np.log(xs) / np.log(base_f)
    y_lim = max(abs(y_marked) * 2.5, 4)
    mask = (ys > -y_lim) & (ys < y_lim)
    ax.plot(xs[mask], ys[mask], "k-", linewidth=DBE_STYLE["line_width"])
    ax.plot(1, 0, "ko", markersize=DBE_STYLE["point_size"])
    ax.annotate("A", xy=(1, 0), xytext=(1.08, 0.25), fontsize=DBE_STYLE["label_size"], fontweight="bold")
    ax.plot(x_f, y_marked, "ko", markersize=DBE_STYLE["point_size"])
    x_disp = int(x_f) if x_f == int(x_f) else x_f
    y_off = 0.3 if base_f < 1 else -0.35
    ax.annotate(f"({x_disp:g}; {var_name})", xy=(x_f, y_marked),
                xytext=(x_f + 0.15, y_marked + y_off), fontsize=DBE_STYLE["font_size"])
    mid = len(xs[mask]) // 3
    if mid < len(xs[mask]):
        ax.annotate("f", xy=(xs[mask][mid], ys[mask][mid]),
                    xytext=(xs[mask][mid] - 0.15, ys[mask][mid] + 0.3),
                    fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    _style_axes(ax, (-0.5, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)'''

new_log = '''def render_log(base, x_marked, var_name, out_path):
    # aesthetic fix: smoother curve near asymptote, no artificial clipping mask
    base_f = float(base); x_f = float(x_marked)
    if base_f <= 0 or base_f == 1 or x_f <= 0: return False
    y_marked = float(np.log(x_f) / np.log(base_f))
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    x_max = max(x_f * 1.8, 5)
    
    # start very close to 0 for a smooth asymptote tail
    xs = np.logspace(-4, np.log10(x_max), 1000)
    ys = np.log(xs) / np.log(base_f)
    y_lim = max(abs(y_marked) * 2.5, 4)
    
    ax.plot(xs, ys, "k-", linewidth=DBE_STYLE["line_width"])
    
    ax.plot(1, 0, "ko", markersize=DBE_STYLE["point_size"])
    ax.annotate("A", xy=(1, 0), xytext=(1.1, 0.3 if base_f > 1 else -0.4), 
                fontsize=DBE_STYLE["label_size"], fontweight="bold")
                
    ax.plot(x_f, y_marked, "ko", markersize=DBE_STYLE["point_size"])
    x_disp = int(x_f) if x_f == int(x_f) else x_f
    y_off = 0.4 if base_f < 1 else -0.4
    ax.annotate(f"({x_disp:g}; {var_name})", xy=(x_f, y_marked),
                xytext=(x_f + 0.2, y_marked + y_off), fontsize=DBE_STYLE["font_size"])
                
    x_mid = min(2.0, x_max * 0.5)
    y_mid = np.log(x_mid) / np.log(base_f)
    ax.annotate("f", xy=(x_mid, y_mid), xytext=(x_mid + 0.2, y_mid + 0.2),
                fontsize=DBE_STYLE["label_size"], fontstyle="italic")
                
    _style_axes(ax, (-0.5, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)'''
if old_log not in src:
    print("FATAL: render_log anchor not found")
    sys.exit(1)
src = src.replace(old_log, new_log, 1)

# 4. Replace render_log_only
old_log_only = '''def render_log_only(base, out_path):
    """Render log curve with A at (1,0) only — used for x-intercept questions (4.2)."""
    try:
        base_f = float(base)
    except (ValueError, TypeError):
        return False
    if base_f <= 0 or base_f == 1:
        return False
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    x_max = 10
    xs = np.logspace(np.log10(0.05), np.log10(x_max), 400)
    ys = np.log(xs) / np.log(base_f)
    y_lim = 4
    mask = (ys > -y_lim) & (ys < y_lim)
    ax.plot(xs[mask], ys[mask], "k-", linewidth=DBE_STYLE["line_width"])
    ax.plot(1, 0, "ko", markersize=DBE_STYLE["point_size"])
    ax.annotate("A", xy=(1, 0), xytext=(1.08, 0.25),
                fontsize=DBE_STYLE["label_size"], fontweight="bold")
    mid = len(xs[mask]) // 3
    if 0 <= mid < len(xs[mask]):
        ax.annotate("f", xy=(xs[mask][mid], ys[mask][mid]),
                    xytext=(xs[mask][mid] - 0.15, ys[mask][mid] + 0.3),
                    fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    _style_axes(ax, (-0.5, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)'''

new_log_only = '''def render_log_only(base, out_path):
    """Render log curve with A at (1,0) only — used for x-intercept questions (4.2)."""
    # aesthetic fix: smoother curve near asymptote
    try:
        base_f = float(base)
    except (ValueError, TypeError):
        return False
    if base_f <= 0 or base_f == 1:
        return False
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    x_max = 10
    xs = np.logspace(-4, np.log10(x_max), 1000)
    ys = np.log(xs) / np.log(base_f)
    y_lim = 4
    
    ax.plot(xs, ys, "k-", linewidth=DBE_STYLE["line_width"])
    
    ax.plot(1, 0, "ko", markersize=DBE_STYLE["point_size"])
    ax.annotate("A", xy=(1, 0), xytext=(1.1, 0.3 if base_f > 1 else -0.4),
                fontsize=DBE_STYLE["label_size"], fontweight="bold")
                
    x_mid = min(2.0, x_max * 0.5)
    y_mid = np.log(x_mid) / np.log(base_f)
    ax.annotate("f", xy=(x_mid, y_mid), xytext=(x_mid + 0.2, y_mid + 0.2),
                fontsize=DBE_STYLE["label_size"], fontstyle="italic")
                
    _style_axes(ax, (-0.5, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)'''
if old_log_only not in src:
    print("FATAL: render_log_only anchor not found")
    sys.exit(1)
src = src.replace(old_log_only, new_log_only, 1)

target.write_text(src, encoding="utf-8")
print("Aesthetic patch applied to render_log and render_log_only")
