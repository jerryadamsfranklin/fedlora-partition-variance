#!/usr/bin/env python3
"""Phase J figures: vector PDFs in figures/ from analysis/*.csv only."""

from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
ANALYSIS = REPO / "analysis"
FIG = REPO / "figures"

# Colorblind-safe (Okabe-Ito)
C = {
    "fedit": "#0072B2",
    "ffa_lora": "#D55E00",
    "flora": "#009E73",
    "paired": "#0072B2",
    "unpaired": "#D55E00",
    "tl": "#0072B2",
    "l3": "#E69F00",
}
METHOD_LABEL = {"fedit": "FedIT", "ffa_lora": "FFA-LoRA", "flora": "FLoRA"}
MODEL_LABEL = {"tl": "TinyLlama-1.1B", "l3": "LLaMA-3.2-3B"}


def _style():
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def fig1_heldout() -> Path:
    runs = pd.read_csv(ANALYSIS / "runs.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2), sharey=False)
    for ax, model in zip(axes, ("tl", "l3")):
        sub = runs[runs.model == model]
        # x positions: method groups, IID vs a01 side by side
        methods = ["fedit", "ffa_lora", "flora"]
        rng = np.random.default_rng(0)
        for i, meth in enumerate(methods):
            for j, het in enumerate(("iid", "a01")):
                vals = sub[(sub.method == meth) & (sub.het == het)]
                if vals.empty:
                    continue
                x = i + (j - 0.5) * 0.35
                # color points by partition (data_seed)
                seeds = vals["data_seed"].to_numpy()
                uniq = sorted(vals["data_seed"].unique())
                cmap = plt.cm.viridis(np.linspace(0.15, 0.85, max(len(uniq), 1)))
                seed_to_c = {s: cmap[k] for k, s in enumerate(uniq)}
                jitter = rng.uniform(-0.06, 0.06, size=len(vals))
                ax.scatter(
                    np.full(len(vals), x) + jitter,
                    vals["heldout_loss"],
                    c=[seed_to_c[s] for s in seeds],
                    s=14,
                    alpha=0.85,
                    edgecolors="none",
                    zorder=3,
                )
                # mean marker
                ax.hlines(
                    vals["heldout_loss"].mean(),
                    x - 0.12,
                    x + 0.12,
                    colors="black",
                    linewidths=1.0,
                    zorder=4,
                )
        ax.set_xticks(range(len(methods)))
        ax.set_xticklabels([METHOD_LABEL[m] for m in methods])
        ax.set_title(MODEL_LABEL[model])
        ax.set_xlabel("Method")
        if model == "tl":
            ax.set_ylabel("Held-out loss")
        # legend proxy for het
        from matplotlib.lines import Line2D

        handles = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#555555", markersize=5, label="IID"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#555555", markersize=5, label="alpha 0.1"),
        ]
        # annotate offset groups
        ax.text(0 - 0.17, ax.get_ylim()[1] if False else sub["heldout_loss"].max(), "", fontsize=6)
        ax.annotate(
            "left: IID   right: alpha 0.1",
            xy=(0.02, 0.98),
            xycoords="axes fraction",
            va="top",
            fontsize=6,
            color="#333333",
        )
        ax.grid(True, axis="y", alpha=0.3, linewidth=0.5)
    fig.tight_layout()
    out = FIG / "fig1_heldout_loss.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig2_rank_flip() -> Path:
    rf = pd.read_csv(ANALYSIS / "rank_flip.csv")
    rp = pd.read_csv(ANALYSIS / "rank_flip_pairs.csv")
    # main: P(best) paired/unpaired by model
    fig = plt.figure(figsize=(7.2, 4.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.45, wspace=0.3)
    ax_tl = fig.add_subplot(gs[0, 0])
    ax_l3 = fig.add_subplot(gs[0, 1])
    ax_pair_tl = fig.add_subplot(gs[1, 0])
    ax_pair_l3 = fig.add_subplot(gs[1, 1])

    for ax, model in ((ax_tl, "tl"), (ax_l3, "l3")):
        sub = rf[(rf.model == model) & (rf.event == "best")]
        for protocol, color in (("paired", C["paired"]), ("unpaired", C["unpaired"])):
            s = sub[sub.protocol == protocol].sort_values("k")
            ax.errorbar(
                s["k"],
                s["prob"],
                yerr=[s["prob"] - s["wilson_lo"], s["wilson_hi"] - s["prob"]],
                marker="o",
                markersize=4,
                linewidth=1.2,
                capsize=2,
                color=color,
                label=protocol,
            )
        ax.set_ylim(0, 1)
        ax.set_xlabel("Partitions drawn (k)")
        ax.set_ylabel("P(best differs)" if model == "tl" else "")
        ax.set_title(MODEL_LABEL[model])
        ax.grid(True, alpha=0.3, linewidth=0.5)
        if model == "tl":
            ax.legend(frameon=False, loc="upper right")

    # pair inset panels: paired protocol only
    for ax, model in ((ax_pair_tl, "tl"), (ax_pair_l3, "l3")):
        sub = rp[(rp.model == model) & (rp.protocol == "paired")]
        for pair, color, ls in (
            ("fedit-flora", "#000000", "-"),
            ("fedit-ffa_lora", C["ffa_lora"], "--"),
            ("ffa_lora-flora", C["flora"], ":"),
        ):
            s = sub[sub.pair == pair].sort_values("k")
            if s.empty:
                continue
            gap = float(s["true_gap"].iloc[0])
            label = f"{pair.replace('-', ' vs ')} (gap {gap:+.4f})"
            ax.plot(
                s["k"],
                s["prob_order_flip"],
                marker="o",
                markersize=3.5,
                linewidth=1.2,
                color=color,
                linestyle=ls,
                label=label,
            )
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("Partitions drawn (k)")
        ax.set_ylabel("P(pair order flips)" if model == "tl" else "")
        ax.set_title(f"{MODEL_LABEL[model]}: per-pair (paired)")
        ax.grid(True, alpha=0.3, linewidth=0.5)
        ax.legend(frameon=False, fontsize=5.5, loc="best")

    out = FIG / "fig2_rank_flip.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def fig3_power() -> Path:
    power = pd.read_csv(ANALYSIS / "power.csv")
    pre = power[power.kind == "preregistered_delta"].copy()

    def _n_num(v):
        if isinstance(v, str) and "more" in v:
            return 1000
        return float(v)

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
    for ax, model in zip(axes, ("tl", "l3")):
        sub = pre[pre.model == model].sort_values("delta")
        for protocol, col, key in (
            ("paired", C["paired"], "n_paired"),
            ("unpaired", C["unpaired"], "n_unpaired_per_method"),
        ):
            ys = [_n_num(v) for v in sub[key]]
            ax.plot(
                sub["delta"],
                ys,
                marker="o",
                markersize=4,
                linewidth=1.2,
                color=col,
                label=protocol,
            )
        ax.set_xscale("linear")
        ax.set_yscale("log")
        ax.set_xlabel("Detectable Delta (held-out loss)")
        if model == "tl":
            ax.set_ylabel("Partitions needed (n)")
        ax.set_title(MODEL_LABEL[model])
        ax.set_xticks(sub["delta"].tolist())
        ax.set_xticklabels([f"{d:g}" for d in sub["delta"]])
        ax.grid(True, which="both", alpha=0.3, linewidth=0.5)
        if model == "tl":
            ax.legend(frameon=False)
        ax.axhline(1000, color="#888888", linewidth=0.6, linestyle="--")
        ax.text(0.05, 0.02, "cap: more than 1000", transform=ax.transAxes, fontsize=6, color="#555555")
    fig.tight_layout()
    out = FIG / "fig3_draws_needed.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    _style()
    FIG.mkdir(parents=True, exist_ok=True)
    outs = [fig1_heldout(), fig2_rank_flip(), fig3_power()]
    for p in outs:
        print(f"Wrote {p}")


if __name__ == "__main__":
    main()
