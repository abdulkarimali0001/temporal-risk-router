#!/bin/zsh
# Double-click in Finder: runs the demo questions with the free local model.
# Output: results/demo_output.txt   Log: results/demo.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee results/demo.log) 2>&1
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
caffeinate -i python -m src.demo
echo; read "?DONE. Press Enter to close"
