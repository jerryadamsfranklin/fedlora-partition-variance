#!/usr/bin/env python3
"""I8–I10 analysis extensions on analysis/runs.csv (prod_v1 + prod_v2).

Self-contained (does not import analyze_variance.py — MixedLM import can hang on
some macOS Python builds). Reimplements the same moment estimators / cluster
bootstrap as I1 (B=2000, seed=12345). Ranking flips use B=10000 (pre-registered).
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
from statsmodels.stats.power import TTestIndPower, TTestPower

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOT_B = 2000
BOOT_SEED = 12345
RANK_B = 10000
RANK_SEED = 12345
DELTAS = [0.005, 0.01, 0.02, 0.05]
METHODS = ("fedit", "ffa_lora", "flora")
METHOD_PAIRS = [("fedit", "ffa_lora"), ("fedit", "flora"), ("ffa_lora", "flora")]


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


def wilson_ci(successes: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    phat = successes / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


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


def ranking_stability(
    df_a01: pd.DataFrame,
    k_values: Sequence[int],
    B: int = RANK_B,
    seed: int = RANK_SEED,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Paired/unpaired flip probs (I3) — same construction as analyze_variance."""
    methods = list(METHODS)
    means = df_a01.groupby("method")["heldout_loss"].mean()
    ref_order = tuple(sorted(methods, key=lambda m: float(means[m])))
    ref_best = ref_order[0]
    ref_gaps = {(a, b): float(means[a] - means[b]) for a, b in METHOD_PAIRS}

    partitions = sorted(df_a01["data_seed"].unique().tolist())
    seeds_by = {}
    for part in partitions:
        for meth in methods:
            seeds_by[(part, meth)] = sorted(
                df_a01[(df_a01.data_seed == part) & (df_a01.method == meth)]["run_seed"]
                .unique()
                .tolist()
            )

    loss_lookup = {
        (int(r.data_seed), r.method, int(r.run_seed)): float(r.heldout_loss)
        for r in df_a01.itertuples()
    }

    single_draw_flips: Dict[Tuple[str, str], Dict[str, int]] = {
        (a, b): {"flips": 0, "n": 0} for a, b in METHOD_PAIRS
    }
    run_seeds_all = sorted(df_a01["run_seed"].unique().tolist())
    for part in partitions:
        for rs in run_seeds_all:
            if not all((int(part), meth, int(rs)) in loss_lookup for meth in methods):
                continue
            for a, b in METHOD_PAIRS:
                gap = loss_lookup[(int(part), a, int(rs))] - loss_lookup[(int(part), b, int(rs))]
                ref = ref_gaps[(a, b)]
                single_draw_flips[(a, b)]["n"] += 1
                if np.sign(gap) != np.sign(ref) and abs(ref) > 0:
                    single_draw_flips[(a, b)]["flips"] += 1

    agg_rows: List[Dict[str, Any]] = []
    pair_rows: List[Dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    for k in k_values:
        for protocol in ("paired", "unpaired"):
            best_flip = 0
            order_flip = 0
            pair_flip_counts = {(a, b): 0 for a, b in METHOD_PAIRS}
            for _ in range(B):
                method_means: Dict[str, float] = {}
                if protocol == "paired":
                    chosen_parts = rng.choice(partitions, size=k, replace=False)
                    pairs = []
                    for part in chosen_parts:
                        seeds = seeds_by[(part, methods[0])]
                        rs = int(rng.choice(seeds))
                        pairs.append((int(part), rs))
                    for meth in methods:
                        vals = [loss_lookup[(part, meth, rs)] for part, rs in pairs]
                        method_means[meth] = float(np.mean(vals))
                else:
                    for meth in methods:
                        chosen_parts = rng.choice(partitions, size=k, replace=False)
                        vals = []
                        for part in chosen_parts:
                            seeds = seeds_by[(int(part), meth)]
                            rs = int(rng.choice(seeds))
                            vals.append(loss_lookup[(int(part), meth, rs)])
                        method_means[meth] = float(np.mean(vals))
                order = tuple(sorted(methods, key=lambda m: method_means[m]))
                if order[0] != ref_best:
                    best_flip += 1
                if order != ref_order:
                    order_flip += 1
                for a, b in METHOD_PAIRS:
                    gap = method_means[a] - method_means[b]
                    ref = ref_gaps[(a, b)]
                    if np.sign(gap) != np.sign(ref) and abs(ref) > 0:
                        pair_flip_counts[(a, b)] += 1
            for name, count in (("best", best_flip), ("full_order", order_flip)):
                lo, hi = wilson_ci(count, B)
                agg_rows.append(
                    {
                        "k": k,
                        "protocol": protocol,
                        "event": name,
                        "prob": count / B,
                        "wilson_lo": lo,
                        "wilson_hi": hi,
                        "ref_order": ">".join(ref_order),
                        "B": B,
                    }
                )
            for a, b in METHOD_PAIRS:
                count = pair_flip_counts[(a, b)]
                lo, hi = wilson_ci(count, B)
                sd = single_draw_flips[(a, b)]
                pair_rows.append(
                    {
                        "k": k,
                        "protocol": protocol,
                        "pair": f"{a}-{b}",
                        "true_gap": ref_gaps[(a, b)],
                        "prob_order_flip": count / B,
                        "wilson_lo": lo,
                        "wilson_hi": hi,
                        "single_draw_sign_flips": sd["flips"],
                        "single_draw_n": sd["n"],
                        "B": B,
                        "ref_order": ">".join(ref_order),
                    }
                )
    return agg_rows, pair_rows


def n_for_power(delta: float, sd: float, *, paired: bool) -> Any:
    if sd <= 0 or not math.isfinite(sd):
        return "more than 1000"
    es = abs(delta) / sd
    if es <= 0:
        return "more than 1000"
    power_fn = TTestPower() if paired else TTestIndPower()
    for cand in range(2, 1001):
        if paired:
            pow_ = power_fn.power(
                effect_size=es, nobs=cand, alpha=0.05, alternative="two-sided"
            )
        else:
            pow_ = power_fn.power(
                effect_size=es,
                nobs1=cand,
                alpha=0.05,
                ratio=1.0,
                alternative="two-sided",
            )
        if pow_ >= 0.8:
            return cand
    return "more than 1000"


def draws_needed(s2_p: float, s2_pm: float, s2_e: float) -> Tuple[List[Dict[str, Any]], float, float]:
    """Pre-registered power curve: deltas 0.005/0.01/0.02/0.05; distinct paired/unpaired SDs."""
    sd_pair = math.sqrt(2 * s2_pm + 2 * s2_e)
    sd_unpair = math.sqrt(s2_p + s2_pm + s2_e)
    rows: List[Dict[str, Any]] = []
    for delta in DELTAS:
        rows.append(
            {
                "kind": "preregistered_delta",
                "pair": "",
                "delta": delta,
                "n_paired": n_for_power(delta, sd_pair, paired=True),
                "n_unpaired_per_method": n_for_power(delta, sd_unpair, paired=False),
                "sd_pair_model": sd_pair,
                "sd_unpair_model": sd_unpair,
            }
        )
    return rows, sd_pair, sd_unpair


def observed_gap_power(
    df_a01: pd.DataFrame, sd_pair: float, sd_unpair: float
) -> List[Dict[str, Any]]:
    means = df_a01.groupby("method")["heldout_loss"].mean()
    rows = []
    for a, b in METHOD_PAIRS:
        gap = float(means[a] - means[b])
        rows.append(
            {
                "kind": "observed_gap",
                "pair": f"{a}-{b}",
                "delta": gap,
                "n_paired": n_for_power(gap, sd_pair, paired=True),
                "n_unpaired_per_method": n_for_power(gap, sd_unpair, paired=False),
                "sd_pair_model": sd_pair,
                "sd_unpair_model": sd_unpair,
            }
        )
    return rows


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

    # N7-8 post hoc: absolute variance components side by side (not pre-registered).
    abs_rows = [
        {
            "label": "post_hoc_absolute_variance_not_preregistered",
            "model": "tl",
            "het": "a01",
            "alpha": 0.1,
            "s2_P": vc_a01_ref["s2_P"],
            "s2_PM": vc_a01_ref["s2_PM"],
            "s2_E": vc_a01_ref["s2_E"],
            "sd_pair": math.sqrt(2 * vc_a01_ref["s2_PM"] + 2 * vc_a01_ref["s2_E"]),
        },
        {
            "label": "post_hoc_absolute_variance_not_preregistered",
            "model": "tl",
            "het": "a05",
            "alpha": 0.5,
            "s2_P": vc_a05["s2_P"],
            "s2_PM": vc_a05["s2_PM"],
            "s2_E": vc_a05["s2_E"],
            "sd_pair": math.sqrt(2 * vc_a05["s2_PM"] + 2 * vc_a05["s2_E"]),
        },
    ]
    ratio_row = {
        "label": "post_hoc_absolute_variance_ratio_a01_over_a05_not_preregistered",
        "model": "tl",
        "het": "a01_over_a05",
        "alpha": "",
        "s2_P": vc_a01_ref["s2_P"] / vc_a05["s2_P"] if vc_a05["s2_P"] > 0 else float("nan"),
        "s2_PM": vc_a01_ref["s2_PM"] / vc_a05["s2_PM"] if vc_a05["s2_PM"] > 0 else float("nan"),
        "s2_E": vc_a01_ref["s2_E"] / vc_a05["s2_E"] if vc_a05["s2_E"] > 0 else float("nan"),
        "sd_pair": abs_rows[0]["sd_pair"] / abs_rows[1]["sd_pair"]
        if abs_rows[1]["sd_pair"] > 0
        else float("nan"),
    }
    write_csv(out_dir / "absolute_variance_alpha_posthoc.csv", abs_rows + [ratio_row])
    print(
        f"N7-8 post hoc |s2_P a01/a05|={ratio_row['s2_P']:.2f} "
        f"sd_pair a01={abs_rows[0]['sd_pair']:.5f} a05={abs_rows[1]['sd_pair']:.5f}",
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
        f"includes0={vc_p10['share_P_ci_lo'] <= 0 <= vc_p10['share_P_ci_hi']} "
        f"trunc_P={vc_p10['trunc_P']}",
        flush=True,
    )
    (out_dir / "l3_p10_truncation_flag.txt").write_text(
        f"I10 l3 p=10: trunc_P={vc_p10['trunc_P']} trunc_PM={vc_p10['trunc_PM']}\n"
        f"s2_P={vc_p10['s2_P']:.6e} (truncated at zero={vc_p10['trunc_P']})\n"
        f"s2_PM={vc_p10['s2_PM']:.6e} s2_E={vc_p10['s2_E']:.6e}\n"
        f"share_P={vc_p10['share_P']:.6f} CI=[{vc_p10['share_P_ci_lo']:.6f},{vc_p10['share_P_ci_hi']:.6f}]\n",
        encoding="utf-8",
    )

    print(f"I10 ranking stability B={RANK_B}…", flush=True)
    rank_rows, pair_rows = ranking_stability(l3_p10, [1, 2, 3])
    for r in rank_rows:
        r["model"] = "l3"
        r["label"] = "I10_p10"
    for r in pair_rows:
        r["model"] = "l3"
        r["label"] = "I10_p10"
    power_rows, sd_pair, sd_unpair = draws_needed(vc_p10["s2_P"], vc_p10["s2_PM"], vc_p10["s2_E"])
    power_rows.extend(observed_gap_power(l3_p10, sd_pair, sd_unpair))
    for r in power_rows:
        r["model"] = "l3"
        r["label"] = "I10_p10"
    write_csv(out_dir / "rank_flip_l3_p10.csv", rank_rows)
    write_csv(out_dir / "rank_flip_pairs_l3_p10.csv", pair_rows)
    write_csv(out_dir / "power_l3_p10.csv", power_rows)
    print(
        f"power sd_pair={sd_pair:.5f} sd_unpair={sd_unpair:.5f}; "
        f"observed_gap rows={sum(1 for r in power_rows if r['kind']=='observed_gap')}",
        flush=True,
    )

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
    if vc_p10["trunc_P"]:
        claims.append(
            "I10 note: s2_P truncated at zero at p=10 (MS_P < MS_PM); "
            "report trunc_P=True alongside the share CI."
        )
    (out_dir / "i8_i10_selected_claims.txt").write_text("\n".join(claims) + "\n", encoding="utf-8")
    print("Selected outcome rows:", flush=True)
    for c in claims:
        print(" ", c, flush=True)


if __name__ == "__main__":
    main()
