#!/bin/zsh
# Double-click in Finder: the same experiments with a BIGGER model, qwen2.5:14b (about 9 GB).
# Needs a Mac with at least 16 GB of memory. Takes about 6-10 hours: run it overnight,
# plugged in. If it stops, double-click again and it continues.   Log: results/experiment.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee -a results/experiment.log) 2>&1
MEM_GB=$(( $(sysctl -n hw.memsize) / 1073741824 ))
if [ "$MEM_GB" -lt 16 ]; then
  echo "This Mac has $MEM_GB GB of memory; qwen2.5:14b needs at least 16 GB. Stopping."
  read "?Press Enter to close"; exit 1
fi
export OLLAMA_MODEL=qwen2.5:14b
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
echo "=== Model: $OLLAMA_MODEL ($MEM_GB GB memory) ==="
caffeinate -i python -m src.experiment
caffeinate -i python -m src.evaluate_korean
caffeinate -i python -m src.evaluate_korean data/swahili_test.csv
./run_reports.command
echo; read "?DONE. Press Enter to close"
