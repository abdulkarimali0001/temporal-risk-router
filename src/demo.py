"""Live demo: type any question and see how Version 1 and Version 2 sort it.

Run from the project folder:
    python -m src.demo

Type a question and press Enter. Type q to quit.
"""
from src import router_rules
from src.router_ml import train

NAMES = {"LOW": "LOW   -> answer from memory",
         "AMBIGUOUS": "MAYBE -> answer + warning",
         "HIGH": "HIGH  -> search the web first"}


def main():
    print("Training Version 2 on the 150 practice questions...")
    model = train()
    print("Ready! Try: 'Who runs Samsung?'  'What is photosynthesis?'  'What is the tuition fee?'\n")
    while True:
        question = input("Your question (q to quit): ").strip()
        if question.lower() in {"q", "quit", "exit"}:
            break
        if not question:
            continue
        print(f"  Version 1: {NAMES[router_rules.route(question)]}")
        print(f"  Version 2: {NAMES[model.predict([question])[0]]}\n")


if __name__ == "__main__":
    main()
