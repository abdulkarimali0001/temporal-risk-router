"""Demo web app: type a question, watch the router decide.

    python -m src.app            then open http://localhost:8765
(or double-click run_app.command)

Runs only on this computer (localhost). Uses the same pipeline as the experiments:
Check 1 (time check) -> Check 2 (knowledge check) -> decision -> answer with sources.
"""
from __future__ import annotations

import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src import llm, pipeline, router, search, time_check
from src.llm import ROOT

PORT = 8765
PAGE = ROOT / "app" / "index.html"
MODEL = None
LOCK = threading.Lock()          # one question at a time: the local model is busy anyway


def answer(question: str) -> dict:
    global MODEL
    MODEL = MODEL or time_check.load()
    t0 = time.time()
    with LOCK:
        r = pipeline.ask(question, model=MODEL)
    return {
        "question": question,
        "group": router.GROUP_NAMES[r["group"]],
        "knows": r["knows"], "agreement": r["agreement"], "samples": r.get("answers", []),
        "action": r["action"], "action_text": router.ACTIONS[r["action"]], "reason": r["reason"],
        "answer": r["answer"], "query": r.get("query", ""),
        "sources": [{"title": p["title"], "url": p["url"], "retrieved": p.get("retrieved", "")}
                    for p in r.get("sources", [])],
        "not_found": r["answer"] == pipeline.NOT_FOUND,
        "model": llm.model_name(), "web": search.web_enabled(), "seconds": round(time.time() - t0, 1),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, kind: str):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/info":
            self._send(200, json.dumps({"model": llm.model_name(), "web": search.web_enabled()}).encode(),
                       "application/json")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/ask":
            return self._send(404, b"not found", "text/plain")
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            q = (data.get("question") or "").strip()[:500]
            if not q:
                return self._send(400, json.dumps({"error": "Type a question first."}).encode(),
                                  "application/json")
            body = json.dumps(answer(q), ensure_ascii=False).encode()
            self._send(200, body, "application/json; charset=utf-8")
        except Exception as e:
            msg = f"Something went wrong: {e}. Is Ollama running?"
            self._send(500, json.dumps({"error": msg}).encode(), "application/json")

    def log_message(self, *args):
        pass


def main():
    llm.load_env()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Temporal-Risk Router demo running at {url}  (close this window to stop)")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
