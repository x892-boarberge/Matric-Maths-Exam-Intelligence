"""Final Tier 2: Add mark_intercepts to 5.5 overlay."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "mark_intercepts=False" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# 1. Update render_overlay signature and add intercept logic
old_overlay = '''def render_overlay(par, hyp, out_path):
    a, h, k = par
    a_h, p_h, q_h = hyp'''

new_overlay = '''def render_overlay(par, hyp, out_path, mark_intercepts=False):
    a, h, k = par
    a_h, p_h, q_h = hyp'''

src = src.replace(old_overlay, new_overlay, 1)

# 2. Insert the point plotting logic right before the y_lim calculation in render_overlay
old_yvals = '''    y_vals = np.concatenate([ys, [q_h - abs(a_h), q_h + abs(a_h)]])
    y_lim = max(abs(y_vals.min()), abs(y_vals.max())) + 2'''

new_yvals = '''    # Final Tier 2: Mark intercepts M (parabola) and T (hyperbola)
    if mark_intercepts:
        if a != 0 and -k/a >= 0:
            m_x = h + np.sqrt(-k/a)
            ax.plot(m_x, 0, "ko", markersize=DBE_STYLE["point_size"])
            ax.annotate(f"M({m_x:.1f}; 0)", xy=(m_x, 0), xytext=(m_x + 0.2, 0.5), fontsize=DBE_STYLE["font_size"])
        if q_h != 0:
            t_x = -a_h/q_h - p_h
            ax.plot(t_x, 0, "ko", markersize=DBE_STYLE["point_size"])
            ax.annotate(f"T({t_x:.1f}; 0)", xy=(t_x, 0), xytext=(t_x + 0.2, -0.5), fontsize=DBE_STYLE["font_size"])

    y_vals = np.concatenate([ys, [q_h - abs(a_h), q_h + abs(a_h)]])
    y_lim = max(abs(y_vals.min()), abs(y_vals.max())) + 2'''

if old_yvals not in src:
    print("FATAL: render_overlay y_vals anchor not found")
    sys.exit(1)
src = src.replace(old_yvals, new_yvals, 1)

# 3. Update _apply_pool to pass mark_intercepts=True for 5.5
old_apply = '''            elif kind == "overlay":
                p = _parse_overlay(v["variant_question"])
                if p and render_overlay(*p, out_path):
                    if pool_name == "5.5":
                        status = "partial"
                        partial_reason = "M and T intercepts not marked (renderer lacks mark_intercepts)"
                    else:
                        status = "rendered"'''

new_apply = '''            elif kind == "overlay":
                p = _parse_overlay(v["variant_question"])
                if p:
                    kwargs = {}
                    if pool_name == "5.5":
                        kwargs["mark_intercepts"] = True
                    if render_overlay(*p, out_path, **kwargs):
                        status = "rendered"'''

if old_apply not in src:
    print("FATAL: _apply_pool overlay anchor not found")
    sys.exit(1)
src = src.replace(old_apply, new_apply, 1)

target.write_text(src, encoding="utf-8")
print("Final Tier 2 Patch applied: mark_intercepts added to 5.5")
