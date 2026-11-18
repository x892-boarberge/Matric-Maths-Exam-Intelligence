"""S2 fix: add single-value branch to main loop sign-flip (mirror of variant loop)."""
import sys, datetime
from pathlib import Path

target = Path("scripts/cli_tutor.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# main-loop single-value sign-flip" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

old = '''            if misconception and ("SIGN_ERROR" in misconception or "SIGN_FLIP" in misconception or getattr(g, "matcher", "") == "single_value_mismatch"):
                import re as _re
                l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", learner_text) if n not in ('', '-', '+')]
                e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", problem.expected_answer) if n not in ('', '-', '+')]

                if len(l_nums) >= 2 and len(e_nums) >= 2 and sorted([abs(x) for x in l_nums]) == sorted([abs(x) for x in e_nums]):'''

new = '''            if misconception and ("SIGN_ERROR" in misconception or "SIGN_FLIP" in misconception or getattr(g, "matcher", "") == "single_value_mismatch"):
                import re as _re
                # main-loop single-value sign-flip
                if getattr(g, "matcher", "") == "single_value_mismatch":
                    _last_l = learner_text.strip().split("\\n")[-1] if learner_text else ""
                    _last_e = problem.expected_answer.strip().split("\\n")[-1] if problem.expected_answer else ""
                    l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _last_l) if n not in ('', '-', '+')]
                    e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", _last_e) if n not in ('', '-', '+')]
                    if l_nums and e_nums and abs(l_nums[-1]) == abs(e_nums[-1]) and l_nums[-1] != e_nums[-1]:
                        w, r = l_nums[-1], e_nums[-1]
                        w_str = f"+{int(w)}" if w > 0 else str(int(w))
                        r_str = f"+{int(r)}" if r > 0 else str(int(r))
                        print(f"  Tanaka: You wrote {w_str}, but the answer is {r_str}. The number is right, but the sign is flipped.")
                    else:
                        print("  Tanaka: Your numbers are completely wrong. Check your working.")
                else:
                    l_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", learner_text) if n not in ('', '-', '+')]
                    e_nums = [float(n) for n in _re.findall(r"[-+]?\\d*\\.?\\d+", problem.expected_answer) if n not in ('', '-', '+')]
                    if len(l_nums) >= 2 and len(e_nums) >= 2 and sorted([abs(x) for x in l_nums]) == sorted([abs(x) for x in e_nums]):'''

if old not in src:
    print("FATAL: main loop sign-flip anchor not found")
    sys.exit(1)
src = src.replace(old, new, 1)

# Remove the OLD inner block (which is now redundant after the single-value branch)
old_block = '''                    if len(l_nums) >= 2 and len(e_nums) >= 2 and sorted([abs(x) for x in l_nums]) == sorted([abs(x) for x in e_nums]):
                        _is_sign_flip = True
                        wrong = next((l for l in l_nums if l not in e_nums), l_nums[0])
                        right = next((e for e in e_nums if e not in l_nums), e_nums[0])
                        w_str = f"+{int(wrong)}" if wrong > 0 else str(int(wrong))
                        r_str = f"+{int(right)}" if right > 0 else str(int(right))
                        print(f"  Tanaka: You wrote {w_str}, but the root is {r_str}. The number is right, but the sign is flipped.")
                    else:
                        # The numbers are completely different. Do not say "the number is right".
                        print("  Tanaka: Your numbers are completely wrong. Check your working.")'''

new_block = '''                        # Multi-value sign-flip (existing branch)
                        wrong = next((l for l in l_nums if l not in e_nums), l_nums[0])
                        right = next((e for e in e_nums if e not in l_nums), e_nums[0])
                        w_str = f"+{int(wrong)}" if wrong > 0 else str(int(wrong))
                        r_str = f"+{int(right)}" if right > 0 else str(int(right))
                        print(f"  Tanaka: You wrote {w_str}, but the root is {r_str}. The number is right, but the sign is flipped.")
                    else:
                        # The numbers are completely different. Do not say "the number is right".
                        print("  Tanaka: Your numbers are completely wrong. Check your working.")'''

if old_block not in src:
    print("FATAL: redundant multi-value block anchor not found")
    sys.exit(1)
src = src.replace(old_block, new_block, 1)

target.write_text(src, encoding="utf-8")
print("S2 fix applied: main loop now handles single-value sign-flip")
