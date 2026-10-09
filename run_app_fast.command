#!/bin/zsh
# Double-click in Finder: the demo app with a smaller, faster AI model (llama3.2, 3B).
# Answers come about 2-3x faster but are a little less accurate. Close this window to stop.
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
export OLLAMA_MODEL=llama3.2:3b
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
python -m src.app
