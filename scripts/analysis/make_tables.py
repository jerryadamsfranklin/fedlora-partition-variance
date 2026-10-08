#!/usr/bin/env python3
"""Phase J/P5 LaTeX tables in manuscript/tables/ from analysis/*.csv only."""

from __future__ import annotations

import csv
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
ANALYSIS = REPO / "analysis"
TABLES = REPO / "manuscript" / "tables"

METHOD_TEX = {"fedit": "FedIT", "ffa_lora": "FFA-LoRA", "flora": "FLoRA"}
MODEL_TEX = {"tl": "TinyLlama-1.1B", "l3": "LLaMA-3.2-3B"}


def _read(name: str) -> List[Dict[str, str]]:
    with (ANALYSIS / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sci_tex(x: Any) -> str:
    """Typeset a float as $a.bc{\\times}10^{k}$; exact zero as 0."""
    v = float(x)
    if v == 0.0:
        return "0"
    # Two significant digits after the leading digit via .2e, then rewrite.
    mant_s, exp_s = f"{v:.2e}".split("e")
    mant = float(mant_s)
    exp = int(exp_s)
    # Normalize sign of mantissa into the exponent form used in the paper.
    return f"${mant:g}{{\\times}}10^{{{exp}}}$"


def round_half_up(x: Any, places: int = 1) -> str:
    """Round half up to ``places`` decimal places; return formatted string."""
    q = Decimal("1").scaleb(-places)
    d = Decimal(str(float(x))).quantize(q, rounding=ROUND_HALF_UP)
    return f"{d:.{places}f}"


def fmt_range(lo: Any, hi: Any, places: int = 1) -> str:
    """Format a numeric range; collapse to one value when endpoints match."""
    a = round_half_up(lo, places)
    b = round_half_up(hi, places)
    if a == b:
        return a
    return f"{a}--{b}"


def fmt_int_range(lo: int, hi: int) -> str:
    if lo == hi:
        return str(lo)
    return f"{lo}--{hi}"


def _f(x: Any, fmt: str) -> str:
    try:
        return format(float(x), fmt)
    except (TypeError, ValueError):
        return str(x)


def tab1_setup() -> str:
    return r"""\begin{tabular}{ll}
\toprule
Element & Value \\
\midrule
Methods & FedIT, FFA-LoRA, FLoRA \\
Models & TinyLlama-1.1B-Chat-v1.0; LLaMA-3.2-3B \\
LoRA & $r{=}16$, $\alpha_{\mathrm{LoRA}}{=}32$, dropout $0.1$, $q\_proj$+$v\_proj$ \\
Federation & 10 clients, full participation, 15 rounds, 1 local epoch \\
Data & Dolly-15k train$[0{:}3000]$; held-out train$[3000{:}3500]$ \\
Non-IID & Dirichlet label skew on \texttt{category}, $\alpha{=}0.1$ and $0.5$ \\
IID & Fixed data seed split \\
Primary metric & Held-out loss (formatter \texttt{v2-dolly-context}) \\
Secondary & Measured communication (MB) \\
TinyLlama cells & 60 ($\alpha{=}0.1$) + 60 ($\alpha{=}0.5$) + 15 (IID) \\
LLaMA-3.2-3B cells & 60 ($\alpha{=}0.1$, $p{=}10$) + 9 (IID) \\
\bottomrule
\end{tabular}
"""


def _share_cell(r: Dict[str, str], key: str) -> str:
    return (
        f"{_f(r[f'share_{key}'], '.3f')} "
        f"[{_f(r[f'share_{key}_ci_lo'], '.3f')}, {_f(r[f'share_{key}_ci_hi'], '.3f')}]"
    )


def tab2_variance() -> str:
    """Four rows: TL a01, TL a05, L3 p=10 primary, L3 p=6 sensitivity."""
    by_het = {r["het"]: r for r in _read("variance_components_by_het.csv") if r["model"] == "tl"}
    l3 = {r["p"]: r for r in _read("variance_components_l3_p10.csv") if r["model"] == "l3"}
    rows_spec: List[Tuple[str, str, Dict[str, str], int]] = [
        ("TinyLlama-1.1B", r"$\alpha{=}0.1$", by_het["a01"], 10),
        ("TinyLlama-1.1B", r"$\alpha{=}0.5$", by_het["a05"], 10),
        ("LLaMA-3.2-3B", r"$\alpha{=}0.1$, $p{=}10$", l3["10"], 10),
        ("LLaMA-3.2-3B", r"$\alpha{=}0.1$, $p{=}6$ sens.\ ", l3["6"], 6),
    ]
    lines = [
        r"\begin{tabular}{llrrrlllrrr}",
        r"\toprule",
        r"Model & Setting & $\hat\sigma^2_P$ & $\hat\sigma^2_{PM}$ & $\hat\sigma^2_E$ "
        r"& Share $P$ & Share $PM$ & Share $E$ & $p$ & $m$ & $r$ \\",
        r"\midrule",
    ]
    for model, setting, r, p in rows_spec:
        lines.append(
            f"{model} & {setting} & {sci_tex(r['s2_P'])} & {sci_tex(r['s2_PM'])} & "
            f"{sci_tex(r['s2_E'])} & {_share_cell(r, 'P')} & {_share_cell(r, 'PM')} & "
            f"{_share_cell(r, 'E')} & {p} & 3 & 2 \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        "",
        r"% Caption note: balanced two-way ANOVA with replication; $p$ partitions, "
        r"$m{=}3$ methods (fixed), $r{=}2$ run seeds. "
        r"Shares are point estimates with percentile bootstrap 95\% CIs over partitions "
        r"($B{=}2000$). "
        r"LLaMA $p{=}10$ is primary ($s2_P$ truncated at zero); $p{=}6$ is the "
        r"pre-registered sensitivity.",
    ]
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
            m = next(
                r
                for r in means
                if r["model"] == model and r["method"] == meth and r["het"] == "a01"
            )
            c = next(
                r
                for r in comm
                if r["model"] == model and r["method"] == meth and r["het"] == "a01"
            )
            act = [
                int(r["active_clients"])
                for r in parts
                if r["model"] == model and r.get("het", "a01") in ("a01", "")
            ]
            if not act:
                act = [int(r["active_clients"]) for r in parts if r["model"] == model]
            # Prefer active_min/max from comm when present
            if "active_min" in c and c["active_min"] != "":
                act_lo, act_hi = int(float(c["active_min"])), int(float(c["active_max"]))
            else:
                act_lo, act_hi = min(act), max(act)
            lines.append(
                f"{MODEL_TEX[model]}{' ($p{=}10$)' if model == 'l3' else ''} & "
                f"{METHOD_TEX[meth]} & "
                f"{_f(m['mean'], '.4f')} & {_f(m['sd'], '.4f')} & "
                f"{fmt_range(c['comm_mb_min'], c['comm_mb_max'], 1)} & "
                f"{fmt_int_range(act_lo, act_hi)} \\\\"
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
