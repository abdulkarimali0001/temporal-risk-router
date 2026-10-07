#!/bin/zsh
# Group 4 - Week 3: run the Two-Signal Router with a FREE local model (Ollama).
# Double-click this file in Finder. It sets everything up and saves the results.
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
LOG=results/week3_output.txt
mkdir -p results
exec > >(tee "$LOG") 2>&1
echo "=== Week 3 local run: $(date) ==="

# 1. Find Ollama
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Ollama.app/Contents/Resources:$PATH"
if ! command -v ollama >/dev/null; then
  echo "STEP FAILED: Ollama is not installed. Download it from https://ollama.com, then run this file again."
  read "?Press Enter to close"; exit 1
fi
echo "Ollama found: $(command -v ollama)"

# 2. Start Ollama if it is not running
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
  echo "Starting Ollama..."
  open -a Ollama 2>/dev/null || (ollama serve >/dev/null 2>&1 &)
  for i in {1..30}; do curl -s http://localhost:11434/api/tags >/dev/null && break; sleep 2; done
fi
curl -s http://localhost:11434/api/tags >/dev/null || { echo "STEP FAILED: Ollama did not start."; read "?Press Enter to close"; exit 1; }

# 3. Make sure a model exists (downloads llama3.2, about 2 GB, only the first time)
echo "Installed models:"; ollama list
if [ "$(ollama list | wc -l)" -le 1 ]; then
  echo "No model yet - downloading llama3.2 (about 2 GB)..."
  ollama pull llama3.2 || { echo "STEP FAILED: model download"; read "?Press Enter to close"; exit 1; }
fi

# 4. Python environment
if ! .venv/bin/python -c "import sklearn, pandas" 2>/dev/null; then
  echo "Creating Python environment..."
  python3 -m venv --clear .venv || { echo "STEP FAILED: python3 venv"; read "?Press Enter to close"; exit 1; }
fi
source .venv/bin/activate
echo "Python: $(python --version)"
pip install -q -r requirements.txt || { echo "STEP FAILED: pip install"; read "?Press Enter to close"; exit 1; }

# 5. Run Week 3
export CONFIDENCE_BACKEND=ollama
echo; echo "--- One question, both signals ---"
python -m src.two_signal "Who was the founding president of Kyungdong University?"
echo; echo "--- Full Week 3 test (45 questions) ---"
python -m src.week3_results
echo; echo "=== DONE. Output saved to $LOG ==="
read "?Press Enter to close"
