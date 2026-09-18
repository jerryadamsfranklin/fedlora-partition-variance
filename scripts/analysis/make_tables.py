#!/usr/bin/env python3
"""Phase J LaTeX tables in manuscript/tables/ from analysis/*.csv only."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
ANALYSIS = REPO / "analysis"
TABLES = REPO / "manuscript" / "tables"

METHOD_TEX = {"fedit": "FedIT", "ffa_lora": "FFA-LoRA", "flora": "FLoRA"}
MODEL_TEX = {"tl": "TinyLlama-1.1B", "l3": "LLaMA-3.2-3B"}


def _read(name: str) -> List[Dict[str, str]]:
    with (ANALYSIS / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(x: Any, fmt: str) -> str:
    try:
        return format(float(x), fmt)
    except (TypeError, ValueError):
        return str(x)


def tab1_setup() -> str:
    # From frozen Section 0 / SCOPE (static from plan; no hand-typed results numbers)
    return r"""\begin{tabular}{ll}
\toprule
Element & Value \\
\midrule
Methods & FedIT, FFA-LoRA, FLoRA \\
Models & TinyLlama-1.1B-Chat-v1.0; LLaMA-3.2-3B \\
LoRA & $r{=}16$, $\alpha{=}32$, dropout $0.1$, $q\_proj$+$v\_proj$ \\
Federation & 10 clients, full participation, 15 rounds, 1 local epoch \\
Data & Dolly-15k train$[0{:}3000]$; held-out train$[3000{:}3500]$ \\
Non-IID & Dirichlet label skew on \texttt{category}, $\alpha{=}0.1$ \\
IID & Fixed data seed split \\
Primary metric & Held-out loss (formatter \texttt{v2-dolly-context}) \\
Secondary & Measured communication (MB) \\
TinyLlama cells & 60 ($\alpha{=}0.1$) + 15 (IID) \\
LLaMA-3.2-3B cells & 36 ($\alpha{=}0.1$) + 9 (IID) \\
\bottomrule
\end{tabular}
"""


def tab2_variance() -> str:
    rows = _read("variance_components.csv")
    lines = [
        r"\begin{tabular}{lrrrlll}",
        r"\toprule",
        r"Model & $\hat\sigma^2_P$ & $\hat\sigma^2_{PM}$ & $\hat\sigma^2_E$ & Share $P$ & Share $PM$ & Share $E$ \\",
        r"\midrule",
    ]
    for r in rows:
        model = MODEL_TEX[r["model"]]
        share = (
            f"{_f(r['share_P'], '.3f')} [{_f(r['share_P_ci_lo'], '.3f')}, {_f(r['share_P_ci_hi'], '.3f')}]"
        )
        share_pm = (
            f"{_f(r['share_PM'], '.3f')} [{_f(r['share_PM_ci_lo'], '.3f')}, {_f(r['share_PM_ci_hi'], '.3f')}]"
        )
        share_e = (
            f"{_f(r['share_E'], '.3f')} [{_f(r['share_E_ci_lo'], '.3f')}, {_f(r['share_E_ci_hi'], '.3f')}]"
        )
        # scientific for variance components
        lines.append(
            f"{model} & {_f(r['s2_P'], '.2e')} & {_f(r['s2_PM'], '.2e')} & {_f(r['s2_E'], '.2e')} "
            f"& {share} & {share_pm} & {share_e} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    lines.append(
        r"% Shares show point estimate and percentile bootstrap 95\% CI over partitions ($B{=}2000$)."
    )
    return "\n".join(lines) + "\n"


def tab3_means_comm() -> str:
    means = _read("method_means.csv")
    comm = _read("comm.csv")
    parts = _read("partition_effects.csv")
    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Model & Method & Mean ($\alpha{=}0.1$) & SD & Comm.\ range (MB) & Active clients \\",
        r"\midrule",
    ]
    for model in ("tl", "l3"):
        for meth in ("fedit", "ffa_lora", "flora"):
            m = next(r for r in means if r["model"] == model and r["method"] == meth and r["het"] == "a01")
            c = next(r for r in comm if r["model"] == model and r["method"] == meth)
            # active range from partition_effects for this model
            act = [int(r["active_clients"]) for r in parts if r["model"] == model]
            lines.append(
                f"{MODEL_TEX[model]} & {METHOD_TEX[meth]} & "
                f"{_f(m['mean'], '.4f')} & {_f(m['sd'], '.4f')} & "
                f"{_f(c['comm_mb_min'], '.1f')}--{_f(c['comm_mb_max'], '.1f')} & "
                f"{min(act)}--{max(act)} \\\\"
            )
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    mapping = {
        "tab1_setup.tex": tab1_setup(),
        "tab2_variance.tex": tab2_variance(),
        "tab3_means_comm.tex": tab3_means_comm(),
    }
    for name, body in mapping.items():
        path = TABLES / name
        path.write_text(body, encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
