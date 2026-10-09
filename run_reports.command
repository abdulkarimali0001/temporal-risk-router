#!/bin/zsh
# Rebuilds every report from the saved answers (no AI needed, a few minutes).
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || source ./setup.sh
python -m src.rescore
python -m src.learned_router
python -m src.curves
python -m src.cost
[ -f results/timing.csv ] && python -m src.timing --report
