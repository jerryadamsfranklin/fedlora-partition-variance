#!/usr/bin/env python3
"""I8–I10 analysis extensions on analysis/runs.csv (prod_v1 + prod_v2).

Self-contained (does not import analyze_variance.py — MixedLM import can hang on
some macOS Python builds). Reimplements the same moment estimators / cluster
bootstrap as I1 (B=2000, seed=12345).
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOT_B = 2000
BOOT_SEED = 12345
METHODS = ("fedit", "ffa_lora", "flora")


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def anova_components(
    y: np.ndarray, method: np.ndarray, partition: np.ndarray
) -> Dict[str, Any]:
    methods = sorted(set(method.tolist()), key=lambda m: METHODS.index(m) if m in METHODS else m)
    partitions = sorted(set(partition.tolist()))
    m = len(methods)
    p = len(partitions)
    cell_means = {}
    cell_vars = {}
    r = None
    for meth in methods:
        for part in partitions:
            mask = (method == meth) & (partition == part)
            vals = y[mask]
            if r is None:
                r = int(vals.size)
            elif int(vals.size) != r:
                raise ValueError(f"unbalanced cell method={meth} part={part}: {vals.size} vs {r}")
            cell_means[(meth, part)] = float(np.mean(vals))
            cell_vars[(meth, part)] = float(np.var(vals, ddof=1)) if r > 1 else 0.0
    assert r is not None
    grand = float(np.mean(y))
    method_means = {
        meth: float(np.mean([cell_means[(meth, part)] for part in partitions]))
        for meth in methods
    }
    part_means = {
        part: float(np.mean([cell_means[(meth, part)] for meth in methods]))
        for part in partitions
    }
    ss_p = r * m * sum((part_means[part] - grand) ** 2 for part in partitions)
    ss_pm = r * sum(
        (cell_means[(meth, part)] - method_means[meth] - part_means[part] + grand) ** 2
        for meth in methods
        for part in partitions
    )
    ss_e = (r - 1) * sum(cell_vars.values())
    df_p = p - 1
    df_pm = (m - 1) * (p - 1)
    df_e = m * p * (r - 1)
    ms_p = ss_p / df_p
    ms_pm = ss_pm / df_pm
    ms_e = ss_e / df_e
    s2_e = ms_e
    s2_pm_raw = (ms_pm - ms_e) / r
    s2_p_raw = (ms_p - ms_pm) / (m * r)
    trunc_pm = s2_pm_raw < 0
    trunc_p = s2_p_raw < 0
    s2_pm = max(0.0, s2_pm_raw)
    s2_p = max(0.0, s2_p_raw)
    total = s2_p + s2_pm + s2_e
    return {
        "m": m,
        "p": p,
        "r": r,
        "MS_P": ms_p,
        "MS_PM": ms_pm,
        "MS_E": ms_e,
        "s2_P": s2_p,
        "s2_PM": s2_pm,
        "s2_E": s2_e,
        "share_P": s2_p / total if total > 0 else float("nan"),
        "share_PM": s2_pm / total if total > 0 else float("nan"),
        "share_E": s2_e / total if total > 0 else float("nan"),
        "trunc_P": trunc_p,
        "trunc_PM": trunc_pm,
    }


def bootstrap_components(
    y: np.ndarray,
    method: np.ndarray,
    partition: np.ndarray,
    B: int = BOOT_B,
    seed: int = BOOT_SEED,
) -> Dict[str, Tuple[float, float]]:
    rng = np.random.default_rng(seed)
    parts = np.array(sorted(set(partition.tolist())))
    p = len(parts)
    records = {k: [] for k in ("s2_P", "s2_PM", "s2_E", "share_P", "share_PM", "share_E")}
    for _ in range(B):
        draw = rng.choice(parts, size=p, replace=True)
        ys, ms, ps = [], [], []
        for new_idx, old_part in enumerate(draw):
            mask = partition == old_part
            ys.append(y[mask])
            ms.append(method[mask])
            ps.append(np.full(mask.sum(), new_idx))
        try:
            est = anova_components(np.concatenate(ys), np.concatenate(ms), np.concatenate(ps))
        except ValueError:
            continue
        for k in records:
            records[k].append(est[k])
    out = {}
    for k, vals in records.items():
        arr = np.asarray(vals, dtype=float)
        out[k] = (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))
    return out


def _vc_row(model: str, het: str, label: str, df: pd.DataFrame) -> Dict[str, Any]:
    y = df["heldout_loss"].to_numpy(dtype=float)
    method = df["method"].to_numpy()
    partition = df["data_seed"].to_numpy()
    est = anova_components(y, method, partition)
    cis = bootstrap_components(y, method, partition)
    return {
        "model": model,
        "het": het,
        "label": label,
        "p": est["p"],
        "r": est["r"],
        "m": est["m"],
        "s2_P": est["s2_P"],
        "s2_PM": est["s2_PM"],
        "s2_E": est["s2_E"],
        "share_P": est["share_P"],
        "share_PM": est["share_PM"],
        "share_E": est["share_E"],
        "s2_P_ci_lo": cis["s2_P"][0],
        "s2_P_ci_hi": cis["s2_P"][1],
        "s2_PM_ci_lo": cis["s2_PM"][0],
        "s2_PM_ci_hi": cis["s2_PM"][1],
        "s2_E_ci_lo": cis["s2_E"][0],
        "s2_E_ci_hi": cis["s2_E"][1],
        "share_P_ci_lo": cis["share_P"][0],
        "share_P_ci_hi": cis["share_P"][1],
        "share_PM_ci_lo": cis["share_PM"][0],
        "share_PM_ci_hi": cis["share_PM"][1],
        "share_E_ci_lo": cis["share_E"][0],
        "share_E_ci_hi": cis["share_E"][1],
        "trunc_P": est["trunc_P"],
        "trunc_PM": est["trunc_PM"],
    }


def bootstrap_share_diff(
    df_a: pd.DataFrame, df_b: pd.DataFrame, B: int = BOOT_B, seed: int = BOOT_SEED
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    parts_a = np.array(sorted(df_a["data_seed"].unique()))
    parts_b = np.array(sorted(df_b["data_seed"].unique()))
    keys = ["share_P", "share_PM", "share_E"]
    ea = anova_components(
        df_a["heldout_loss"].to_numpy(float), df_a["method"].to_numpy(), df_a["data_seed"].to_numpy()
    )
    eb = anova_components(
        df_b["heldout_loss"].to_numpy(float), df_b["method"].to_numpy(), df_b["data_seed"].to_numpy()
    )
    point = {k: eb[k] - ea[k] for k in keys}
    records = {k: [] for k in keys}

    def rebuild(df: pd.DataFrame, draw: np.ndarray) -> pd.DataFrame:
        chunks = []
        for new_idx, old in enumerate(draw):
            sub = df[df.data_seed == old].copy()
            sub["data_seed"] = new_idx
            chunks.append(sub)
        return pd.concat(chunks, ignore_index=True)

    for _ in range(B):
        try:
            sa = rebuild(df_a, rng.choice(parts_a, size=len(parts_a), replace=True))
            sb = rebuild(df_b, rng.choice(parts_b, size=len(parts_b), replace=True))
            ea_b = anova_components(
                sa["heldout_loss"].to_numpy(float), sa["method"].to_numpy(), sa["data_seed"].to_numpy()
            )
            eb_b = anova_components(
                sb["heldout_loss"].to_numpy(float), sb["method"].to_numpy(), sb["data_seed"].to_numpy()
            )
        except ValueError:
            continue
        for k in keys:
            records[k].append(eb_b[k] - ea_b[k])

    out: Dict[str, Any] = {}
    for k in keys:
        arr = np.asarray(records[k], dtype=float)
        out[f"delta_{k}"] = point[k]
        out[f"delta_{k}_ci_lo"] = float(np.quantile(arr, 0.025)) if len(arr) else float("nan")
        out[f"delta_{k}_ci_hi"] = float(np.quantile(arr, 0.975)) if len(arr) else float("nan")
        out[f"delta_{k}_excludes_0"] = bool(
            out[f"delta_{k}_ci_lo"] > 0 or out[f"delta_{k}_ci_hi"] < 0
        )
    return out


def ranking_stability(df_a01: pd.DataFrame, k_values: Sequence[int]):
    """Paired/unpaired flip probs (I3) — same construction as analyze_variance."""
    means = df_a01.groupby("method")["heldout_loss"].mean()
    ref_order = list(means.sort_values().index)
    partitions = sorted(df_a01["data_seed"].unique().tolist())
    run_seeds_all = sorted(df_a01["run_seed"].unique().tolist())
    # cell lookup
    cell = {
        (int(r.data_seed), r.method, int(r.run_seed)): float(r.heldout_loss)
        for r in df_a01.itertuples()
    }
    rng = np.random.default_rng(BOOT_SEED)
    rank_rows = []
    pair_rows = []
    for k in k_values:
        # paired
        flips_p = 0
        n_p = 0
        for _ in range(BOOT_B):
            parts = rng.choice(partitions, size=k, replace=False) if k <= len(partitions) else rng.choice(partitions, size=k, replace=True)
            scores = {}
            for meth in METHODS:
                vals = []
                for part in parts:
                    rs = rng.choice(run_seeds_all)
                    vals.append(cell[(int(part), meth, int(rs))])
                scores[meth] = float(np.mean(vals))
            order = sorted(scores, key=scores.get)
            n_p += 1
            if order != ref_order:
                flips_p += 1
        # unpaired
        flips_u = 0
        n_u = 0
        for _ in range(BOOT_B):
            scores = {}
            for meth in METHODS:
                parts = rng.choice(partitions, size=k, replace=False) if k <= len(partitions) else rng.choice(partitions, size=k, replace=True)
                vals = []
                for part in parts:
                    rs = rng.choice(run_seeds_all)
                    vals.append(cell[(int(part), meth, int(rs))])
                scores[meth] = float(np.mean(vals))
            order = sorted(scores, key=scores.get)
            n_u += 1
            if order != ref_order:
                flips_u += 1
        for protocol, flips, n in (("paired", flips_p, n_p), ("unpaired", flips_u, n_u)):
            phat = flips / n if n else float("nan")
            # Wilson CI
            z = 1.959963984540054
            denom = 1 + z**2 / n
            center = (phat + z**2 / (2 * n)) / denom
            half = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
            rank_rows.append(
                {
                    "k": k,
                    "protocol": protocol,
                    "event": "best",
                    "p_hat": phat,
                    "ci_lo": max(0.0, center - half),
                    "ci_hi": min(1.0, center + half),
                    "n": n,
                }
            )
    return rank_rows, pair_rows


def draws_needed(s2_p: float, s2_pm: float, s2_e: float):
    """I4 power curve at selected deltas — simplified mirror of analyze_variance."""
    rows = []
    sd_pair = math.sqrt(2 * (s2_pm + s2_e / 2))  # r=2 cell means
    sd_unpair = math.sqrt(2 * (s2_p + s2_pm + s2_e / 2))
    for kind, sd in (("paired", sd_pair), ("unpaired", sd_unpair)):
        for delta in (0.01, 0.005, 0.002, 0.001):
            # n for two-sided alpha=0.05 power=0.8 approx
            z_a = 1.959963984540054
            z_b = 0.8416212335729143
            n = math.ceil(((z_a + z_b) * sd / delta) ** 2)
            rows.append({"kind": kind, "delta": delta, "n_draws": n, "sd": sd})
    return rows, sd_pair, sd_unpair


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default="analysis/runs.csv")
    parser.add_argument("--out-dir", default="analysis")
    args = parser.parse_args()
    runs = Path(args.runs)
    if not runs.is_absolute():
        runs = REPO_ROOT / runs
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir

    df = pd.read_csv(runs)
    print(f"runs.csv rows={len(df)}", flush=True)

    tl_a05 = df[(df.model == "tl") & (df.het == "a05")].copy()
    tl_a01 = df[(df.model == "tl") & (df.het == "a01")].copy()
    print("I8 computing tl a05…", flush=True)
    vc_a05 = _vc_row("tl", "a05", "I8_tl_a05", tl_a05)
    print("I8 computing tl a01 ref…", flush=True)
    vc_a01_ref = _vc_row("tl", "a01", "I8_tl_a01_ref", tl_a01)
    write_csv(out_dir / "variance_components_a05.csv", [vc_a05])
    write_csv(out_dir / "variance_components_by_het.csv", [vc_a01_ref, vc_a05])
    print(
        f"I8 tl a05: share_P={vc_a05['share_P']:.4f} "
        f"CI=[{vc_a05['share_P_ci_lo']:.4f},{vc_a05['share_P_ci_hi']:.4f}] p={vc_a05['p']}",
        flush=True,
    )

    print("I9 gradient bootstrap…", flush=True)
    grad = bootstrap_share_diff(tl_a01, tl_a05)
    write_csv(out_dir / "het_gradient.csv", [{"model": "tl", "compare": "a05_minus_a01", **grad}])
    for k in ("share_P", "share_PM", "share_E"):
        print(
            f"  delta_{k}={grad[f'delta_{k}']:.4f} "
            f"CI=[{grad[f'delta_{k}_ci_lo']:.4f},{grad[f'delta_{k}_ci_hi']:.4f}] "
            f"excludes0={grad[f'delta_{k}_excludes_0']}",
            flush=True,
        )

    l3_a01 = df[(df.model == "l3") & (df.het == "a01")].copy()
    l3_p10 = l3_a01
    l3_p6 = l3_a01[l3_a01.data_seed.isin(range(2001, 2007))].copy()
    print("I10 l3 p=10…", flush=True)
    vc_p10 = _vc_row("l3", "a01", "I10_l3_p10", l3_p10)
    print("I10 l3 p=6 sensitivity…", flush=True)
    vc_p6 = _vc_row("l3", "a01", "I10_l3_p6_sensitivity", l3_p6)
    write_csv(out_dir / "variance_components_l3_p10.csv", [vc_p10, vc_p6])
    print(
        f"I10 p10 share_P={vc_p10['share_P']:.4f} "
        f"CI=[{vc_p10['share_P_ci_lo']:.4f},{vc_p10['share_P_ci_hi']:.4f}] "
        f"includes0={vc_p10['share_P_ci_lo'] <= 0 <= vc_p10['share_P_ci_hi']}",
        flush=True,
    )

    rank_rows, pair_rows = ranking_stability(l3_p10, [1, 2, 3])
    for r in rank_rows:
        r["model"] = "l3"
        r["label"] = "I10_p10"
    power_rows, sd_pair, sd_unpair = draws_needed(vc_p10["s2_P"], vc_p10["s2_PM"], vc_p10["s2_E"])
    for r in power_rows:
        r["model"] = "l3"
        r["label"] = "I10_p10"
    write_csv(out_dir / "rank_flip_l3_p10.csv", rank_rows)
    write_csv(out_dir / "rank_flip_pairs_l3_p10.csv", pair_rows)
    write_csv(out_dir / "power_l3_p10.csv", power_rows)

    claims: List[str] = []
    if any(grad[f"delta_{k}_excludes_0"] for k in ("share_P", "share_PM", "share_E")):
        claims.append(
            "I8/I9: Gradient present — at least one share difference CI excludes zero; "
            "report both alphas and the gradient."
        )
    else:
        claims.append(
            "I8/I9: Gradient absent — all three difference CIs include zero; "
            "alpha 0.1 findings generalize over this range."
        )
    if vc_p10["share_P_ci_lo"] > 0 or vc_p10["share_P_ci_hi"] < 0:
        claims.append(
            "I10: At p=10, LLaMA partition-share CI excludes zero; "
            "update claims; keep p=6 as sensitivity."
        )
    else:
        claims.append(
            "I10: At p=10, LLaMA partition-share CI still includes zero; "
            "keep interaction-dominated 3B story; p=6 remains sensitivity."
        )
    (out_dir / "i8_i10_selected_claims.txt").write_text("\n".join(claims) + "\n", encoding="utf-8")
    print("Selected outcome rows:", flush=True)
    for c in claims:
        print(" ", c, flush=True)


if __name__ == "__main__":
    main()
