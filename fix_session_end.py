from pathlib import Path
p = Path("scripts/cli_tutor.py")
c = p.read_text(encoding="utf-8")
orig_len = len(c)

# FIX 1: correct calc counts "match" too
old1 = 'correct = sum(1 for e in seen_attempts if e == "none")'
new1 = 'correct = sum(1 for e in seen_attempts if str(e or "").lower() in ("none", "match"))'
if old1 in c:
    c = c.replace(old1, new1); print("FIX 1: calc updated")
elif new1 in c:
    print("FIX 1: already done")
else:
    print("FIX 1: LINE NOT FOUND")

# FIX 2: replace [] with inline query
old2 = 'show_session_summary(store, learner_id, session_id, _skill, [])'
new2 = 'show_session_summary(store, learner_id, session_id, _skill, [(r["error_type"] or "") for r in store.conn.execute("SELECT error_type FROM attempt WHERE session_id=? AND learner_id=? AND skill_id=? ORDER BY timestamp", (session_id, learner_id, _skill)).fetchall()])'
if old2 in c:
    c = c.replace(old2, new2); print("FIX 2: summary call updated")
elif new2 in c:
    print("FIX 2: already done")
else:
    print("FIX 2: LINE NOT FOUND")

# FIX 3: if try-block was mangled, remove the stray print-inside-try
bad = '        show_learner_dashboard(store, learner_id)\n        print(f"  [dashboard unavailable: {_e}]")\n    except Exception as _e:\n        print(f"  [dashboard unavailable: {_e}]")'
good = '        show_learner_dashboard(store, learner_id)\n    except Exception as _e:\n        print(f"  [dashboard unavailable: {_e}]")'
if bad in c:
    c = c.replace(bad, good); print("FIX 3: stray print removed")
else:
    print("FIX 3: no stray print found (fine if not mangled)")

p.write_text(c, encoding="utf-8")
print(f"Done. {orig_len} -> {len(c)} bytes")
