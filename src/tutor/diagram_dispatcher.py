# src/tutor/diagram_dispatcher.py
# Maps template `diagram` names to renderer functions in
# question_diagrams.py (P1) and question_diagrams_p2.py (P2).

from pathlib import Path
import importlib.util
import sys

ROOT = None
for _cand in [Path.cwd()] + list(Path.cwd().parents):
    if (_cand / "src" / "tutor").exists():
        ROOT = _cand
        break
if ROOT is None:
    ROOT = Path(r"C:\Users\Administrator\Desktop\Matric-Maths-Exam-Intelligence")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_p1_path = ROOT / "src" / "tutor" / "question_diagrams.py"
_p2_path = ROOT / "src" / "tutor" / "question_diagrams_p2.py"
_diagrams_p1 = _load("question_diagrams", _p1_path) if _p1_path.exists() else None
_diagrams_p2 = _load("question_diagrams_p2", _p2_path) if _p2_path.exists() else None


RENDERER_ALIASES = {
    # P2 stats
    "scatter_regression":       ("p2", "render_scatter_regression"),
    "ogive":                    ("p2", "render_ogive"),
    "histogram":                ("p2", "render_histogram"),
    "bar_chart":                ("p2", "render_bar_chart"),
    # P2 analytical
    "analytical_triangle":      ("p2", "render_analytical_triangle"),
    "analytical_circle":        ("p2", "render_analytical_circle"),
    "point_on_axes":            ("p2", "render_point_on_axes"),
    # P2 trig
    "trig_graph":               ("p2", "render_trig_graph"),
    "three_d_trig":             ("p2", "render_three_d_trig"),
    # P2 Euclidean
    "circle_centre_angle":      ("p2", "render_circle_centre_angle"),
    "circle_tangent":           ("p2", "render_circle_tangent"),
    "circle_cyclic_quad":       ("p2", "render_circle_cyclic_quad"),
    "circle_similarity":        ("p2", "render_circle_similarity"),
    "triangle_proportion":      ("p2", "render_triangle_proportion"),
    # P1 renderers
    "parabola_line":            ("p1", "render_parabola_line"),
    "parabola_hyperbola":       ("p1", "render_parabola_hyperbola"),
    "hyperbola_solo":           ("p1", "render_hyperbola_solo"),
    "hyperbola_line":           ("p1", "render_hyperbola_line"),
    "cubic":                    ("p1", "render_cubic"),
    "exponential_solo":         ("p1", "render_exponential_solo"),
    "exponential_two_points":   ("p1", "render_exponential_two_points"),
    "log_solo":                 ("p1", "render_log_solo"),
    "cylinder":                 ("p1", "render_cylinder"),
    "venn":                     ("p1", "render_venn"),
    "poster":                   ("p1", "render_poster"),
}


def render_diagram(name, **kwargs):
    if name not in RENDERER_ALIASES:
        raise KeyError(f"No renderer mapped for diagram: {name!r}")
    which, fn_name = RENDERER_ALIASES[name]
    mod = _diagrams_p1 if which == "p1" else _diagrams_p2
    if mod is None:
        raise RuntimeError(f"Diagram module for {which!r} not loaded.")
    fn = getattr(mod, fn_name, None)
    if fn is None:
        raise AttributeError(
            f"Alias {name!r} -> {fn_name!r} is not defined in the "
            f"{which} module.")
    return fn(**kwargs)


def available_renderers():
    return sorted(RENDERER_ALIASES.keys())
