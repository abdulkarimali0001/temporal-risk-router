"""Learned router: instead of hand-written rules, LEARN when to search.

The rule-based router (src/router.py) uses fixed rules on the two checks.
Here a small logistic-regression model looks at all the signals at once and
predicts "will the AI's memory answer be wrong?". If yes -> search.

Signals (all available BEFORE answering, no correct answer needed):
  time check     probability of LOW / MAYBE / HIGH        (Check 1)
  agreement      how much the 3 sampled answers agree    (Check 2)
  dont_know      how many of the 3 samples said "I don't know"
  confidence     the model's own 0-100 confidence
  abstained      the memory answer itself says it does not know

Training label: was the memory answer wrong? (from results/experiment_answers*.csv)
Evaluation: 5-fold cross-validation repeated 5 times (never tested on questions it
trained on), and cross-model transfer (train on llama, test on qwen and back).

    python -m src.learned_router
Output: results/learned_router_report.md, results/learned_router_chart.png,
        results/learned_router.joblib (trained on all data, used by the pipeline)
"""
from __future__ import annotations

import json
import random
from math import comb

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src import knowledge_check, time_check
from src.evaluate_answers import NO_GUESS
from src import benchmarks
from src.llm import ROOT

RESULTS = ROOT / "results"
MODEL_PATH = RESULTS / "learned_router.joblib"
REPORT = RESULTS / "learned_router_report.md"
CHART = RESULTS / "learned_router_chart.png"
def _runs() -> dict:
    from src.experiment import MODELS, answers_file
    return {m: RESULTS / answers_file(m) for m in MODELS}
FEATURES = ["p_low", "p_maybe", "p_high", "agreement", "dont_know", "confidence", "abstained"]
RULES = ["Never search", "Always search", "Self-consistency only", "Verbal confidence",
         "Router (ours)", "Router + cutoff rule (ours)", "Oracle (best possible)"]


# ---------- features ----------
def abstained(text: str) -> int:
    low = str(text).lower()
    return int(any(p in low for p in NO_GUESS))


def kc_answers(cache: dict, model: str, question: str) -> list[str]:
    keys = [f"ollama::{model}::{question}"]
    if model == "llama3.1:8b":                 # older cache entries had no model name
        keys.append(f"ollama::{question}")
    return next((cache[k] for k in keys if k in cache), [])


def features(question: str, kc: list[str], confidence: float, memory: str, tc_model) -> dict:
    probs = dict(zip(tc_model.classes_, tc_model.predict_proba([question])[0]))
    j = knowledge_check.judge(kc[:3]) if kc else {"agreement": 0.0, "said_dont_know": 3}
    s = knowledge_check.judge_strict([str(memory)] + kc[:3], question) if kc else None
    # strict check as a score: share of contradicting answer pairs + share of "I don't know"
    strict_risk = 1.0 if s is None else min(1.0, (1 - s["agreement"]) + s["said_dont_know"] / 4)
    return {"strict_risk": strict_risk,"p_low": probs.get("LOW", 0), "p_maybe": probs.get("AMBIGUOUS", 0),
            "p_high": probs.get("HIGH", 0), "agreement": j["agreement"],
            "dont_know": j["said_dont_know"] / 3, "confidence": float(confidence) / 100,
            "abstained": abstained(memory)}


def load_runs() -> pd.DataFrame:
    tc_model = time_check.load()
    kc_cache = json.loads((RESULTS / "knowledge_check_cache.json").read_text(encoding="utf-8"))
    frames = []
    for model, path in _runs().items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if len(df) < 100:                   # a run that has only just started
            continue
        feats = [features(r.question, kc_answers(kc_cache, model, r.question), r.confidence,
                          r.memory, tc_model) for r in df.itertuples()]
        df = df.drop(columns=[c for c in FEATURES if c in df.columns]).reset_index(drop=True)
        df = pd.concat([df, pd.DataFrame(feats)], axis=1)
        df["model"] = model
        df["mem_ok"] = (df["memory_score"] == "correct").astype(int)
        df["srch_ok"] = (df["search_score"] == "correct").astype(int)
        df["y"] = 1 - df["mem_ok"]          # 1 = memory answer wrong -> should search
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ---------- model + policy ----------
def make_model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000,
                                                              class_weight="balanced"))


def policy_accuracy(df: pd.DataFrame, search: np.ndarray) -> float:
    return float(np.where(search, df["srch_ok"], df["mem_ok"]).mean())


def pick_threshold(df: pd.DataFrame, p: np.ndarray) -> float:
    """Threshold with the best accuracy on the TRAINING data (ties: fewer searches)."""
    best = (-1, 0, 0.5)
    for t in np.linspace(0.05, 0.95, 37):
        s = p >= t
        best = max(best, (policy_accuracy(df, s), -s.mean(), t))
    return best[2]


def cross_validate(df: pd.DataFrame, repeats: int = 5, folds: int = 5) -> pd.DataFrame:
    """Out-of-fold decisions, averaged over repeats -> per-question search probability."""
    out = np.zeros(len(df))
    strat = df["model"] + "|" + df["type"]
    for rep in range(repeats):
        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=rep)
        for tr, te in skf.split(df, strat):
            m = make_model().fit(df.iloc[tr][FEATURES], df.iloc[tr]["y"])
            t = pick_threshold(df.iloc[tr], m.predict_proba(df.iloc[tr][FEATURES])[:, 1])
            out[te] += (m.predict_proba(df.iloc[te][FEATURES])[:, 1] >= t) / repeats
    return out >= 0.5        # majority vote over repeats


def transfer(df: pd.DataFrame, train_model: str, test_model: str) -> tuple[float, float]:
    tr, te = df[df["model"] == train_model], df[df["model"] == test_model]
    m = make_model().fit(tr[FEATURES], tr["y"])
    t = pick_threshold(tr, m.predict_proba(tr[FEATURES])[:, 1])
    s = m.predict_proba(te[FEATURES])[:, 1] >= t
    return policy_accuracy(te, s), float(s.mean())


def mcnemar(a_ok: np.ndarray, b_ok: np.ndarray) -> tuple[int, int, float]:
    x, y = int((a_ok & ~b_ok).sum()), int((~a_ok & b_ok).sum())
    n = x + y
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(x, y) + 1)) / 2 ** n)
    return x, y, p


# ---------- report ----------
def chart(df: pd.DataFrame, cv_search: np.ndarray, models: list[str]):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid, accent = "#111827", "#6B7280", "#E5E7EB", "#2563EB"
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4.6), dpi=200, squeeze=False)
    for ax, model in zip(axes[0], models):
        sub = df[df["model"] == model]
        for rule in RULES:
            x, y = sub[f"{rule}::searched"].mean() * 100, (sub[f"{rule}::score"] == "correct").mean() * 100
            ours = rule.startswith("Router")
            ax.scatter(x, y, s=55, color="white" if rule.startswith("Oracle") else muted,
                       edgecolors=muted, linewidths=1.4, zorder=3)
            ax.annotate(rule.replace(" (ours)", "").replace(" (best possible)", ""), (x, y),
                        xytext=(7, -4), textcoords="offset points", fontsize=8, color=ink)
        s = cv_search[sub.index]
        x, y = s.mean() * 100, policy_accuracy(sub, s) * 100
        ax.scatter(x, y, s=110, color=accent, zorder=4)
        ax.annotate("Learned router", (x, y), xytext=(8, 7), textcoords="offset points",
                    fontsize=10, color=ink, fontweight="bold")
        ax.set_title(model, loc="left", color=ink, fontsize=11)
        ax.set_xlabel("Questions searched (%)", color=ink)
        ax.set_ylabel("Correct answers (%)", color=ink)
        ax.set_xlim(-5, 118)
        ax.grid(color=grid, linewidth=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(grid)
        ax.tick_params(colors=muted)
    fig.tight_layout()
    fig.savefig(benchmarks.suffixed(CHART))
    plt.close(fig)


def main():
    df = load_runs()
    if len(df) < 50 or df["y"].nunique() < 2:
        print("Not enough experiment results yet for the learned router - run src.experiment first.")
        return
    models = list(df["model"].unique())
    cv_search = cross_validate(df)
    df["learned::searched"] = cv_search
    df["learned::ok"] = np.where(cv_search, df["srch_ok"], df["mem_ok"]).astype(bool)

    L = ["# Learned router\n",
         "A logistic-regression model predicts whether the memory answer will be wrong, from "
         f"signals available before answering: {', '.join(FEATURES)}. It decides to search when "
         "that is likely. Results are **out-of-fold** (5-fold cross-validation, repeated 5 times): "
         "every question is decided by a model that never saw it.\n",
         "## Accuracy and searches\n",
         "| Method | " + " | ".join(f"{m} correct | wrong | searched" for m in models) + " |",
         "|---|" + "---|---|---|" * len(models)]
    for rule in RULES[:-1] + ["Learned router (ours)", RULES[-1]]:
        cells = []
        for m in models:
            sub = df[df["model"] == m]
            if rule.startswith("Learned"):
                acc, sr = sub["learned::ok"].mean(), sub["learned::searched"].mean()
                wrong = int((np.where(sub["learned::searched"], sub["search_score"],
                                      sub["memory_score"]) == "wrong").sum())
            else:
                acc, sr = (sub[f"{rule}::score"] == "correct").mean(), sub[f"{rule}::searched"].mean()
                wrong = int((sub[f"{rule}::score"] == "wrong").sum())
            cells.append(f"{acc:.0%} | {wrong} | {sr:.0%}")
        name = f"**{rule}**" if rule.startswith("Learned") else rule
        L.append(f"| {name} | " + " | ".join(cells) + " |")

    L += ["", "## Is the learned router better? (paired McNemar test)\n",
          "| Model | Learned vs. | Only learned right | Only other right | p-value |",
          "|---|---|---|---|---|"]
    for m in models:
        sub = df[df["model"] == m]
        for rule in ["Always search", "Self-consistency only", "Router (ours)"]:
            x, y, p = mcnemar(sub["learned::ok"].values, (sub[f"{rule}::score"] == "correct").values)
            L.append(f"| {m} | {rule} | {x} | {y} | {p:.3f}{' *' if p < 0.05 else ''} |")

    if len(models) >= 2:
        L += ["", "## Does it transfer to another AI model?\n",
              "Trained on one model's questions, tested on another model (no retraining).\n",
              "| Trained on | Tested on | Correct | Searched |", "|---|---|---|---|"]
        for a, b in [(x, y) for x in models for y in models if x != y]:
            acc, sr = transfer(df, a, b)
            L.append(f"| {a} | {b} | {acc:.0%} | {sr:.0%} |")

    if benchmarks.current_set() == "heldout":
        # the cleanest test: trained ONLY on the development questions, decided on the held-out ones
        import os
        os.environ["TRR_SET"] = "dev"
        dev = load_runs()
        os.environ["TRR_SET"] = "heldout"
        L += ["", "## Trained on the development set, tested on the held-out set\n",
              "| Model | Correct | Searched | Always search |", "|---|---|---|---|"]
        for m in models:
            tr, te = dev[dev["model"] == m], df[df["model"] == m]
            if len(tr) < 100:
                continue
            fit = make_model().fit(tr[FEATURES], tr["y"])
            thr = pick_threshold(tr, fit.predict_proba(tr[FEATURES])[:, 1])
            s = fit.predict_proba(te[FEATURES])[:, 1] >= thr
            L.append(f"| {m} | {policy_accuracy(te, s):.0%} | {s.mean():.0%} | {te['srch_ok'].mean():.0%} |")

    final = make_model().fit(df[FEATURES], df["y"])
    coefs = final[-1].coef_[0]
    L += ["", "## What the model learned\n",
          "Weights of the final model (standardised signals; positive = more likely to search):\n",
          "| Signal | Weight |", "|---|---|"]
    L += [f"| {f} | {w:+.2f} |" for f, w in sorted(zip(FEATURES, coefs), key=lambda fw: -abs(fw[1]))]
    L += ["", "![Learned router](learned_router_chart.png)"]

    threshold = pick_threshold(df, final.predict_proba(df[FEATURES])[:, 1])
    joblib.dump({"model": final, "threshold": threshold, "features": FEATURES}, benchmarks.suffixed(MODEL_PATH))
    benchmarks.suffixed(REPORT).write_text("\n".join(L) + "\n", encoding="utf-8")
    chart(df, cv_search, models)
    print("\n".join(L))


if __name__ == "__main__":
    random.seed(0)
    main()
