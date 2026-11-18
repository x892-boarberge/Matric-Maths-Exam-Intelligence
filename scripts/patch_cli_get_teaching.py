"""Wire get_teaching() into both voice-map call sites in cli_tutor.py."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
if not target.exists():
    print("FATAL: scripts/cli_tutor.py not found. Run from repo root.")
    sys.exit(1)

backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "get_teaching(misconception)" in src and "get_teaching(_mid)" in src:
    print("FATAL: patch already appears applied.")
    sys.exit(1)

# =========================================================================
# PATCH 1 — Main loop: insert teaching check as topmost branch
# =========================================================================

p1_old = '''                obj = _to.find_for(misconception)
                if obj and obj.get("learner_message"):'''

p1_new = '''                obj = _to.find_for(misconception)
                _lesson = None
                try:
                    from src.tutor.diagnosis import get_teaching
                    _lesson = get_teaching(misconception)
                except Exception:
                    pass
                if _lesson:
                    for _ln in _lesson.split("\\n"):
                        print("  Tanaka: " + _ln if _ln.strip() else "")
                elif obj and obj.get("learner_message"):'''

if p1_old not in src:
    print("FATAL: Patch 1 anchor not found. The main loop block may differ.")
    sys.exit(1)
if src.count(p1_old) != 1:
    print(f"FATAL: Patch 1 anchor found {src.count(p1_old)} times — ambiguous.")
    sys.exit(1)
src = src.replace(p1_old, p1_new, 1)
print("Patch 1 applied: main loop teaching check inserted.")

# =========================================================================
# PATCH 2 — Variant loop: insert teaching check before _var_voice chain
# =========================================================================

p2_old = '''                            _var_voice = None
                            if _mid:
                                if _mid == "M_CALCULATION_ERROR" or _mid == "M_SURD_CALCULATION_ERROR":'''

p2_new = '''                            _var_voice = None
                            _var_is_lesson = False
                            try:
                                from src.tutor.diagnosis import get_teaching
                                _lesson = get_teaching(_mid) if _mid else None
                                if _lesson:
                                    _var_voice = _lesson
                                    _var_is_lesson = True
                            except Exception:
                                pass
                            if _var_voice is None and _mid:
                                if _mid == "M_CALCULATION_ERROR" or _mid == "M_SURD_CALCULATION_ERROR":'''

if p2_old not in src:
    print("FATAL: Patch 2 anchor not found. The variant loop block may differ.")
    sys.exit(1)
if src.count(p2_old) != 1:
    print(f"FATAL: Patch 2 anchor found {src.count(p2_old)} times — ambiguous.")
    sys.exit(1)
src = src.replace(p2_old, p2_new, 1)
print("Patch 2 applied: variant loop teaching check inserted.")

# =========================================================================
# PATCH 3 — Variant loop: change final print to handle multi-line lesson
# =========================================================================

p3_old = '''                            if not _var_voice:
                                _var_voice = _var.get("fatal_error", "There is an error here.")
                            print("  Tanaka: " + _var_voice)'''

p3_new = '''                            if not _var_voice:
                                _var_voice = _var.get("fatal_error", "There is an error here.")
                            if _var_is_lesson:
                                for _ln in _var_voice.split("\\n"):
                                    print("  Tanaka: " + _ln if _ln.strip() else "")
                            else:
                                print("  Tanaka: " + _var_voice)'''

if p3_old not in src:
    print("FATAL: Patch 3 anchor not found. The final print block may differ.")
    sys.exit(1)
if src.count(p3_old) != 1:
    print(f"FATAL: Patch 3 anchor found {src.count(p3_old)} times — ambiguous.")
    sys.exit(1)
src = src.replace(p3_old, p3_new, 1)
print("Patch 3 applied: variant loop final print handles multi-line.")

target.write_text(src, encoding="utf-8")
print(f"\nAll three patches applied. File: {target}")
print("Run: py -m py_compile scripts/cli_tutor.py")
