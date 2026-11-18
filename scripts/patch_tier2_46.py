"""Tier 2: Add two-curve log renderer for 4.6."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())

src = target.read_text(encoding="utf-8")

if "def render_log_translated_inverse" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# 1. Add the new renderer before RENDERER_MAP
new_renderer = '''
def render_log_translated_inverse(base, shift_right, out_path):
    # Renders f(x) = log_b(x) and h(x) = log_b(x - shift_right) for 4.6
    base_f = float(base); shift = float(shift_right)
    if base_f <= 0 or base_f == 1: return False
    fig, ax = plt.subplots(figsize=DBE_STYLE["figsize"], dpi=DBE_STYLE["dpi"])
    x_max = max(shift + 6, 10)
    
    # f(x)
    xs1 = np.logspace(-2, np.log10(x_max), 800)
    ys1 = np.log(xs1) / np.log(base_f)
    ax.plot(xs1, ys1, "k-", linewidth=DBE_STYLE["line_width"])
    
    # h(x) = f_inv(x - shift)
    xs2 = np.logspace(-2, np.log10(x_max + shift), 800) + shift
    ys2 = np.log(xs2 - shift) / np.log(base_f)
    ax.plot(xs2, ys2, "k-", linewidth=DBE_STYLE["line_width"])
    
    ax.annotate("f", xy=(2, np.log(2)/np.log(base_f)), xytext=(2.2, np.log(2)/np.log(base_f) + 0.2), fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    ax.annotate("h", xy=(shift + 2, np.log(2)/np.log(base_f)), xytext=(shift + 2.2, np.log(2)/np.log(base_f) + 0.2), fontsize=DBE_STYLE["label_size"], fontstyle="italic")
    
    y_lim = 4
    _style_axes(ax, (-1, x_max), (-y_lim, y_lim))
    return _save(fig, out_path)

RENDERER_MAP = {'''

src = src.replace("RENDERER_MAP = {", new_renderer, 1)

# 2. Map 4.6 to the new kind
src = src.replace('"4.6": "log",', '"4.6": "log_translated",', 1)

# 3. Hook up parser to _apply_pool
old_branch = '''            if kind == "log":
                p = _parse_log_variant(v["variant_question"])'''
new_branch = '''            if kind == "log_translated":
                _shift_match = re.search(r"(\\d+)\\s*units\\s*(?:horizontally)?\\s*right", v["variant_question"])
                _base_match = re.search(r"log_\\{?([0-9/.]+)\\}?\\(x\\)", v["variant_question"])
                if _shift_match and _base_match:
                    if render_log_translated_inverse(_base_match.group(1), _shift_match.group(1), out_path):
                        status = "rendered"
            elif kind == "log":
                p = _parse_log_variant(v["variant_question"])'''

if old_branch not in src:
    print("FATAL: _apply_pool log branch not found")
    sys.exit(1)
src = src.replace(old_branch, new_branch, 1)

target.write_text(src, encoding="utf-8")
print("Tier 2 patch 4.6 applied: two-curve log renderer added")
