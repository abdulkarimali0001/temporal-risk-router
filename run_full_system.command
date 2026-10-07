#!/bin/zsh
# Group 4 - Full system demo: router + Wikipedia search + answer, with the free local model.
# Double-click this file in Finder. Output is saved to results/full_system_demo.txt
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee results/full_system_log.txt) 2>&1
echo "=== run started $(date) ==="
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Ollama.app/Contents/Resources:$PATH"
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
  echo "Starting Ollama..."; open -a Ollama 2>/dev/null || (ollama serve >/dev/null 2>&1 &)
  for i in {1..30}; do curl -s http://localhost:11434/api/tags >/dev/null && break; sleep 2; done
fi
# Rebuild the Python environment if it is missing or broken (e.g. after moving the folder)
if ! .venv/bin/python -c "import sklearn, pandas" 2>/dev/null; then
  echo "Setting up Python environment..."; python3 -m venv --clear .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
export CONFIDENCE_BACKEND=ollama
caffeinate -i python -m src.full_system --demo
echo; read "?DONE. Press Enter to close"
