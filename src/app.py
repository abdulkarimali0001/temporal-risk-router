"""Demo web app: type a question, watch the router decide.

    python -m src.app            then open http://localhost:8765
(or double-click run_app.command)

To feel as fast as a normal chatbot, the app does three things AT THE SAME TIME:
  1. the AI starts answering from memory at once, word by word (the quick answer)
  2. the two checks run (does the answer change? does the AI know it?)
  3. sources are gathered in the background (Wikipedia + live web)
Easy questions: the checks agree, the quick answer stays.
Risky questions (outdated or unknown): the quick answer is replaced by an answer
written only from the sources, with links.

Runs only on this computer (localhost).
"""
from __future__ import annotations

import json
import queue
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src import knowledge_check, language, llm, pipeline, router, search, time_check
from src.llm import ROOT

PORT = 8765
PAGE = ROOT / "app" / "index.html"
LOG = ROOT / "results" / "app_log.jsonl"     # every question asked in the app, for checking later
MODEL = None


def run(question: str, emit):
    """Answer one question, sending events to the page as each part is ready."""
    global MODEL
    MODEL = MODEL or time_check.load()
    t0 = time.time()
    since = lambda: round(time.time() - t0, 1)

    def check1():   # instant for English; a Korean question is translated first
        group = time_check.classify(language.to_english(question), MODEL)
        emit("check1", {"group": router.GROUP_NAMES[group], "seconds": since()})

    with ThreadPoolExecutor(4) as pool:
        sources_job = pool.submit(pipeline.gather_sources, question)      # 3. in the background
        route_job = pool.submit(router.route, question, MODEL)            # 2. the two checks
        pool.submit(check1)                                               # shown as soon as ready

        # 1. quick answer from memory, word by word
        draft = ""
        for piece in llm.stream(pipeline.memory_prompt(question), max_tokens=150):
            draft += piece
            emit("draft", {"text": piece})
        emit("draft_done", {"seconds": since()})

        r = route_job.result()
        if r["group"] != "HIGH" and r.get("answers"):
            # strict check: the quick answer itself must not contradict the AI's other answers
            # (e.g. "in Yangyang" vs "in Gangneung" = the AI is guessing the city)
            strict = knowledge_check.judge_strict([draft] + r["answers"], question)
            r["agreement"] = strict["agreement"]
            if r["knows"] and not strict["knows"]:
                r["knows"] = False
                r["action"], _ = router.decide(r["group"], False)
                r["reason"] = "the quick answer contradicts the AI's other answers, so it is guessing"
        emit("checks", {"group": router.GROUP_NAMES[r["group"]], "knows": r["knows"],
                        "agreement": r["agreement"], "samples": r.get("answers", []),
                        "action": r["action"], "action_text": router.ACTIONS[r["action"]],
                        "reason": r["reason"], "seconds": since()})

        if r["action"] == "answer":
            emit("final", {"mode": "kept", "seconds": since()})
            return
        if r["action"] == "warn":
            emit("final", {"mode": "warn", "warning": pipeline.WARNING, "seconds": since()})
            return

        # risky: answer again, only from the sources
        pages = sources_job.result()
        emit("sources", {"sources": [{"title": p["title"], "url": p["url"],
                                      "retrieved": p.get("retrieved", "")} for p in pages],
                         "seconds": since()})
        if not pages:
            emit("final", {"mode": "not_found", "text": pipeline.NOT_FOUND, "seconds": since()})
            return
        text = ""
        for piece in llm.stream(pipeline.source_prompt(question, pages), max_tokens=250):
            text += piece
            emit("verified", {"text": piece})
        mode = "not_found" if "NOT FOUND" in text.upper() else "verified"
        emit("final", {"mode": mode, "text": pipeline.NOT_FOUND if mode == "not_found" else text,
                       "seconds": since()})


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
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        q = (data.get("question") or "").strip()[:500]
        if not q:
            return self._send(400, json.dumps({"error": "Type a question first."}).encode(),
                              "application/json")
        # stream events to the page as they happen (server-sent events)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        events = queue.Queue()

        log = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "question": q, "model": llm.model_name(),
               "draft": "", "verified": ""}

        def emit(kind, payload):
            if kind in ("draft", "verified"):
                log[kind] += payload["text"]
            elif kind != "draft_done":
                log[kind] = payload
            events.put((kind, payload))

        def work():
            try:
                run(q, emit)
            except Exception as e:
                emit("error", {"error": f"Something went wrong: {e}. Is Ollama running?"})
            try:   # every question is saved, so wrong answers can be looked into later
                with LOG.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(log, ensure_ascii=False) + "\n")
            except OSError:
                pass
            events.put(("end", {}))

        threading.Thread(target=work, daemon=True).start()
        while True:
            kind, payload = events.get()
            try:
                self.wfile.write(f"event: {kind}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                                 .encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return                              # the page was closed
            if kind == "end":
                return

    def log_message(self, *args):
        pass


def main():
    import os
    llm.load_env()
    os.environ.setdefault("TRR_FAST", "1")      # shorter pauses between Wikipedia requests
    print("Loading the AI model into memory ...", flush=True)
    threading.Thread(target=lambda: (llm.warm_up(), time_check.load()), daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Temporal-Risk Router demo running at {url}  (close this window to stop)")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
