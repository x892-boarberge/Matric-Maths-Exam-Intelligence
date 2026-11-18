"""Surgically patch render_diagrams.py for Tier 1 fixes.
Verifies every anchor before touching the file. Refuses to apply twice.
"""
import sys
from pathlib import Path

target = Path("scripts/render_diagrams.py")
if not target.exists():
    print("FATAL: scripts/render_diagrams.py not found. Run from repo root.")
    sys.exit(1)

# Backup first
import datetime
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if 'status = "partial"' in src:
    print("FATAL: patch already appears applied (found 'status = \"partial\"' in file).")
    print("       Restore from backup if you need to re-run.")
    sys.exit(1)

# =========================================================================
# PATCH 1: Insert _parse_log_base_only + render_log_only before RENDERER_MAP
# =========================================================================

patch1_old = "RENDERER_MAP = {"
patch1_new = '''def _parse_log_base_only(text):
    """Extract base from 'f(x) = log_{N}(x)' or 'f(x) = log_N(x)' — for x-intercept-only variants."""
    m = re.search(r"log_\\{?([0-9/.]+)\\}?\\(x\\)", text)
    if m:
        try:
            return Fraction(m.group(1))
        except (ValueError, ZeroDivisionError):
            return None
    return None

def render_log_only(base, out_path):
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
    return _save(fig, out_path)

RENDERER_MAP = {'''

if patch1_old not in src:
    print("FATAL: Patch 1 anchor (RENDERER_MAP = {) not found.")
    sys.exit(1)
src = src.replace(patch1_old, patch1_new, 1)
print("Patch 1 applied: _parse_log_base_only + render_log_only inserted.")

# =========================================================================
# PATCH 2: Replace _apply_pool entirely
# =========================================================================

patch2_old = '''def _apply_pool(pool_name, kind, pool_data):
    """Render each variant in pool. Returns (rendered, skipped, note_count)."""
    out_subdir = OUT_DIR / pool_name
    out_subdir.mkdir(parents=True, exist_ok=True)
    rendered = 0
    skipped = 0
    notes = 0
    for i, v in enumerate(pool_data, 1):
        try:
            out_path = out_subdir / f"v{i:02d}.png"
            ok = False
            if kind == "log":
                p = _parse_log_variant(v["variant_question"])
                if p:
                    base, x_m, var, note = p
                    ok = render_log(base, x_m, var, out_path)
                    if note:
                        v["diagram_note"] = note
                        notes += 1
            elif kind == "blank":
                ok = render_blank_axes(out_path)
            elif kind in ("parabola", "parabola_with_line", "parabola_with_point", "parabola_with_tangent"):
                p = _parse_parabola_vertex(v["variant_question"])
                if p:
                    a, h, k = p
                    kwargs = {}
                    if kind == "parabola_with_line":
                        m_line = re.search(r"less than\\s*(-?\\d+)", v["variant_question"])
                        if m_line: kwargs["mark_line"] = int(m_line.group(1))
                    if kind == "parabola_with_tangent":
                        m_t = re.search(r"tangent.*?at x = (-?\\d+)", v["variant_question"])
                        if m_t:
                            x0 = int(m_t.group(1))
                            y0 = a*(x0-h)**2 + k
                            m_slope = 2*a*(x0-h)
                            kwargs["tangent"] = (x0, y0, m_slope)
                    ok = render_parabola(a, h, k, out_path, **kwargs)
            elif kind == "hyperbola":
                p = _parse_hyperbola(v["variant_question"])
                if p:
                    ok = render_hyperbola(*p, out_path)
            elif kind == "overlay":
                p = _parse_overlay(v["variant_question"])
                if p:
                    ok = render_overlay(*p, out_path)
            elif kind == "cubic":
                p = _parse_cubic(v["variant_question"])
                if p:
                    ok = render_cubic_with_tangents(p, out_path)
            elif kind == "cylinder":
                ok = render_cylinder(out_path)
            elif kind == "table":
                p = _parse_contingency(v["variant_question"])
                if p:
                    ok = render_table(p, out_path)
            if ok:
                v["diagram_path"] = str(out_path)
                v["diagram_status"] = "rendered"
                rendered += 1
            else:
                skipped += 1
        except Exception as e:
            skipped += 1
    return rendered, skipped, notes'''

patch2_new = '''def _apply_pool(pool_name, kind, pool_data):
    """Render each variant in pool. Returns (rendered, partial, skipped, note_count)."""
    out_subdir = OUT_DIR / pool_name
    out_subdir.mkdir(parents=True, exist_ok=True)
    rendered = 0
    partial = 0
    skipped = 0
    notes = 0
    for i, v in enumerate(pool_data, 1):
        try:
            out_path = out_subdir / f"v{i:02d}.png"
            status = "skipped"
            partial_reason = None
            if kind == "log":
                p = _parse_log_variant(v["variant_question"])
                if p:
                    base, x_m, var, note = p
                    if render_log(base, x_m, var, out_path):
                        status = "rendered"
                    if note:
                        v["diagram_note"] = note
                        notes += 1
                else:
                    base = _parse_log_base_only(v["variant_question"])
                    if base is not None and render_log_only(base, out_path):
                        status = "rendered"
                        v["diagram_note"] = "log-only (no marked point in variant text)"
            elif kind == "blank":
                if render_blank_axes(out_path):
                    status = "rendered"
            elif kind in ("parabola", "parabola_with_line", "parabola_with_point", "parabola_with_tangent"):
                p = _parse_parabola_vertex(v["variant_question"])
                if p:
                    a, h, k = p
                    kwargs = {}
                    if kind == "parabola_with_line":
                        m_line = re.search(r"less than\\s*(-?\\d+)", v["variant_question"])
                        if m_line:
                            kwargs["mark_line"] = int(m_line.group(1))
                        else:
                            partial_reason = "horizontal line value not parsed (rendered bare parabola)"
                    if kind == "parabola_with_point":
                        m_pt = re.search(r"([DP])\\s+(?:is|lies|has).*?x\\s*=\\s*(-?\\d+)", v["variant_question"])
                        if m_pt:
                            px = int(m_pt.group(2))
                            py = a * (px - h)**2 + k
                            kwargs["mark_point"] = (px, py, m_pt.group(1))
                        else:
                            partial_reason = "mark_point (D/P) not parsed (rendered bare parabola)"
                    if kind == "parabola_with_tangent":
                        m_t = re.search(r"tangent.*?at x = (-?\\d+)", v["variant_question"])
                        if m_t:
                            x0 = int(m_t.group(1))
                            y0 = a*(x0-h)**2 + k
                            kwargs["tangent"] = (x0, y0, 2*a*(x0-h))
                        else:
                            partial_reason = "tangent point not parsed"
                    if render_parabola(a, h, k, out_path, **kwargs):
                        status = "partial" if partial_reason else "rendered"
            elif kind == "hyperbola":
                p = _parse_hyperbola(v["variant_question"])
                if p and render_hyperbola(*p, out_path):
                    status = "rendered"
            elif kind == "overlay":
                p = _parse_overlay(v["variant_question"])
                if p and render_overlay(*p, out_path):
                    if pool_name == "5.5":
                        status = "partial"
                        partial_reason = "M and T intercepts not marked (renderer lacks mark_intercepts)"
                    else:
                        status = "rendered"
            elif kind == "cubic":
                p = _parse_cubic(v["variant_question"])
                if p and render_cubic_with_tangents(p, out_path):
                    status = "partial"
                    partial_reason = "A/B/C/D/E labels not added (pending Tier 3)"
            elif kind == "cylinder":
                if render_cylinder(out_path):
                    status = "rendered"
            elif kind == "table":
                p = _parse_contingency(v["variant_question"])
                if p and render_table(p, out_path):
                    status = "rendered"

            if status == "rendered":
                v["diagram_path"] = str(out_path)
                v["diagram_status"] = "rendered"
                v.pop("diagram_partial_reason", None)
                rendered += 1
            elif status == "partial":
                v["diagram_path"] = str(out_path)
                v["diagram_status"] = "partial"
                if partial_reason:
                    v["diagram_partial_reason"] = partial_reason
                partial += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"    {pool_name} v{i:02d}: {type(e).__name__}: {e}")
            skipped += 1
    return rendered, partial, skipped, notes'''

if patch2_old not in src:
    print("FATAL: Patch 2 anchor (_apply_pool) not found.")
    sys.exit(1)
src = src.replace(patch2_old, patch2_new, 1)
print("Patch 2 applied: _apply_pool replaced (partial tracking + 5.4 mark_point + 4.2 fallback).")

# =========================================================================
# PATCH 3: Replace main()
# =========================================================================

patch3_old = '''def main():
    print("=== Batch renderer ===\\n")
    total_rendered = 0
    total_skipped = 0
    summary = []
    for pool_name, kind in RENDERER_MAP.items():
        p = POOL_DIR / f"{pool_name}_pool.json"
        if not p.exists():
            print(f"  {pool_name}: pool file missing")
            continue
        pool = json.loads(p.read_text(encoding="utf-8-sig"))
        print(f"  {pool_name} ({kind}): ", end="", flush=True)
        rendered, skipped, notes = _apply_pool(pool_name, kind, pool)
        # Backup and write
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
        p.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{rendered} rendered, {skipped} skipped" + (f", {notes} notes" if notes else ""))
        summary.append((pool_name, rendered, skipped, notes))
        total_rendered += rendered
        total_skipped += skipped
    
    # Mark NOT_REQUIRED pools
    print("\\n=== Marking not_required ===")
    for pool_name in NOT_REQUIRED:
        p = POOL_DIR / f"{pool_name}_pool.json"
        if not p.exists():
            continue
        pool = json.loads(p.read_text(encoding="utf-8-sig"))
        for v in pool:
            v["diagram"] = "not_required"
            v["diagram_hint"] = None
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
        p.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  {len(NOT_REQUIRED)} pools marked not_required")
    
    # Summary
    print(f"\\n=== TOTAL ===")
    print(f"Rendered: {total_rendered}")
    print(f"Skipped:  {total_skipped}")
    print(f"\\nPer-pool:")
    for name, r, s, n in summary:
        print(f"  {name:8}  {r:2}/{r+s:2} rendered" + (f"  ({n} with notes)" if n else ""))


if __name__ == "__main__":
    main()'''

patch3_new = '''def main():
    print("=== Batch renderer ===\\n")
    total_rendered = 0
    total_partial = 0
    total_skipped = 0
    summary = []
    for pool_name, kind in RENDERER_MAP.items():
        p = POOL_DIR / f"{pool_name}_pool.json"
        if not p.exists():
            print(f"  {pool_name}: pool file missing")
            continue
        pool = json.loads(p.read_text(encoding="utf-8-sig"))
        print(f"  {pool_name} ({kind}): ", end="", flush=True)
        rendered, partial, skipped, notes = _apply_pool(pool_name, kind, pool)
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
        p.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")
        msg = f"{rendered} rendered"
        if partial: msg += f", {partial} partial"
        if skipped: msg += f", {skipped} skipped"
        if notes:   msg += f", {notes} notes"
        print(msg)
        summary.append((pool_name, rendered, partial, skipped, notes))
        total_rendered += rendered
        total_partial += partial
        total_skipped += skipped

    print("\\n=== Marking not_required ===")
    for pool_name in NOT_REQUIRED:
        p = POOL_DIR / f"{pool_name}_pool.json"
        if not p.exists():
            continue
        pool = json.loads(p.read_text(encoding="utf-8-sig"))
        for v in pool:
            v["diagram"] = "not_required"
            v["diagram_hint"] = None
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
        p.write_text(json.dumps(pool, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  {len(NOT_REQUIRED)} pools marked not_required")

    print(f"\\n=== TOTAL ===")
    print(f"Rendered: {total_rendered}")
    print(f"Partial:  {total_partial}  (content incomplete — see breakdown below)")
    print(f"Skipped:  {total_skipped}")
    print(f"\\nPer-pool:")
    for name, r, pa, s, n in summary:
        parts = f"{r} rendered"
        if pa: parts += f", {pa} partial"
        if s:  parts += f", {s} skipped"
        if n:  parts += f" ({n} notes)"
        total = r + pa + s
        print(f"  {name:8}  {parts}  [{r}/{total} correct]")

    print(f"\\n=== Partial breakdown ===")
    reasons = {}
    for pool_name in RENDERER_MAP:
        p = POOL_DIR / f"{pool_name}_pool.json"
        if not p.exists():
            continue
        pool = json.loads(p.read_text(encoding="utf-8-sig"))
        for v in pool:
            if v.get("diagram_status") == "partial":
                reason = v.get("diagram_partial_reason", "unknown")
                reasons[reason] = reasons.get(reason, 0) + 1
    if reasons:
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {count:3}× {reason}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()'''

if patch3_old not in src:
    print("FATAL: Patch 3 anchor (main) not found.")
    sys.exit(1)
src = src.replace(patch3_old, patch3_new, 1)
print("Patch 3 applied: main() replaced (partial reporting + breakdown).")

# Write back
target.write_text(src, encoding="utf-8")
print(f"\nAll three patches applied. File: {target}")
print("Run: py -m py_compile scripts/render_diagrams.py")
