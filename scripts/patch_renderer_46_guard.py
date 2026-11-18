"""Fix 4.6 regression: log-only fallback refuses translation/inverse questions."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
if not target.exists():
    print("FATAL: scripts/render_diagrams.py not found")
    sys.exit(1)

backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "TRANSLATION_KEYWORDS" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

# Insert a semantic guard before the log-only fallback in _apply_pool
old_block = '''                else:
                    base = _parse_log_base_only(v["variant_question"])
                    if base is not None and render_log_only(base, out_path):
                        status = "rendered"
                        v["diagram_note"] = "log-only (no marked point in variant text)"'''

new_block = '''                else:
                    TRANSLATION_KEYWORDS = ("translated", "translation", "shifted",
                                            "moved", "inverse", "range", "domain")
                    text_lower = v["variant_question"].lower()
                    is_translation_q = any(kw in text_lower for kw in TRANSLATION_KEYWORDS)
                    base = _parse_log_base_only(v["variant_question"])
                    if base is not None and render_log_only(base, out_path):
                        if is_translation_q:
                            status = "partial"
                            partial_reason = "translation/inverse question — needs two-curve renderer"
                        else:
                            status = "rendered"
                            v["diagram_note"] = "log-only (no marked point in variant text)"'''

if old_block not in src:
    print("FATAL: anchor not found. The _apply_pool block may have been modified.")
    sys.exit(1)

src = src.replace(old_block, new_block, 1)
target.write_text(src, encoding="utf-8")
print("Patch applied: 4.6 translation guard inserted.")
print("Run: py -m py_compile scripts/render_diagrams.py")
print("Then: py scripts/render_diagrams.py")
