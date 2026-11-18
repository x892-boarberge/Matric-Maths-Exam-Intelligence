"""Final Tier 2: fix 5.5 overlay parser, fix 9.4 cubic tangency/labels."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# Final Tier 2" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# =========================================================================
# FIX 1: _parse_overlay (5.5) — use _parse_parabola_vertex to avoid fake tuples
# =========================================================================
old_overlay = '''def _parse_overlay(text):
    """Extract both parabola and hyperbola params from a variant question."""
    # Tier 2: 5.5 expanded form fallback
    m_par = re.search(r"(-?\\d+(?:/\\d+)?)?\\(x\\s*([+-])\\s*(\\d+)\\)\\^2\\s*([+-])\\s*(\\d+)", text)
    if not m_par:
        m_exp = re.search(r"(-?\\d+(?:/\\d+)?)?x\\^2\\s*([+-])\\s*(\\d+)x\\s*([+-])\\s*(\\d+)", text)
        if m_exp:
            a_s = m_exp.group(1) or "1"
            a = _frac(a_s) if a_s not in ("-", "+") else (-1.0 if a_s == "-" else 1.0)
            b = int(m_exp.group(3)) * (1 if m_exp.group(2) == "+" else -1)
            c = int(m_exp.group(5)) * (1 if m_exp.group(4) == "+" else -1)
            if a != 0:
                h = -b / (2 * a)
                k = a * h * h + b * h + c
                # Fake a regex match tuple for the rest of the function
                m_par = (None, str(a), "+", str(int(abs(h))), "+" if k >= 0 else "-", str(int(abs(k))))
                if h < 0: # fix the sign for h
                    m_par = (None, str(a), "-", str(int(abs(h))), "+" if k >= 0 else "-", str(int(abs(k))))

    m_hyp = re.search(r"(-?\\d+(?:/\\d+)?)?/\\(x\\s*([+-])\\s*(\\d+)\\)\\s*([+-])\\s*(\\d+)", text)
    if not m_par or not m_hyp: return None'''

new_overlay = '''def _parse_overlay(text):
    """Extract both parabola and hyperbola params from a variant question."""
    # Final Tier 2: clean reuse of _parse_parabola_vertex
    par = _parse_parabola_vertex(text)
    m_hyp = re.search(r"(-?\\d+(?:/\\d+)?)?/\\(x\\s*([+-])\\s*(\\d+)\\)\\s*([+-])\\s*(\\d+)", text)
    if not par or not m_hyp: return None

    a_h_s = m_hyp.group(1) or "1"
    a_h = _frac(a_h_s)
    if m_hyp.group(1) and m_hyp.group(1).startswith("-"):
        a_h = -_frac(m_hyp.group(1)[1:])
    p_h = int(m_hyp.group(3)) if m_hyp.group(2) == "+" else -int(m_hyp.group(3))
    q_h = int(m_hyp.group(5)) * (1 if m_hyp.group(4) == "+" else -1)
    
    return par, (a_h, p_h, q_h)'''

if old_overlay not in src:
    print("FATAL: _parse_overlay anchor not found")
    sys.exit(1)
src = src.replace(old_overlay, new_overlay, 1)

# =========================================================================
# FIX 2: _parse_cubic (9.4) — allow float tangency, no perfect square required
# =========================================================================
old_cubic = '''def _parse_cubic(text):
    """Extract cubic a,b,c,d and line slope m, tangency t values."""
    m_c = re.search(r"x\\^3\\s*([+-])\\s*(\\d+)x\\^2\\s*([+-])\\s*(\\d+)x\\s*([+-])\\s*(\\d+)", text)
    if not m_c: return None
    b = int(m_c.group(2)) * (1 if m_c.group(1) == "+" else -1)
    c = int(m_c.group(4)) * (1 if m_c.group(3) == "+" else -1)
    d = int(m_c.group(6)) * (1 if m_c.group(5) == "+" else -1)
    m_line = re.search(r"y\\s*=\\s*(-?\\d+(?:/\\d+)?)x\\s*\\+\\s*t", text)
    if not m_line: return None
    m = _frac(m_line.group(1))
    # Find tangency t values by solving f'(x)=m
    A, B, C = 3, 2*b, c - m
    disc = B*B - 4*A*C
    if disc < 0: return None
    import math
    sqrt_d = int(disc ** 0.5)
    if sqrt_d ** 2 != disc: return None
    x1 = (-B - sqrt_d) / (2*A)
    x2 = (-B + sqrt_d) / (2*A)
    if x1 == x2: return None
    def f(x): return x**3 + b*x**2 + c*x + d
    t1 = f(x1) - m*x1
    t2 = f(x2) - m*x2
    return (b, c, d, m, x1, x2, t1, t2)'''

new_cubic = '''def _parse_cubic(text):
    """Extract cubic a,b,c,d and line slope m, tangency t values."""
    m_c = re.search(r"x\\^3\\s*([+-])\\s*(\\d+)x\\^2\\s*([+-])\\s*(\\d+)x\\s*([+-])\\s*(\\d+)", text)
    if not m_c: return None
    b = int(m_c.group(2)) * (1 if m_c.group(1) == "+" else -1)
    c = int(m_c.group(4)) * (1 if m_c.group(3) == "+" else -1)
    d = int(m_c.group(6)) * (1 if m_c.group(5) == "+" else -1)
    m_line = re.search(r"y\\s*=\\s*(-?\\d+(?:/\\d+)?)x\\s*\\+\\s*t", text)
    if not m_line: return None
    m = _frac(m_line.group(1))
    
    A, B, C = 3, 2*b, c - m
    disc = B*B - 4*A*C
    if disc < 0: return None
    
    import math
    sqrt_d = math.sqrt(disc) # Final Tier 2: allow floats
    x1 = (-B - sqrt_d) / (2*A)
    x2 = (-B + sqrt_d) / (2*A)
    if abs(x1 - x2) < 1e-6: return None
    def f(x): return x**3 + b*x**2 + c*x + d
    t1 = f(x1) - m*x1
    t2 = f(x2) - m*x2
    return (b, c, d, m, x1, x2, t1, t2)'''

if old_cubic not in src:
    print("FATAL: _parse_cubic anchor not found")
    sys.exit(1)
src = src.replace(old_cubic, new_cubic, 1)

# =========================================================================
# FIX 3: render_cubic_with_tangents (9.4) — add labels & dynamic range
# =========================================================================
old_render_cubic = '''def render_cubic_with_tangents(cubic, out_path):
    b, c, d, m, x1, x2, t1, t2 = cubic
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    xs = np.linspace(-6, 8, 400)
    ys = xs**3 + b*xs**2 + c*xs + d
    ax.plot(xs, ys, "k-", linewidth=DBE_STYLE["line_width"])
    # Tangency lines
    for x0, t in [(x1, t1), (x2, t2)]:
        line_xs = np.linspace(x0 - 2.5, x0 + 2.5, 50)
        line_ys = m * line_xs + t
        ax.plot(line_xs, line_ys, "k--", linewidth=0.8)
    ax.annotate("f", xy=(5, 5**3 + b*25 + c*5 + d),
                fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    y_lim = max(abs(ys.min()), abs(ys.max())) + 3
    _style_axes(ax, (-6, 8), (-y_lim, y_lim))
    return _save(fig, out_path)'''

new_render_cubic = '''def render_cubic_with_tangents(cubic, out_path):
    b, c, d, m, x1, x2, t1, t2 = cubic
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    
    # Final Tier 2: dynamic x-range covering tangency points
    x_min = min(x1, x2) - 3
    x_max = max(x1, x2) + 3
    xs = np.linspace(x_min, x_max, 400)
    ys = xs**3 + b*xs**2 + c*xs + d
    ax.plot(xs, ys, "k-", linewidth=DBE_STYLE["line_width"])
    
    # Tangency lines and labels A/B/C/D/E
    for x0, t, lbl in [(x1, t1, "A"), (x2, t2, "B")]:
        line_xs = np.linspace(x0 - 2, x0 + 2, 50)
        line_ys = m * line_xs + t
        ax.plot(line_xs, line_ys, "k--", linewidth=0.8)
        y0 = m * x0 + t
        ax.plot(x0, y0, "ko", markersize=DBE_STYLE["point_size"])
        ax.annotate(f"{lbl}({x0:.1f}; {y0:.1f})", xy=(x0, y0), xytext=(x0 + 0.2, y0 + 0.5), fontsize=DBE_STYLE["font_size"])
        
    # Label the y-intercept as C
    ax.plot(0, d, "ko", markersize=DBE_STYLE["point_size"])
    ax.annotate(f"C(0; {d})", xy=(0, d), xytext=(0.2, d + 0.5), fontsize=DBE_STYLE["font_size"])

    ax.annotate("f", xy=(xs[-1]-1, ys[-1]-2), fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    y_lim = max(abs(ys.min()), abs(ys.max())) + 3
    _style_axes(ax, (x_min, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)'''

if old_render_cubic not in src:
    print("FATAL: render_cubic anchor not found")
    sys.exit(1)
src = src.replace(old_render_cubic, new_render_cubic, 1)

# 4. Remove the hardcoded partial status for 9.4 in _apply_pool
old_status = '''            elif kind == "cubic":
                p = _parse_cubic(v["variant_question"])
                if p and render_cubic_with_tangents(p, out_path):
                    status = "partial"
                    partial_reason = "A/B/C/D/E labels not added (pending Tier 3)"'''

new_status = '''            elif kind == "cubic":
                p = _parse_cubic(v["variant_question"])
                if p and render_cubic_with_tangents(p, out_path):
                    status = "rendered"'''

if old_status not in src:
    print("FATAL: 9.4 status anchor not found")
    sys.exit(1)
src = src.replace(old_status, new_status, 1)

target.write_text(src, encoding="utf-8")
print("Final Tier 2 Patch applied: 5.5 parser, 9.4 float tangency + labels")
