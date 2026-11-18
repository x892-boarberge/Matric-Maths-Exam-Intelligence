"""Extend dynamic sign-flip check to catch single-value mismatches (log, trig, etc.)."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if 'single_value_mismatch" in _var' in src or '"single_value_mismatch" == _gv' in src:
    print("FATAL: patch already applied")
    sys.exit(1)

old = '''                        # DYNAMIC SIGN FLIP CHECK (Only if absolute values match!)
                        _is_sign_flip = False
                        if _mid and ("SIGN_ERROR" in _mid or "SIGN_FLIP" in _mid):
                            import re as _re
                            l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _var_text) if n not in ('', '-', '+')]
                            e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _var["expected"]) if n not in ('', '-', '+')]

                            if len(l_nums) >= 2 and len(e_nums) >= 2 and sorted([abs(x) for x in l_nums]) == sorted([abs(x) for x in e_nums]):
                                _is_sign_flip = True
                                wrong = next((l for l in l_nums if l not in e_nums), l_nums[0])
                                right = next((e for e in e_nums if e not in l_nums), e_nums[0])
                                w_str = f"+{int(wrong)}" if wrong > 0 else str(int(wrong))
                                r_str = f"+{int(right)}" if right > 0 else str(int(right))
                                print(f"  Tanaka: You wrote {w_str}, but the root is {r_str}. The number is right, but the sign is flipped.")
                            else:
                                # The numbers are completely different. Do not say "the number is right".
                                print("  Tanaka: Your numbers are completely wrong. Check your working.")'''

new = '''                        # DYNAMIC SIGN FLIP CHECK (Only if absolute values match!)
                        _is_sign_flip = False
                        if _mid and ("SIGN_ERROR" in _mid or "SIGN_FLIP" in _mid or _gv.matcher == "single_value_mismatch"):
                            import re as _re

                            # Single-value case (log, trig, single-answer): compare last number
                            if _gv.matcher == "single_value_mismatch":
                                _last = _var_text.strip().split("\\n")[-1] if _var_text else ""
                                l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _last) if n not in ('', '-', '+')]
                                e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _var["expected"]) if n not in ('', '-', '+')]
                                if l_nums and e_nums and abs(l_nums[-1]) == abs(e_nums[-1]) and l_nums[-1] != e_nums[-1]:
                                    _is_sign_flip = True
                                    w = l_nums[-1]
                                    r = e_nums[-1]
                                    w_str = f"+{int(w)}" if w > 0 else str(int(w))
                                    r_str = f"+{int(r)}" if r > 0 else str(int(r))
                                    print(f"  Tanaka: You wrote {w_str}, but the answer is {r_str}. The number is right, but the sign is flipped.")
                                else:
                                    print("  Tanaka: Your numbers are completely wrong. Check your working.")
                            else:
                                # Multi-value case (roots, pairs): existing logic
                                l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _var_text) if n not in ('', '-', '+')]
                                e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _var["expected"]) if n not in ('', '-', '+')]
                                if len(l_nums) >= 2 and len(e_nums) >= 2 and sorted([abs(x) for x in l_nums]) == sorted([abs(x) for x in e_nums]):
                                    _is_sign_flip = True
                                    wrong = next((l for l in l_nums if l not in e_nums), l_nums[0])
                                    right = next((e for e in e_nums if e not in l_nums), e_nums[0])
                                    w_str = f"+{int(wrong)}" if wrong > 0 else str(int(wrong))
                                    r_str = f"+{int(right)}" if right > 0 else str(int(right))
                                    print(f"  Tanaka: You wrote {w_str}, but the root is {r_str}. The number is right, but the sign is flipped.")
                                else:
                                    print("  Tanaka: Your numbers are completely wrong. Check your working.")'''

if old not in src:
    print("FATAL: anchor not found. The block may have been reformatted.")
    sys.exit(1)
if src.count(old) != 1:
    print(f"FATAL: anchor count = {src.count(old)} (expected 1)")
    sys.exit(1)
src = src.replace(old, new, 1)

target.write_text(src, encoding="utf-8")
print("Sign-flip patch applied: single-value branch added")
