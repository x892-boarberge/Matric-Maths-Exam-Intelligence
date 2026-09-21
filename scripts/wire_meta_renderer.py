"""Replace meta_library call with meta_renderer in tutor_engine.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "tutor" / "tutor_engine.py"
src = ENGINE.read_text(encoding="utf-8")

if "meta_renderer" not in src:
    src = src.replace(
        "from . import meta_library\n",
        "from . import meta_library\nfrom . import meta_renderer\n",
        1,
    )
    print("Added meta_renderer import")
else:
    print("meta_renderer already imported")

old = '''            meta_message = meta_library.respond_to_disengagement(
                diseng.kind.value,
                learner_id=learner_state.learner_id,
                attempts=prior_same,
            )'''

new = '''            meta_message = meta_renderer.render_meta_response(
                diseng.kind.value,
                learner_text=learner_response,
                learner_id=learner_state.learner_id,
                attempts=prior_same,
            )'''

if old in src:
    src = src.replace(old, new, 1)
    ENGINE.write_text(src, encoding="utf-8")
    print("Engine now calls meta_renderer")
else:
    print("WARNING - old meta_library call not found")
