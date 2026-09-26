from pathlib import Path
import ast

P = Path("src/tutor/analogue_generators.py")
src = P.read_text(encoding="utf-8-sig")

old = '''    # Merge written analogues
    for tid, entries in WRITTEN_ANALOGUES.items():
        pool[tid] = entries
        if verbose:
            print(f"  {tid}: {len(entries)} written")
    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            pool[tid] = entries
            if verbose:
                print(f"  {tid}: {len(entries)} written (extra)")
    except NameError:
        pass'''

new = '''    # Merge written analogues (add to generated, do not overwrite)
    for tid, entries in WRITTEN_ANALOGUES.items():
        if tid in pool and pool[tid]:
            existing = {a.get("problem", "") for a in pool[tid]}
            extra = [e for e in entries if e.get("problem", "") not in existing]
            pool[tid] = list(pool[tid]) + extra
        else:
            pool[tid] = list(entries)
        if verbose:
            print(f"  {tid}: {len(pool[tid])} total ({len(entries)} written merged)")
    try:
        for tid, entries in EXTRA_WRITTEN_ANALOGUES.items():
            if tid in pool and pool[tid]:
                existing = {a.get("problem", "") for a in pool[tid]}
                extra = [e for e in entries if e.get("problem", "") not in existing]
                pool[tid] = list(pool[tid]) + extra
            else:
                pool[tid] = list(entries)
            if verbose:
                print(f"  {tid}: {len(pool[tid])} total ({len(entries)} extra merged)")
    except NameError:
        pass'''

if old in src:
    src = src.replace(old, new, 1)
    print("Fixed merge logic")
else:
    print("WARN: anchor not found")

ast.parse(src)
P.write_text(src, encoding="utf-8")
print("Syntax OK")