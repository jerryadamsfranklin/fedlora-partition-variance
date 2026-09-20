#!/usr/bin/env python3
"""Phase J figures: vector PDFs in figures/ from analysis/*.csv only.

SAI two-column widths: single = 242 pt, full = 505 pt. All fonts >= 8 pt at final size.
"""

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

# Exact template widths (points -> inches)
PT_SINGLE = 242.0
PT_FULL = 505.0
IN_SINGLE = PT_SINGLE / 72.0
IN_FULL = PT_FULL / 72.0

C = {
    "paired": "#0072B2",
    "unpaired": "#D55E00",
    "tie": "#000000",
    "sep1": "#D55E00",
    "sep2": "#009E73",
}
METHOD_LABEL = {"fedit": "FedIT", "ffa_lora": "FFA-LoRA", "flora": "FLoRA"}
MODEL_LABEL = {"tl": "TinyLlama-1.1B", "l3": "LLaMA-3.2-3B"}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 72,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


def _report_size(path: Path, min_font_pt: float) -> None:
    # Media box from matplotlib savefig bbox
    from matplotlib.backends.backend_pdf import PdfPages

    # Read with matplotlib PdfFileReader alternative: parse via file size + known figsize
    w_in, h_in = None, None
    # Prefer pikepdf/pypdf if present; else report from intended figsize stored beside
    try:
        from pypdf import PdfReader

        box = PdfReader(str(path)).pages[0].mediabox
        w_pt, h_pt = float(box.width), float(box.height)
    except Exception:
        # Fallback: use pdfminer-free approach via subprocess mdls not available;
        # report intended width from companion .sizetxt if written
        meta = path.with_suffix(".size.txt")
        if meta.is_file():
            w_pt, h_pt = [float(x) for x in meta.read_text().split()]
        else:
            w_pt = h_pt = float("nan")
    print(f"{path.name}: width={w_pt:.1f} pt, height={h_pt:.1f} pt, min_font={min_font_pt:.1f} pt")


def _savefig(fig: plt.Figure, path: Path, width_pt: float, height_in: float, min_font: float) -> Path:
    fig.set_size_inches(width_pt / 72.0, height_in)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.02)
    # bbox_inches=tight changes final size; re-save with fixed size and constrained layout instead
    plt.close(fig)
    # Re-open approach: write size metadata of intended target; then verify with a no-tight save
    path.with_suffix(".size.txt").write_text(f"{width_pt} {height_in * 72.0}\n", encoding="utf-8")
    _report_size(path, min_font)
    return path


def fig1_heldout() -> Path:
    """Full-width two-panel held-out loss figure.

    TinyLlama: IID, alpha 0.5, alpha 0.1 (three groups).
    LLaMA: IID, alpha 0.1 (two groups).
    """
    runs = pd.read_csv(ANALYSIS / "runs.csv")
    min_font = 8.0
    fig, axes = plt.subplots(1, 2, figsize=(IN_FULL, 2.6), sharey=False)
    # Order: mild → skew for left-to-right readability; TL has a05, L3 does not.
    het_by_model = {
        "tl": (("iid", "a05", "a01"), "left→right: IID, α=0.5, α=0.1"),
        "l3": (("iid", "a01"), "left: IID; right: α=0.1"),
    }
    for ax, model in zip(axes, ("tl", "l3")):
        sub = runs[runs.model == model]
        methods = ["fedit", "ffa_lora", "flora"]
        hets, annot = het_by_model[model]
        n_het = len(hets)
        # Center groups around each method tick; span grows with group count.
        offsets = {
            2: (-0.18, 0.18),
            3: (-0.28, 0.0, 0.28),
        }[n_het]
        rng = np.random.default_rng(0)
        for i, meth in enumerate(methods):
            for j, het in enumerate(hets):
                vals = sub[(sub.method == meth) & (sub.het == het)]
                if vals.empty:
                    continue
                x = i + offsets[j]
                seeds = vals["data_seed"].to_numpy()
                uniq = sorted(vals["data_seed"].unique())
                cmap = plt.cm.viridis(np.linspace(0.15, 0.85, max(len(uniq), 1)))
                seed_to_c = {s: cmap[k] for k, s in enumerate(uniq)}
                jitter = rng.uniform(-0.04, 0.04, size=len(vals))
                ax.scatter(
                    np.full(len(vals), x) + jitter,
                    vals["heldout_loss"],
                    c=[seed_to_c[s] for s in seeds],
                    s=12,
                    alpha=0.85,
                    edgecolors="none",
                    zorder=3,
                )
                ax.hlines(
                    vals["heldout_loss"].mean(),
                    x - 0.09,
                    x + 0.09,
                    colors="black",
                    linewidths=1.0,
                    zorder=4,
                )
        ax.set_xticks(range(len(methods)))
        ax.set_xticklabels([METHOD_LABEL[m] for m in methods])
        ax.set_title(MODEL_LABEL[model], fontsize=8)
        ax.set_xlabel("Method", fontsize=8)
        if model == "tl":
            ax.set_ylabel("Held-out loss", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.text(
            0.02,
            0.98,
            annot,
            transform=ax.transAxes,
            va="top",
            fontsize=8,
            color="#333333",
        )
        ax.grid(True, axis="y", alpha=0.3, linewidth=0.5)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.90, bottom=0.18, wspace=0.28)
    out = FIG / "fig1_heldout_loss.pdf"
    fig.set_size_inches(IN_FULL, 2.6)
    fig.savefig(out, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"{out.name}: width={PT_FULL:.1f} pt (target full), min_font={min_font:.1f} pt")
    return out


def fig2_rank_flip() -> Path:
    """Full-width: aggregate flips (top) + per-pair flips (bottom).

    TinyLlama from rank_flip.csv / rank_flip_pairs.csv (p=10 a01).
    LLaMA from rank_flip_l3_p10.csv / rank_flip_pairs_l3_p10.csv (p=10 primary).
    """
    rf_tl = pd.read_csv(ANALYSIS / "rank_flip.csv")
    rp_tl = pd.read_csv(ANALYSIS / "rank_flip_pairs.csv")
    rf_l3 = pd.read_csv(ANALYSIS / "rank_flip_l3_p10.csv")
    rp_l3 = pd.read_csv(ANALYSIS / "rank_flip_pairs_l3_p10.csv")
    min_font = 8.0
    fig = plt.figure(figsize=(IN_FULL, 4.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], hspace=0.55, wspace=0.32)
    ax_tl = fig.add_subplot(gs[0, 0])
    ax_l3 = fig.add_subplot(gs[0, 1])
    ax_pair_tl = fig.add_subplot(gs[1, 0])
    ax_pair_l3 = fig.add_subplot(gs[1, 1])

    for ax, model, rf in ((ax_tl, "tl", rf_tl), (ax_l3, "l3", rf_l3)):
        sub = rf[(rf.event == "best")].copy()
        if "model" in sub.columns:
            sub = sub[sub.model == model]
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
        ks = sorted(sub["k"].unique().tolist())
        ax.set_xticks(ks)
        ax.set_xticklabels([str(int(k)) for k in ks])
        ax.set_ylim(0, 1)
        ax.set_xlabel("Partitions drawn (k)", fontsize=8)
        ax.set_ylabel("P(best differs)" if model == "tl" else "", fontsize=8)
        title = MODEL_LABEL[model] + (" ($p{=}10$)" if model == "l3" else "")
        ax.set_title(title, fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.3, linewidth=0.5)
        if model == "tl":
            ax.legend(frameon=False, loc="upper right", fontsize=8)

    for ax, model, rp in ((ax_pair_tl, "tl", rp_tl), (ax_pair_l3, "l3", rp_l3)):
        sub = rp[rp.protocol == "paired"].copy()
        if "model" in sub.columns:
            sub = sub[sub.model == model]
        for pair, color, ls in (
            ("fedit-flora", C["tie"], "-"),
            ("fedit-ffa_lora", C["sep1"], "--"),
            ("ffa_lora-flora", C["sep2"], ":"),
        ):
            s = sub[sub.pair == pair].sort_values("k")
            if s.empty:
                continue
            gap = float(s["true_gap"].iloc[0])
            label = f"{pair.replace('-', ' vs ')} ({gap:+.4f})"
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
        ks = sorted(sub["k"].unique().tolist())
        ax.set_xticks(ks)
        ax.set_xticklabels([str(int(k)) for k in ks])
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("Partitions drawn (k)", fontsize=8)
        ax.set_ylabel("P(pair order flips)" if model == "tl" else "", fontsize=8)
        ax.set_title(f"{MODEL_LABEL[model]}: per-pair (paired)", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.3, linewidth=0.5)
        ax.legend(frameon=False, fontsize=8, loc="best")

    fig.subplots_adjust(left=0.09, right=0.99, top=0.94, bottom=0.10)
    out = FIG / "fig2_rank_flip.pdf"
    fig.set_size_inches(IN_FULL, 4.8)
    fig.savefig(out, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"{out.name}: width={PT_FULL:.1f} pt (target full), min_font={min_font:.1f} pt")
    return out


def fig3_power() -> Path:
    """Full-width draws-needed figure (preregistered deltas + observed near-tie).

    TinyLlama from power.csv; LLaMA from power_l3_p10.csv (p=10; near-tie >1000).
    """
    power_tl = pd.read_csv(ANALYSIS / "power.csv")
    power_l3 = pd.read_csv(ANALYSIS / "power_l3_p10.csv")
    min_font = 8.0

    def _n_num(v):
        if isinstance(v, str) and "more" in str(v).lower():
            return 1000.0
        return float(v)

    fig, axes = plt.subplots(1, 2, figsize=(IN_FULL, 2.7), sharey=True)
    for ax, model, power in zip(axes, ("tl", "l3"), (power_tl, power_l3)):
        pre = power[power.kind == "preregistered_delta"].copy()
        if "model" in pre.columns:
            pre = pre[pre.model == model]
        pre = pre.sort_values("delta").reset_index(drop=True)
        obs = power[(power.kind == "observed_gap") & (power.pair == "fedit-flora")].copy()
        if "model" in obs.columns:
            obs = obs[obs.model == model]
        xs = np.arange(len(pre), dtype=float)
        for protocol, col, key, mark in (
            ("paired", C["paired"], "n_paired", "o"),
            ("unpaired", C["unpaired"], "n_unpaired_per_method", "s"),
        ):
            ys = [_n_num(v) for v in pre[key]]
            ax.plot(
                xs,
                ys,
                marker=mark,
                markersize=4,
                linewidth=1.2,
                color=col,
                label=protocol,
            )
        if not obs.empty:
            n_raw = obs["n_paired"].iloc[0]
            n_paired = _n_num(n_raw)
            gap = abs(float(obs["delta"].iloc[0]))
            x_star = float(len(pre)) + 0.35
            ax.scatter(
                [x_star],
                [n_paired],
                marker="*",
                s=70,
                color=C["tie"],
                zorder=5,
                label="obs. near-tie (paired)",
            )
            n_lab = "more than 1000" if isinstance(n_raw, str) and "more" in str(n_raw).lower() else f"n={int(n_paired)}"
            # Place the near-tie label below the star when it sits on the cap line
            # (LLaMA >1000), otherwise above-left as before.
            if n_paired >= 900:
                xytext = (x_star - 0.05, 120)
                va = "bottom"
            else:
                xytext = (x_star - 0.15, n_paired * 0.55)
                va = "top"
            ax.annotate(
                f"{n_lab}\n(|g|={gap:.4f})",
                xy=(x_star, n_paired),
                xytext=xytext,
                fontsize=8,
                color=C["tie"],
                arrowprops=dict(arrowstyle="-", color=C["tie"], lw=0.7),
                ha="right",
                va=va,
            )
        ax.set_yscale("log")
        ax.set_xlabel(r"Detectable $\Delta$ / observed gap", fontsize=8)
        if model == "tl":
            ax.set_ylabel("Partitions needed (n)", fontsize=8)
        title = MODEL_LABEL[model] + (" ($p{=}10$)" if model == "l3" else "")
        ax.set_title(title, fontsize=8)
        tick_x = list(xs) + ([float(len(pre)) + 0.35] if not obs.empty else [])
        tick_lab = [f"{d:g}" for d in pre["delta"]] + (["near-tie"] if not obs.empty else [])
        ax.set_xticks(tick_x)
        ax.set_xticklabels(tick_lab, fontsize=8)
        ax.set_xlim(-0.35, float(len(pre)) + 0.9)
        ax.tick_params(labelsize=8)
        ax.grid(True, which="both", alpha=0.3, linewidth=0.5)
        if model == "tl":
            ax.legend(frameon=False, fontsize=8, loc="upper left")
        ax.axhline(1000, color="#888888", linewidth=0.6, linestyle="--")
        # Cap label only on TinyLlama; on LLaMA it collides with the >1000 star.
        if model == "tl":
            ax.text(
                0.98,
                0.92,
                "cap >1000",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=8,
                color="#555555",
            )
    fig.subplots_adjust(left=0.09, right=0.99, top=0.88, bottom=0.20, wspace=0.25)
    out = FIG / "fig3_draws_needed.pdf"
    fig.set_size_inches(IN_FULL, 2.7)
    fig.savefig(out, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"{out.name}: width={PT_FULL:.1f} pt (target full), min_font={min_font:.1f} pt")
    return out


def main() -> None:
    _style()
    FIG.mkdir(parents=True, exist_ok=True)
    for fn in (fig1_heldout, fig2_rank_flip, fig3_power):
        fn()


if __name__ == "__main__":
    main()
