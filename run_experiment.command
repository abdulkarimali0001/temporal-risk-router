#!/bin/zsh
# Double-click in Finder: the main experiment on public benchmarks (FreshQA + PopQA).
#   1. llama3.1:8b  (main model)        -> results/experiment_report.md
#   2. qwen2.5:7b   (second model, to check the results hold for another AI)
#                                       -> results/experiment_report_qwen2.5-7b.md
# Takes a few hours the first time. Everything is cached, so it can be stopped and
# restarted and continues where it stopped.   Log: results/experiment.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee -a results/experiment.log) 2>&1
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
[ -f data/benchmark.csv ] && [ -f data/time_check_extra.csv ] || python -m src.benchmarks || { read "?Download failed. Press Enter to close"; exit 1; }

echo "=== Model 1: llama3.1:8b ==="
OLLAMA_MODEL=llama3.1:8b caffeinate -i python -m src.experiment
python -m src.evaluate_answers > /dev/null

echo "=== Model 2: qwen2.5:7b ==="
ollama list | grep -q "^qwen2.5:7b" || ollama pull qwen2.5:7b
OLLAMA_MODEL=qwen2.5:7b caffeinate -i python -m src.experiment

echo; read "?DONE. Press Enter to close"
