"""Tier 2: 5.4 mark_point, 5.5 expanded form, 4.6 regex loosen."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "Tier 2: 5.5 expanded form" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# 1. Update _parse_overlay to handle expanded form
old_overlay = '''def _parse_overlay(text):
    """Extract both parabola and hyperbola params from a variant question."""
    # Find parabola form "a(x-h)^2 + k"
    m_par = re.search(r"(-?\\d+(?:/\\d+)?)?\\(x\\s*([+-])\\s*(\\d+)\\)\\^2\\s*([+-])\\s*(\\d+)", text)
    m_hyp = re.search(r"(-?\\d+(?:/\\d+)?)?/\\(x\\s*([+-])\\s*(\\d+)\\)\\s*([+-])\\s*(\\d+)", text)
    if not m_par or not m_hyp: return None'''

new_overlay = '''def _parse_overlay(text):
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

# Do the replacement safely
if old_overlay not in src:
    print("FATAL: _parse_overlay anchor not found")
    sys.exit(1)
src = src.replace(old_overlay, new_overlay, 1)

# 2. Fix 5.4 mark_point parsing in _apply_pool
old_pt = '''                    if kind == "parabola_with_point":
                        m_pt = re.search(r"([DP])\\s+(?:is|lies|has).*?x\\s*=\\s*(-?\\d+)", v["variant_question"])
                        if m_pt:
                            px = int(m_pt.group(2))
                            py = a * (px - h)**2 + k
                            kwargs["mark_point"] = (px, py, m_pt.group(1))
                        else:
                            partial_reason = "mark_point (D/P) not parsed (rendered bare parabola)"'''

new_pt = '''                    if kind == "parabola_with_point":
                        # Look for coordinate pair D(x; y) or P(x; y) first
                        m_pt = re.search(r"([DP])\\s*\\(\\s*(-?\\d+)\\s*;\\s*(-?\\d+)\\s*\\)", v["variant_question"])
                        if m_pt:
                            px, py = int(m_pt.group(2)), int(m_pt.group(3))
                            kwargs["mark_point"] = (px, py, m_pt.group(1))
                        else:
                            # Fallback: look for D is at x = ...
                            m_pt = re.search(r"([DP])\\s+(?:is|lies|has|at).*?x\\s*=\\s*(-?\\d+)", v["variant_question"])
                            if m_pt:
                                px = int(m_pt.group(2))
                                py = a * (px - h)**2 + k
                                kwargs["mark_point"] = (px, py, m_pt.group(1))
                            else:
                                partial_reason = "mark_point (D/P) not parsed (rendered bare parabola)"'''

if old_pt not in src:
    print("FATAL: 5.4 mark_point anchor not found")
    sys.exit(1)
src = src.replace(old_pt, new_pt, 1)

# 3. Loosen 4.6 shift regex to catch "to the right"
old_46 = '''                _shift_match = re.search(r"(\\d+)\\s*units\\s*(?:horizontally)?\\s*right", v["variant_question"])'''
new_46 = '''                _shift_match = re.search(r"(\\d+)\\s*units\\s*(?:horizontally\\s*)?(?:to the\\s*)?right", v["variant_question"])'''
if old_46 not in src:
    print("FATAL: 4.6 shift anchor not found")
    sys.exit(1)
src = src.replace(old_46, new_46, 1)

target.write_text(src, encoding="utf-8")
print("Tier 2 Patch applied: 5.4 point parse, 5.5 expanded overlay, 4.6 regex")
