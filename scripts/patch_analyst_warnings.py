"""patch_analyst_warnings.py — add spurious-correlation guard to correlate()."""
import subprocess
import sys
from pathlib import Path

P = Path("src") / "tutor" / "analyst.py"
src = P.read_text(encoding="utf-8")

if "warnings_list" in src and "structural_artifact" in src:
    print("Already patched. Nothing to do.")
    sys.exit(0)

old = '''        if dx == 0 or dy == 0:
            r = 0.0
            note = "zero variance in one metric — correlation undefined"
        else:
            r = num / (dx * dy)
            note = ""
            if abs(r) < 0.1:
                note = "negligible correlation"
            elif abs(r) < 0.3:
                note = "weak correlation"
            elif abs(r) < 0.7:
                note = "moderate correlation"
            else:
                note = "strong correlation"
            if r > 0:
                note += " (positive)"
            elif r < 0:
                note += " (negative)"

        return {
            "node_id": node_id,
            "metric_a": metric_a,
            "metric_b": metric_b,
            "n": n,
            "pearson_r": round(r, 4),
            "note": note,
            "caveat": (
                "Correlation is not causation. Any proposed causal claim "
                "requires a controlled test, not this number."
            ),
        }'''

new = '''        warnings_list = []
        if n < 10:
            warnings_list.append(f"small_sample: n={n} (recommend n>=10)")

        if dx == 0 or dy == 0:
            r = 0.0
            note = "zero variance in one metric — correlation undefined"
            warnings_list.append("zero_variance: one or both metrics constant")
        else:
            r = num / (dx * dy)
            note = ""
            if abs(r) < 0.1:
                note = "negligible correlation"
            elif abs(r) < 0.3:
                note = "weak correlation"
            elif abs(r) < 0.7:
                note = "moderate correlation"
            else:
                note = "strong correlation"
            if r > 0:
                note += " (positive)"
            elif r < 0:
                note += " (negative)"

        zeros_a = sum(1 for x in xs if x == 0)
        zeros_b = sum(1 for y in ys if y == 0)
        if zeros_a / n > 0.5:
            warnings_list.append(
                f"structural_artifact: {zeros_a}/{n} learners have {metric_a}=0"
            )
        if zeros_b / n > 0.5:
            warnings_list.append(
                f"structural_artifact: {zeros_b}/{n} learners have {metric_b}=0"
            )

        if warnings_list and abs(r) > 0.7 and dx > 0 and dy > 0:
            note = ("strong correlation (positive)" if r > 0
                    else "strong correlation (negative)")
            note += " BUT LIKELY SPURIOUS — see warnings"

        return {
            "node_id": node_id,
            "metric_a": metric_a,
            "metric_b": metric_b,
            "n": n,
            "pearson_r": round(r, 4),
            "note": note,
            "warnings": warnings_list,
            "caveat": (
                "Correlation is not causation. Any proposed causal claim "
                "requires a controlled test, not this number."
            ),
        }'''

if old not in src:
    print("FAIL: original correlate tail not found")
    sys.exit(1)

src = src.replace(old, new, 1)
P.write_text(src, encoding="utf-8")
print(f"Patched {P}")

r = subprocess.run([sys.executable, "-m", "py_compile", str(P)], capture_output=True)
if r.returncode == 0:
    print("py_compile: PASS")
    sys.exit(0)
print("py_compile: FAIL")
print(r.stderr.decode())
sys.exit(1)
