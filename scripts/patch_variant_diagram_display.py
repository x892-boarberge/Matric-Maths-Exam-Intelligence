"""Wire variant diagram display into CLI (DP-15a follow-up)."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# variant diagram display" in src:
    print("FATAL: patch appears already applied")
    sys.exit(1)

# Anchor: the two prints after the VARIANT PRACTICE header
old = '''                    print("  " + _var["variant_question"])
                    print()'''

new = '''                    print("  " + _var["variant_question"])
                    # variant diagram display (DP-15a, 2026-11-17)
                    _v_dpath = _var.get("diagram_path")
                    if _v_dpath:
                        from pathlib import Path as _VPath
                        _v_ppath = _VPath(_v_dpath)
                        if _v_ppath.exists():
                            print("  Variant image: " + str(_v_dpath))
                            _v_opened = False
                            try:
                                _os.startfile(str(_v_ppath.resolve()))
                                _v_opened = True
                            except Exception:
                                try:
                                    import subprocess as _vsub
                                    _vsub.run(["explorer.exe", str(_v_ppath.resolve())], check=False, timeout=3)
                                    _v_opened = True
                                except Exception:
                                    _v_opened = False
                            if _v_opened:
                                print("  (attempted to open)")
                            else:
                                print("  (open the path above)")
                            _v_reason = _var.get("diagram_partial_reason")
                            if _var.get("diagram_status") == "partial" or _v_reason:
                                print("  [!] Diagram is partial - " + (_v_reason or "content incomplete"))
                    print()'''

if old not in src:
    print("FATAL: anchor not found. The variant_question print block may have moved.")
    sys.exit(1)
if src.count(old) != 1:
    print(f"FATAL: anchor count = {src.count(old)} (expected 1)")
    sys.exit(1)

src = src.replace(old, new, 1)
target.write_text(src, encoding="utf-8")
print("Patch applied: variant diagram display inserted")
