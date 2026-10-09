"""Shared access to the language model used by the checks and the answer step.

Choose the backend with AI_BACKEND in .env:
  ollama  - free local model via Ollama (https://ollama.com, must be running)
  claude  - Claude API (needs ANTHROPIC_API_KEY, small cost per call)
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLLAMA_HOST = "http://localhost:11434"


def load_env():
    """Settings and keys from .env and keys.txt (both stay on this computer, never uploaded)."""
    for name in (".env", "keys.txt"):
        env = ROOT / name
        if env.exists():
            for line in env.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    if v.strip():
                        os.environ.setdefault(k.strip(), v.strip())


def backend() -> str:
    load_env()
    return os.getenv("AI_BACKEND", "ollama")


def ollama_model() -> str:
    """The model set in OLLAMA_MODEL, else the first model installed in Ollama."""
    wanted = os.getenv("OLLAMA_MODEL")
    if wanted:
        return wanted
    host = os.getenv("OLLAMA_HOST", OLLAMA_HOST)
    with urllib.request.urlopen(f"{host}/api/tags", timeout=10) as r:
        models = [m["name"] for m in json.load(r).get("models", [])]
    if not models:
        raise SystemExit("Ollama has no models. Run e.g.:  ollama pull llama3.1:8b")
    return models[0]


def model_name() -> str:
    if backend() == "ollama":
        return ollama_model()
    return os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")


def generate(prompt: str, temperature: float = 0.0, max_tokens: int = 300) -> str:
    """One call to the language model; returns its text reply."""
    if backend() == "ollama":
        host = os.getenv("OLLAMA_HOST", OLLAMA_HOST)
        body = json.dumps({"model": ollama_model(), "prompt": prompt, "stream": False,
                           "options": {"temperature": temperature,
                                       "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "8192"))}}).encode()
        req = urllib.request.Request(f"{host}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)["response"].strip()

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set (add it to .env), or set AI_BACKEND=ollama")
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=model_name(), max_tokens=max_tokens, temperature=temperature,
        messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in msg.content if b.type == "text").strip()
