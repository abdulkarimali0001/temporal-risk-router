#!/bin/zsh
# Double-click in Finder: runs the full evaluation with the free local model.
# Output: results/evaluation_report.md, results/router_decisions.csv,
#         results/answer_evaluation.md, results/answer_evaluation.csv   Log: results/evaluation.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee results/evaluation.log) 2>&1
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
caffeinate -i python -m src.evaluate
caffeinate -i python -m src.evaluate_answers
echo; read "?DONE. Press Enter to close"
