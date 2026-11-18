import json, re, shutil
from pathlib import Path
from datetime import datetime

POOL_DIR = Path("data/processed/tutor/variant_pools")
ts = datetime.now().strftime("%Y%m%d%H%M%S")

def clean_string(s):
    if not isinstance(s, str):
        return s
    # Only fix leading coefficient 1: "1x²" -> "x²", "-1x²" -> "-x²", "1x^" -> "x^"
    s = re.sub(r"(?<![0-9])1x\^", "x^", s)
    s = re.sub(r"(?<![0-9])-1x\^", "-x^", s)
    # + -N -> - N
    s = re.sub(r"\+\s*-(\d)", r"- \1", s)
    # - -N -> + N
    s = re.sub(r"-\s*-(\d)", r"+ \1", s)
    return s

def clean_recursive(obj):
    if isinstance(obj, str):
        return clean_string(obj)
    if isinstance(obj, list):
        return [clean_recursive(x) for x in obj]
    if isinstance(obj, dict):
        return {k: clean_recursive(v) for k, v in obj.items()}
    return obj

for name in ["5.2", "5.4", "5.6", "6.1", "6.2", "6.3"]:
    p = POOL_DIR / f"{name}_pool.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    d_clean = clean_recursive(d)
    shutil.copy(p, p.with_suffix(f".json.bak_{ts}"))
    p.write_text(json.dumps(d_clean, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{name}: cleaned")
