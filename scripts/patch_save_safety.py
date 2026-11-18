"""Fix _save OSError on Windows: force str path and handle locked files."""
import sys, datetime
from pathlib import Path

target = Path("scripts/render_diagrams.py")
backup = target.with_suffix(f".py.bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
backup.write_bytes(target.read_bytes())
print(f"Backup: {backup}")

src = target.read_text(encoding="utf-8")

if "# _save safety fix" in src:
    print("FATAL: patch already applied")
    sys.exit(1)

old_save = '''def _save(fig, out_path):
    fig.tight_layout()
    fig.savefig(out_path, dpi=DBE_STYLE["dpi"], bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return True'''

new_save = '''def _save(fig, out_path):
    # _save safety fix: force str for Windows + retry if file is locked
    import time
    fig.tight_layout()
    path_str = str(out_path)
    for attempt in range(3):
        try:
            fig.savefig(path_str, dpi=DBE_STYLE["dpi"], bbox_inches="tight", facecolor="white")
            plt.close(fig)
            return True
        except OSError as e:
            if attempt == 2:
                print(f"    WARN: could not save {path_str} (is it open in a viewer?)")
                plt.close(fig)
                return False
            time.sleep(0.1)
    return False'''

if old_save not in src:
    print("FATAL: _save anchor not found")
    sys.exit(1)
src = src.replace(old_save, new_save, 1)

target.write_text(src, encoding="utf-8")
print("Path string + retry patch applied to _save")
