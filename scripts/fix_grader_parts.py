"""Fix _parts prefix + normalise * insertion."""
from pathlib import Path
import ast

P = Path("src/tutor/math_grader.py")
src = P.read_text(encoding="utf-8-sig")

# ---- FIX 1: add * insertion in _normalise ----
old_norm = '''    # Comma decimal inside a number → dot (SA convention)
    s = re.sub(r"(\\d),(\\d)", r"\\1.\\2", s)
    # Collapse whitespace
    s = re.sub(r"\\s+", " ", s).strip()
    # Lowercase for comparison stability
    return s.lower()'''

new_norm = '''    # Comma decimal inside a number → dot (SA convention)
    s = re.sub(r"(\\d),(\\d)", r"\\1.\\2", s)
    # Insert * for implicit multiplication (2x → 2*x, 5n → 5*n)
    # Only for a single letter not followed by another letter
    s = re.sub(r"(\\d)([a-z])(?![a-z])", r"\\1*\\2", s, flags=re.IGNORECASE)
    # 2(x+1) → 2*(x+1)
    s = re.sub(r"(\\d)\\(", r"\\1*(", s)
    # Collapse whitespace
    s = re.sub(r"\\s+", " ", s).strip()
    # Lowercase for comparison stability
    return s.lower()'''

if old_norm in src:
    src = src.replace(old_norm, new_norm, 1)
    print("FIX 1: added * insertion in _normalise")
else:
    print("FIX 1 WARN: _normalise anchor not found")

# ---- FIX 2: strip prefix per part in _parts ----
old_parts = '''    clean = []
    for p in parts:
        p = re.sub(r"\\(.*?\\)", "", p).strip()
        p = re.sub(r"\\b(from|see|moved|step|above|below|note)\\b.*$", "", p).strip()
        if not p:
            continue
        if len(p) > 60:
            continue
        clean.append(p)
    return clean'''

new_parts = '''    clean = []
    for p in parts:
        # Strip any residual 'x = ' style prefix
        p = _strip_prefix(p)
        # Strip trailing parentheses and working fragments
        p = re.sub(r"\\(.*?\\)", "", p).strip()
        p = re.sub(r"\\b(from|see|moved|step|above|below|note)\\b.*$", "", p).strip()
        if not p:
            continue
        if len(p) > 60:
            continue
        clean.append(p)
    return clean'''

if old_parts in src:
    src = src.replace(old_parts, new_parts, 1)
    print("FIX 2: strip prefix per part")
else:
    print("FIX 2 WARN: _parts clean loop not found")

# ---- FIX 3: numeric_multi_root pairwise fallback ----
old_mnr = '''    if a_syms and b_syms and a_syms == b_syms:
        return True, 0.95, "multi-root set equal"
    return False, 0.0, ""'''

new_mnr = '''    if a_syms and b_syms and a_syms == b_syms:
        return True, 0.95, "multi-root set equal"

    # Pairwise fallback: same count, values equal after simplify
    if a_syms and b_syms and len(a_syms) == len(b_syms):
        remaining = set(b_syms)
        for av in a_syms:
            matched = False
            for bv in list(remaining):
                try:
                    if sp.simplify(av - bv) == 0:
                        remaining.discard(bv)
                        matched = True
                        break
                except Exception:
                    continue
            if not matched:
                return False, 0.0, ""
        if not remaining:
            return True, 0.95, "multi-root set equal (pairwise)"

    return False, 0.0, ""'''

if old_mnr in src:
    src = src.replace(old_mnr, new_mnr, 1)
    print("FIX 3: numeric_multi_root pairwise fallback")
else:
    print("FIX 3 WARN: numeric_multi_root anchor not found")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)