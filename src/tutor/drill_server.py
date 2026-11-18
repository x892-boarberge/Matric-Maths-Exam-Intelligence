"""
drill_server.py — HTTP shell over drill.grade_submission.
Also serves the keyboard HTML + libs so everything is same-origin.
"""
from __future__ import annotations

import json
import sys
import threading
import traceback
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "src"
DOCS = ROOT / "docs"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tutor import drill
from tutor.learner_store import open_store
from tutor.schemas import Problem

STORE = open_store(ROOT / "data" / "learner_store" / "learners.db")
ENGINE = None
LEARNER_ID = "tanaka"

ANCHORS = [
    Problem(
        problem_id="2023_P1_Q1.1.1",
        skill_id="algebra.quadratic.solve",
        topic="Algebra",
        subtopic="Quadratic equations",
        structure_type="routine_calculation",
        prompt="Solve for x:  x^2 + x - 12 = 0",
        expected_answer="x = -4 or x = 3",
    ),
]

SESSION = {
    "id": str(uuid.uuid4()),
    "anchor": ANCHORS[0],
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        import sys as _sys, time as _time
        print(f"[{_time.strftime('%H:%M:%S')}] " + (a[0] % a[1:] if a else ""),
              file=_sys.stderr, flush=True)

    # ---------- json response ----------
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------- static file ----------
    def _serve_file(self, rel_path):
        target = (DOCS / rel_path).resolve()
        try:
            target.relative_to(DOCS.resolve())
        except ValueError:
            return self._send(403, {"error": "forbidden"})
        if not target.exists() or not target.is_file():
            return self._send(404, {"error": "not found"})
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css":  "text/css; charset=utf-8",
            ".js":   "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png":  "image/png",
            ".svg":  "image/svg+xml",
            ".ico":  "image/x-icon",
        }.get(target.suffix.lower(), "application/octet-stream")
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path in ("/", "/index.html", "/keyboard_preview.html"):
            return self._serve_file("keyboard_preview.html")

        if path.startswith("/libs/"):
            return self._serve_file(path[1:])

        if path.startswith("/next_question"):
            a = SESSION["anchor"]
            return self._send(200, {
                "problem_id":      a.problem_id,
                "skill_id":        a.skill_id,
                "prompt":          a.prompt,
                "expected_answer": a.expected_answer,
                "session_id":      SESSION["id"],
            })

        if path.startswith("/health"):
            return self._send(200, {"ok": True,
                                    "anchor": SESSION["anchor"].problem_id})

        return self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"error": "bad json"})

        if self.path.startswith("/reset_session"):
            SESSION["id"] = str(uuid.uuid4())
            return self._send(200, {"session_id": SESSION["id"]})

        if self.path.startswith("/grade"):
            lines = body.get("learner_lines_latex") or []
            import sys as _sys
            print(f"[grade] received {len(lines)} line(s) from {self.client_address}", file=_sys.stderr, flush=True)
            if not isinstance(lines, list):
                return self._send(400, {"error": "learner_lines_latex must be a list"})
            sbc = body.get("sbc_message") or ""
            try:
                result = drill.grade_submission(
                    store=STORE,
                    learner_id=LEARNER_ID,
                    session_id=SESSION["id"],
                    anchor=SESSION["anchor"],
                    learner_lines=lines,
                    sbc_message=sbc,
                )
                return self._send(200, result)
            except Exception as e:
                import traceback as _tb
                tb_str = _tb.format_exc()
                print(tb_str)  # to notebook output
                return self._send(500, {"error": str(e), "traceback": tb_str})

        return self._send(404, {"error": "not found"})


def serve_forever(host="127.0.0.1", port=8765):
    print(f"drill_server at http://{host}:{port}")
    print(f"  keyboard: http://{host}:{port}/")
    print(f"  anchor:   {SESSION['anchor'].problem_id}  |  learner: {LEARNER_ID}")
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.serve_forever()


def serve_in_thread(host="127.0.0.1", port=8765):
    t = threading.Thread(target=serve_forever, args=(host, port), daemon=True)
    t.start()
    print(f"drill_server running in background thread on http://{host}:{port}")
    return t


if __name__ == "__main__":
    serve_forever()
