"""Fix: after learner says 'no, I didn't mean that', do NOT fire diagnosis."""
from pathlib import Path
import ast

P = Path("src/tutor/drill.py")
src = P.read_text(encoding="utf-8-sig")

old = '''                if confirm in ("", "y", "yes"):
                    correct_count += 1
                    print()
                    print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                    break
                if confirm in ("s", "skip"):
                    print()
                    print("  Let's move on.")
                    break
                # else fall through to "wrong" path
                print()
                print("  Let's try again.")'''

new = '''                if confirm in ("", "y", "yes"):
                    correct_count += 1
                    print()
                    print(f"  ✓ Correct.  ({correct_count} correct this drill)")
                    break
                if confirm in ("s", "skip"):
                    print()
                    print("  Let's move on.")
                    break
                # Learner says "that's not what I meant" — do NOT fire diagnosis.
                # Just loop back and let them retype.
                print()
                print("  No problem. Try the same question again.")
                continue'''

if old in src:
    src = src.replace(old, new, 1)
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("Fixed: 'no' at confirmation -> clean retry loop, no diagnosis")
    print("Syntax OK")
else:
    print("WARN: anchor not found")

# Also: after "Let's try again." from a real wrong answer, we should NOT show sibling if the learner already saw one this question
# Count siblings shown per question to avoid repeating