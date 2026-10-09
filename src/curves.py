"""Accuracy at every search budget: a curve per method instead of one point.

Each method gives every question a "search need" score. Searching the top k% of
questions by that score, for k = 0 ... 100, gives a curve of accuracy against the
share of questions searched. A better method is higher at every budget.

  Time check           p(HIGH) + 0.5 p(MAYBE)
  Self-consistency     (1 - agreement) + share of "I don't know" samples
  Verbal confidence    1 - stated confidence
  Router (ours)        the larger of the time risk and the knowledge risk (no training)
  Learned router (ours) out-of-fold probability that the memory answer is wrong
  Random               searches questions at random (a straight line)
  Oracle               searches only where it helps (the upper bound)

Summary numbers: area under the curve (mean accuracy over all budgets) with a 95%
bootstrap interval, and accuracy at 25%, 50% and 75% of questions searched.

    python -m src.curves
Output: results/curves_report.md, results/curves_chart.png
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from src import learned_router as lr
from src.llm import ROOT

REPORT = ROOT / "results" / "curves_report.md"
CHART = ROOT / "results" / "curves_chart.png"
BUDGETS = [0.25, 0.50, 0.75]
METHODS = ["Time check", "Self-consistency", "Verbal confidence", "Router (ours)",
           "Learned router (ours)", "Random", "Oracle"]


def oof_probability(df: pd.DataFrame, folds: int = 5, repeats: int = 5) -> np.ndarray:
    """Learned router: probability from models that never saw the question."""
    p = np.zeros(len(df))
    strat = df["model"] + "|" + df["type"]
    for rep in range(repeats):
        for tr, te in StratifiedKFold(folds, shuffle=True, random_state=rep).split(df, strat):
            m = lr.make_model().fit(df.iloc[tr][lr.FEATURES], df.iloc[tr]["y"])
            p[te] += m.predict_proba(df.iloc[te][lr.FEATURES])[:, 1] / repeats
    return p


def scores(df: pd.DataFrame) -> dict[str, np.ndarray]:
    time_risk = (df["p_high"] + 0.5 * df["p_maybe"]).to_numpy()
    know_risk = np.clip((1 - df["agreement"]) + df["dont_know"], 0, 1).to_numpy()
    gain = df["srch_ok"].to_numpy() - df["mem_ok"].to_numpy()        # +1 helps, -1 hurts
    return {"Time check": time_risk,
            "Self-consistency": know_risk,
            "Verbal confidence": 1 - df["confidence"].to_numpy(),
            "Router (ours)": np.maximum(time_risk, know_risk),
            "Learned router (ours)": df["learned_p"].to_numpy(),
            "Oracle": gain.astype(float)}


def curve(score: np.ndarray, mem_ok: np.ndarray, srch_ok: np.ndarray, seeds: int = 20) -> np.ndarray:
    """Accuracy when searching the top-k questions, k = 0..n (ties broken at random, averaged)."""
    n, acc = len(score), np.zeros(len(score) + 1)
    rng = np.random.default_rng(0)
    for _ in range(seeds):
        order = np.lexsort((rng.random(n), -score))                  # highest need first
        gain = (srch_ok[order] - mem_ok[order]).astype(float)
        acc += (mem_ok.sum() + np.concatenate([[0], np.cumsum(gain)])) / n / seeds
    return acc


def random_curve(mem_ok, srch_ok) -> np.ndarray:
    n = len(mem_ok)
    return mem_ok.mean() + (srch_ok.mean() - mem_ok.mean()) * np.arange(n + 1) / n


def at(c: np.ndarray, budget: float) -> float:
    return float(c[int(round(budget * (len(c) - 1)))])


def auc_ci(score, mem_ok, srch_ok, boot: int = 300) -> tuple[float, float]:
    rng = np.random.default_rng(1)
    vals = []
    for _ in range(boot):
        i = rng.integers(0, len(score), len(score))
        vals.append(curve(score[i], mem_ok[i], srch_ok[i], seeds=3).mean())
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def paired_diff(a, b, mem_ok, srch_ok, boot: int = 500) -> tuple[float, float, float]:
    """Area of method a minus area of method b on the SAME resampled questions:
    (difference, 95% low, 95% high). An interval above 0 = a is reliably better."""
    rng = np.random.default_rng(2)
    d = curve(a, mem_ok, srch_ok).mean() - curve(b, mem_ok, srch_ok).mean()
    vals = []
    for _ in range(boot):
        i = rng.integers(0, len(a), len(a))
        vals.append(curve(a[i], mem_ok[i], srch_ok[i], seeds=3).mean()
                    - curve(b[i], mem_ok[i], srch_ok[i], seeds=3).mean())
    return float(d), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


RATIOS = [1, 2, 3, 5, 10]       # cost of a wrong answer, in searches


def best_cost(c: np.ndarray, ratio: float) -> tuple[float, float]:
    """A cost-aware router: pick the search budget that minimises
    (share searched) + ratio * (share not correct). Returns (cost, budget)."""
    k = np.linspace(0, 1, len(c))
    cost = k + ratio * (1 - c)
    i = int(np.argmin(cost))
    return float(cost[i]), float(k[i])


def chart(curves_by_model: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid, accent = "#111827", "#9CA3AF", "#E5E7EB", "#2563EB"
    style = {"Router (ours)": dict(color=accent, lw=2.6),
             "Learned router (ours)": dict(color=accent, lw=1.6, ls="--"),
             "Self-consistency": dict(color="#6B7280", lw=1.4),
             "Verbal confidence": dict(color="#6B7280", lw=1.4, ls=":"),
             "Time check": dict(color=muted, lw=1.2, ls="-."),
             "Random": dict(color=muted, lw=1.0, ls=(0, (1, 3))),
             "Oracle": dict(color="#111827", lw=1.0, ls="--")}
    fig, axes = plt.subplots(1, len(curves_by_model), figsize=(6.4 * len(curves_by_model), 4.8),
                             dpi=200, squeeze=False)
    for ax, (model, cs) in zip(axes[0], curves_by_model.items()):
        for m in METHODS:
            c = cs[m]
            x = np.linspace(0, 100, len(c))
            ax.plot(x, c * 100, label=m, **style[m])
        ax.set_title(model, loc="left", color=ink, fontsize=12)
        ax.set_xlabel("Questions searched (%)", color=ink)
        ax.set_ylabel("Correct answers (%)", color=ink)
        ax.grid(color=grid, linewidth=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors="#6B7280")
    axes[0][0].legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.suptitle("Accuracy at every search budget (higher is better)", x=0.01, ha="left",
                 color=ink, fontsize=13)
    fig.tight_layout()
    fig.savefig(CHART)
    plt.close(fig)


def main():
    df = lr.load_runs()
    df["learned_p"] = oof_probability(df)
    L = ["# Accuracy at every search budget\n",
         "Each method ranks the questions by how much they need a search; searching the top "
         "k% gives accuracy at that budget. **Area** = mean accuracy over all budgets from 0% "
         "to 100% (higher is better), with a 95% bootstrap interval. The learned router uses "
         "out-of-fold probabilities (never tested on a question it trained on).\n",
         "![Curves](curves_chart.png)\n"]
    curves_by_model = {}
    for model in df["model"].unique():
        sub = df[df["model"] == model].reset_index(drop=True)
        mem_ok, srch_ok = sub["mem_ok"].to_numpy(), sub["srch_ok"].to_numpy()
        sc = scores(sub)
        cs = {m: curve(s, mem_ok, srch_ok) for m, s in sc.items()}
        cs["Random"] = random_curve(mem_ok, srch_ok)
        curves_by_model[model] = cs
        L += [f"## {model} ({len(sub)} questions)\n",
              f"Never search {mem_ok.mean():.0%} · always search {srch_ok.mean():.0%}\n",
              "| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |",
              "|---|---|---|---|---|"]
        for m in METHODS:
            c = cs[m]
            ci = "" if m in ("Random", "Oracle") else \
                " ({:.1%}-{:.1%})".format(*auc_ci(sc[m], mem_ok, srch_ok))
            name = f"**{m}**" if "ours" in m else m
            L.append(f"| {name} | {c.mean():.1%}{ci} | " +
                     " | ".join(f"{at(c, b):.0%}" for b in BUDGETS) + " |")
        L += ["", "Paired comparison of areas (same questions resampled; an interval above zero "
              "means the router is reliably better):\n",
              "| Router (ours) vs. | Difference in area | 95% interval |", "|---|---|---|"]
        for m in ["Time check", "Self-consistency", "Verbal confidence"]:
            d, lo, hi = paired_diff(sc["Router (ours)"], sc[m], mem_ok, srch_ok)
            L.append(f"| {m} | {d * 100:+.1f} points | {lo * 100:+.1f} to {hi * 100:+.1f}"
                     f"{' *' if lo > 0 else ''} |")
        rnd = cs["Random"].mean()
        L.append(f"| Random | {(cs['Router (ours)'].mean() - rnd) * 100:+.1f} points | |")
        L += ["", "**Cost model.** Total cost per question = share searched + R x share not correct, "
              "where R = how many searches one wrong or missing answer is worth. Each method searches "
              "the budget that is cheapest for that R (its best point on the curve). Cost relative to "
              "always searching (lower is better); in brackets the share of questions searched.\n",
              "| Method | " + " | ".join(f"R = {r}" for r in RATIOS) + " |",
              "|---|" + "---|" * len(RATIOS)]
        for m in ["Never search", "Always search"] + [x for x in METHODS if x not in ("Oracle",)]:
            cells = []
            for r in RATIOS:
                always = 1 + r * (1 - srch_ok.mean())
                if m == "Never search":
                    cost, k = r * (1 - mem_ok.mean()), 0.0
                elif m == "Always search":
                    cost, k = always, 1.0
                else:
                    cost, k = best_cost(cs[m], r)
                cells.append(f"{cost / always:.2f} ({k:.0%})")
            name = f"**{m}**" if "ours" in m else m
            L.append(f"| {name} | " + " | ".join(cells) + " |")
        L.append("")
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    chart(curves_by_model)
    print("\n".join(L))


if __name__ == "__main__":
    main()
