#!/bin/zsh
# Double-click in Finder: opens the demo in your browser (http://localhost:8765).
# Close this Terminal window to stop it.
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
python -m src.app
