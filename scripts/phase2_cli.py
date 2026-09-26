"""CLI collects working line-by-line."""
from pathlib import Path
import ast

P = Path("scripts/cli_tutor.py")
src = P.read_text(encoding="utf-8-sig")

if "def collect_working" in src:
    print("Already patched")
    raise SystemExit(0)

# Insert collect_working helper before main()
HELPER = '''

def collect_working():
    """Collect working line-by-line. Returns WorkingSubmission or None to quit."""
    from src.tutor.schemas import WorkingSubmission, WorkingStep
    import time as _time

    print()
    print("Show your working. One line at a time.")
    print("  - Type 'done' when finished")
    print("  - Type 'answer: x = ...' for a single-answer attempt")
    print("  - Type 'q' to quit")
    print()

    steps = []
    start = _time.time()
    while True:
        idx = len(steps) + 1
        try:
            raw = input(f"  Line {idx}: ").rstrip()
        except (EOFError, KeyboardInterrupt):
            return None
        stripped = raw.strip()
        if not stripped:
            continue
        low = stripped.lower()

        if low in ("q", "quit", "exit"):
            return None

        if low == "done" or low == "submit":
            if not steps:
                print("  (no working yet — type at least one line, or 'q' to quit)")
                continue
            return WorkingSubmission(
                steps=[WorkingStep(index=i + 1, raw_text=t) for i, t in enumerate(steps)],
                source="typed",
                final_answer=steps[-1],
            )

        if low.startswith("answer:"):
            answer = stripped[len("answer:"):].strip()
            if answer:
                return WorkingSubmission(
                    steps=[WorkingStep(index=1, raw_text=answer, timestamp=_time.time() - start)],
                    source="typed",
                    final_answer=answer,
                )
            print("  (empty answer — try again)")
            continue

        # Any other line is a working step
        steps.append(stripped)
        if len(steps) >= 40:
            print("  (40 lines — submit with 'done')")


'''

# Insert helper before "def main()"
anchor = "def main() -> None:"
if anchor in src:
    src = src.replace(anchor, HELPER + "\n" + anchor, 1)
    print("Inserted collect_working()")
else:
    print("WARN: main() anchor not found")

# Replace the input loop
old_loop = '''    while True:
        raw = input("\\nYour answer: ").strip()
        if not raw:
            print("Type an attempt, or 'quit'.")
            continue
        low = raw.lower()
        if low in ("q", "quit", "exit"):
            break
        if low in ("diagram", "d"):
            _p = _open_diagram(problem)
            if _p is not None:
                print("(reopened: " + str(_p) + ")")
            else:
                print("(no diagram page for this question)")
            continue

        explicit = low in (
            "answer",
            "just give me the answer",
            "give me the answer",
            "solution",
            "solve it",
        )

        action = engine.step(
            state,
            problem,
            raw,
            explicit_solution_request=explicit,
        )'''

new_loop = '''    while True:
        submission = collect_working()
        if submission is None:
            break

        # Detect answer-demand shortcut (e.g. "answer:" was already stripped
        # inside collect_working, so we don't need to detect it here)

        action = engine.step(
            state,
            problem,
            submission,
            explicit_solution_request=False,
        )'''

if old_loop in src:
    src = src.replace(old_loop, new_loop, 1)
    print("Replaced input loop")
else:
    print("WARN: old loop not found — trying a looser match")
    # Looser: find "raw = input" and check surrounding
    idx = src.find("raw = input(")
    if idx > 0:
        print("  Found 'raw = input' at char", idx)
        # Show a snippet for the user to inspect
        print(src[max(0, idx - 200):idx + 200])

try:
    ast.parse(src)
    P.write_text(src, encoding="utf-8")
    print("CLI patched")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)