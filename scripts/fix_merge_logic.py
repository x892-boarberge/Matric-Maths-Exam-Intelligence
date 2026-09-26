"""Fix generate_all to merge written + generated instead of overwriting."""
from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

old = '''    # Merge written analogues
    for tid, entries in WRITTEN_ANALOGUES.items():
        pool[tid] = entries
        if verbose:
            print(f"  {tid}: {len(entries)} written")'''

new = '''    # Merge written analogues — MERGE, don't overwrite
    for tid, entries in WRITTEN_ANALOGUES.items():
        if tid in pool and pool[tid]:
            # Combine: generated variants first, then any written ones not already covered
            existing_problems = {a.get("problem", "") for a in pool[tid]}
            extra = [e for e in entries if e.get("problem", "") not in existing_problems]
            pool[tid] = list(pool[tid]) + extra
        else:
            pool[tid] = list(entries)
        if verbose:
            print(f"  {tid}: {len(pool[tid])} (incl. {len(entries)} written)")'''

if old in src:
    src = src.replace(old, new, 1)
    print("Fixed generate_all merge logic")
else:
    print("WARN: anchor not found — searching")
    idx = src.find("Merge written analogues")
    if idx > 0:
        print(src[max(0, idx-50):idx+400])

# Same for EXTRA_WRITTEN_ANALOGUES if it exists
old2 = '''    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            pool[tid] = entries
            if verbose:
                print(f"  {tid}: {len(entries)} written (extra)")
    except NameError:
        pass'''

new2 = '''    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            if tid in pool and pool[tid]:
                existing_problems = {a.get("problem", "") for a in pool[tid]}
                extra = [e for e in entries if e.get("problem", "") not in existing_problems]
                pool[tid] = list(pool[tid]) + extra
            else:
                pool[tid] = list(entries)
            if verbose:
                print(f"  {tid}: {len(pool[tid])} (incl. {len(entries)} extra written)")
    except NameError:
        pass'''

if old2 in src:
    src = src.replace(old2, new2, 1)
    print("Fixed EXTRA_WRITTEN merge logic")
else:
    print("EXTRA_WRITTEN merge: anchor not found or not present")

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)