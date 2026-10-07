# Shared setup for the .command files: start Ollama and prepare Python.
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Ollama.app/Contents/Resources:$PATH"
export AI_BACKEND="${AI_BACKEND:-ollama}" OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.1:8b}"
echo "=== $(date) ==="
if ! command -v ollama >/dev/null; then echo "Ollama is not installed: https://ollama.com"; return 1; fi
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
  echo "Starting Ollama..."; open -a Ollama 2>/dev/null || (ollama serve >/dev/null 2>&1 &)
  for i in {1..30}; do curl -s http://localhost:11434/api/tags >/dev/null && break; sleep 2; done
fi
ollama list | grep -q "^${OLLAMA_MODEL}" || ollama pull "$OLLAMA_MODEL" || return 1
if ! .venv/bin/python -c "import sklearn, pandas" 2>/dev/null; then
  echo "Setting up Python environment..."; python3 -m venv --clear .venv || return 1
fi
source .venv/bin/activate
pip install -q -r requirements.txt || return 1
