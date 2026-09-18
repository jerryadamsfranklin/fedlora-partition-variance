#!/usr/bin/env python3
"""Phase I analysis I1-I6 from analysis/runs.csv (pre-registered ANALYSIS_PLAN.md)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.mixed_linear_model import MixedLM
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestIndPower, TTestPower

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.data.partition_stats import (  # noqa: E402
    discarded_trailing_samples,
    optimizer_steps_for_n,
)

# Model-specific DataLoader settings (from base configs / Phase C).
TRAIN_HPARAMS = {
    "tl": {"batch_size": 4, "grad_accum": 4, "local_epochs": 1},
    "l3": {"batch_size": 2, "grad_accum": 8, "local_epochs": 1},
}

# V6 payload bytes for communication fit check.
PAYLOAD_FULL = {"tl": 9_011_200, "l3": 9_175_040}
PAYLOAD_B_ONLY = {"tl": 3_244_032, "l3": 3_670_016}
N_ROUNDS = 15
MB = 1024 * 1024

METHODS = ["fedit", "ffa_lora", "flora"]
BOOT_B = 2000
BOOT_SEED = 12345
RANK_B = 10000
RANK_SEED = 12345
DELTAS = [0.005, 0.01, 0.02, 0.05]


def wilson_ci(successes: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return ((centre - margin) / denom, (centre + margin) / denom)


def gini(sizes: Sequence[float]) -> float:
    x = np.asarray([s for s in sizes if s > 0], dtype=float)
    if x.size == 0:
        return float("nan")
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum((np.arange(1, n + 1)) * x) / (n * np.sum(x))) - (n + 1) / n)


def mean_js_divergence(
    per_client_hists: Sequence[Dict[str, int]],
    global_hist: Dict[str, int],
    client_sizes: Sequence[int],
) -> float:
    """Mean JS divergence (natural log) of active clients vs global."""
    labels = sorted(global_hist.keys())
    g_tot = sum(global_hist.values())
    if g_tot <= 0 or not labels:
        return float("nan")
    g = np.array([global_hist.get(k, 0) / g_tot for k in labels], dtype=float)
    js_vals = []
    for hist, n in zip(per_client_hists, client_sizes):
        if n <= 0:
            continue
        p = np.array([hist.get(k, 0) / n for k in labels], dtype=float)
        m = 0.5 * (p + g)
        # JS = 0.5 KL(p||m) + 0.5 KL(g||m); use nat log; skip zeros safely
        def kl(a: np.ndarray, b: np.ndarray) -> float:
            mask = a > 0
            return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))

        js_vals.append(0.5 * kl(p, m) + 0.5 * kl(g, m))
    if not js_vals:
        return float("nan")
    return float(np.mean(js_vals))


def anova_components(y: np.ndarray, method: np.ndarray, partition: np.ndarray) -> Dict[str, Any]:
    """Two-way ANOVA with replication; method fixed, partition random."""
    methods = sorted(set(method.tolist()))
    partitions = sorted(set(partition.tolist()))
    m = len(methods)
    p = len(partitions)
    # r replications: assume balanced
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
    method_means = {meth: float(np.mean([cell_means[(meth, part)] for part in partitions])) for meth in methods}
    part_means = {part: float(np.mean([cell_means[(meth, part)] for meth in methods])) for part in partitions}

    ss_p = r * m * sum((part_means[part] - grand) ** 2 for part in partitions)
    ss_m = r * p * sum((method_means[meth] - grand) ** 2 for meth in methods)
    ss_pm = r * sum(
        (cell_means[(meth, part)] - method_means[meth] - part_means[part] + grand) ** 2
        for meth in methods
        for part in partitions
    )
    ss_e = (r - 1) * sum(cell_vars.values())  # since var is sample var; SS_E = sum (n-1)*s^2

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

    # Per-method one-way
    per_method = []
    for meth in methods:
        # partitions x r
        ys = []
        for part in partitions:
            mask = (method == meth) & (partition == part)
            ys.append(y[mask])
        ys_arr = np.stack(ys, axis=0)  # p x r
        part_m = ys_arr.mean(axis=1)
        grand_j = float(part_m.mean())
        msb = r * float(np.sum((part_m - grand_j) ** 2) / (p - 1))
        msw = float(np.mean([np.var(ys_arr[i], ddof=1) for i in range(p)]))
        s2_e_j = msw
        s2_p_j = max(0.0, (msb - msw) / r)
        per_method.append(
            {
                "method": meth,
                "s2_P_j": s2_p_j,
                "s2_E_j": s2_e_j,
                "MSB": msb,
                "MSW": msw,
            }
        )

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
        "per_method": per_method,
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
    records = {"s2_P": [], "s2_PM": [], "s2_E": [], "share_P": [], "share_PM": [], "share_E": []}
    for _ in range(B):
        draw = rng.choice(parts, size=p, replace=True)
        # rebuild y, method, partition for resampled partitions (with replacement labels)
        ys, ms, ps = [], [], []
        for new_idx, old_part in enumerate(draw):
            mask = partition == old_part
            ys.append(y[mask])
            ms.append(method[mask])
            ps.append(np.full(mask.sum(), new_idx))
        yb = np.concatenate(ys)
        mb = np.concatenate(ms)
        pb = np.concatenate(ps)
        try:
            est = anova_components(yb, mb, pb)
        except ValueError:
            continue
        for k in records:
            records[k].append(est[k] if not k.startswith("share") else est[k])
    out = {}
    for k, vals in records.items():
        arr = np.asarray(vals, dtype=float)
        out[k] = (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))
    return out


def mixedlm_crosscheck(df: pd.DataFrame) -> Dict[str, Any]:
    """Y ~ C(method) with VC for partition and partition:method."""
    d = df.copy()
    d["partition"] = d["data_seed"].astype(str)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            model = MixedLM.from_formula(
                "heldout_loss ~ C(method)",
                groups="partition",
                vc_formula={"method": "0 + C(method)"},
                data=d,
            )
            fit = model.fit(reml=True, method="lbfgs", maxiter=200)
        except Exception as e:
            return {
                "mixedlm_partition_var": float("nan"),
                "mixedlm_method_vc": float("nan"),
                "mixedlm_residual": float("nan"),
                "mixedlm_converged": False,
                "mixedlm_error": str(e),
            }
    re_var = float("nan")
    if fit.cov_re is not None:
        arr = np.asarray(fit.cov_re, dtype=float).reshape(-1)
        if arr.size:
            re_var = float(arr[0])
    scale = float(fit.scale)
    method_vc = float("nan")
    if getattr(fit, "vcomp", None) is not None:
        varr = np.asarray(fit.vcomp, dtype=float).reshape(-1)
        if varr.size:
            method_vc = float(varr[0])
    return {
        "mixedlm_partition_var": re_var,
        "mixedlm_method_vc": method_vc,
        "mixedlm_residual": scale,
        "mixedlm_converged": bool(getattr(fit, "converged", False)),
    }


METHOD_PAIRS = [("fedit", "ffa_lora"), ("fedit", "flora"), ("ffa_lora", "flora")]


def n_for_power(
    delta: float,
    sd: float,
    *,
    paired: bool,
) -> Any:
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


def ranking_stability(
    df_a01: pd.DataFrame,
    k_values: Sequence[int],
    B: int = RANK_B,
    seed: int = RANK_SEED,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    methods = METHODS
    # reference ranking by mean heldout over all a01
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

    # Single-draw sign flips over all raw (partition, run_seed) cells
    single_draw_flips: Dict[Tuple[str, str], Dict[str, int]] = {
        (a, b): {"flips": 0, "n": 0} for a, b in METHOD_PAIRS
    }
    run_seeds_all = sorted(df_a01["run_seed"].unique().tolist())
    for part in partitions:
        for rs in run_seeds_all:
            # only count cells that exist for all methods
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


def draws_needed(s2_p: float, s2_pm: float, s2_e: float) -> Tuple[List[Dict[str, Any]], float, float]:
    sd_pair = math.sqrt(2 * s2_pm + 2 * s2_e)
    sd_unpair = math.sqrt(s2_p + s2_pm + s2_e)
    rows = []
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


def empirical_sd_pair(df_a01: pd.DataFrame) -> List[Dict[str, Any]]:
    parts = sorted(df_a01["data_seed"].unique())
    out = []
    pairs = [("fedit", "ffa_lora"), ("fedit", "flora"), ("ffa_lora", "flora")]
    for a, b in pairs:
        diffs = []
        for part in parts:
            ma = df_a01[(df_a01.data_seed == part) & (df_a01.method == a)]["heldout_loss"].mean()
            mb = df_a01[(df_a01.data_seed == part) & (df_a01.method == b)]["heldout_loss"].mean()
            diffs.append(float(ma - mb))
        out.append(
            {
                "pair": f"{a}-{b}",
                "sd_pair_empirical": float(np.std(diffs, ddof=1)),
                "n_partitions": len(diffs),
            }
        )
    return out


def method_means_and_tests(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    mean_rows = []
    for het in ("a01", "iid"):
        sub = df[df.het == het]
        for meth in METHODS:
            vals = sub[sub.method == meth]["heldout_loss"].to_numpy()
            mean_rows.append(
                {
                    "het": het,
                    "method": meth,
                    "mean": float(np.mean(vals)),
                    "sd": float(np.std(vals, ddof=1)),
                    "n": int(vals.size),
                }
            )
    # paired t on partition-level means at a01
    a01 = df[df.het == "a01"]
    parts = sorted(a01["data_seed"].unique())
    part_means = {
        meth: np.array(
            [
                a01[(a01.data_seed == part) & (a01.method == meth)]["heldout_loss"].mean()
                for part in parts
            ]
        )
        for meth in METHODS
    }
    pairs = [("fedit", "ffa_lora"), ("fedit", "flora"), ("ffa_lora", "flora")]
    raw = []
    for a, b in pairs:
        d = part_means[a] - part_means[b]
        tres = stats.ttest_rel(part_means[a], part_means[b])
        n = len(d)
        se = float(np.std(d, ddof=1) / math.sqrt(n))
        mean_d = float(np.mean(d))
        tcrit = float(stats.t.ppf(0.975, df=n - 1))
        raw.append(
            {
                "pair": f"{a}-{b}",
                "mean_diff": mean_d,
                "ci_lo": mean_d - tcrit * se,
                "ci_hi": mean_d + tcrit * se,
                "raw_p": float(tres.pvalue),
            }
        )
    reject, holm_p, _, _ = multipletests([r["raw_p"] for r in raw], method="holm")
    for r, hp, rej in zip(raw, holm_p, reject):
        r["holm_p"] = float(hp)
        r["holm_reject_0.05"] = bool(rej)
    return mean_rows, raw


def partition_effects(model: str, df_a01: pd.DataFrame) -> List[Dict[str, Any]]:
    """One row per partition with stats + partition-mean loss."""
    hp = TRAIN_HPARAMS[model]
    rows = []
    parts = sorted(df_a01["data_seed"].unique())
    for part in parts:
        # any method's run_dir for this partition (same partition stats)
        sample = df_a01[df_a01.data_seed == part].iloc[0]
        run_dir = REPO_ROOT / sample["run_dir"]
        ps = json.loads((run_dir / "partition_stats.json").read_text(encoding="utf-8"))
        sizes = ps["client_sizes"]
        eff = sum(
            1
            for n in sizes
            if optimizer_steps_for_n(
                int(n),
                batch_size=hp["batch_size"],
                grad_accum=hp["grad_accum"],
                local_epochs=hp["local_epochs"],
            )
            > 0
        )
        discarded = sum(
            discarded_trailing_samples(
                int(n),
                batch_size=hp["batch_size"],
                grad_accum=hp["grad_accum"],
                local_epochs=hp["local_epochs"],
            )
            for n in sizes
        )
        loss_mean = float(df_a01[df_a01.data_seed == part]["heldout_loss"].mean())
        rows.append(
            {
                "data_seed": int(part),
                "active_clients": int(ps["active_clients"]),
                "effective_clients": int(eff),
                "discarded_trailing_samples": int(discarded),
                "gini_client_sizes": gini(sizes),
                "mean_js_divergence": mean_js_divergence(
                    ps["per_client_label_hist"], ps["global_label_hist"], sizes
                ),
                "partition_mean_heldout_loss": loss_mean,
            }
        )
    return rows


def spearman_rows(part_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    y = np.array([r["partition_mean_heldout_loss"] for r in part_rows], dtype=float)
    out = []
    for key in (
        "active_clients",
        "effective_clients",
        "discarded_trailing_samples",
        "gini_client_sizes",
        "mean_js_divergence",
    ):
        x = np.array([r[key] for r in part_rows], dtype=float)
        if np.nanstd(x) == 0 or np.nanstd(y) == 0:
            rho, p = float("nan"), float("nan")
        else:
            rho, p = stats.spearmanr(x, y)
            rho, p = float(rho), float(p)
        out.append({"statistic": key, "spearman_rho": rho, "spearman_p": p, "n": len(part_rows)})
    return out


def comm_fit(model: str, df_a01: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = []
    full = PAYLOAD_FULL[model]
    b_only = PAYLOAD_B_ONLY[model]
    for meth in METHODS:
        sub = df_a01[df_a01.method == meth]
        # one row per run; use active_clients and upload_mb_total
        x = sub["active_clients"].to_numpy(dtype=float)
        y = sub["comm_mb_total"].to_numpy(dtype=float)
        # expected total communication per V6:
        # upload cumulative after 15 rounds:
        # fedit/flora: 15 * active * full / MB
        # ffa: 1*active*full + 14*active*b_only, download similarly
        # communication_mb is upload+download cumulative
        if meth == "ffa_lora":
            # upload: full + 14*b_only; download: 15*b_only (B only each round)
            expected = x * (full + 14 * b_only + 15 * b_only) / MB
        else:
            # upload 15*full, download 15*full
            expected = x * (2 * 15 * full) / MB
        # linear fit y = a + b * active
        if len(np.unique(x)) >= 2:
            slope, intercept = np.polyfit(x, y, 1)
        else:
            slope, intercept = float("nan"), float(np.mean(y))
        max_abs_err = float(np.max(np.abs(y - expected)))
        rows.append(
            {
                "method": meth,
                "fit_intercept": float(intercept),
                "fit_slope_per_active": float(slope),
                "v6_expected_matches": max_abs_err < 1e-6,
                "max_abs_err_vs_v6": max_abs_err,
                "comm_mb_min": float(np.min(y)),
                "comm_mb_max": float(np.max(y)),
                "active_min": int(np.min(x)),
                "active_max": int(np.max(x)),
                "n": int(len(sub)),
            }
        )
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
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


def analyze_model(df_all: pd.DataFrame, model: str, out_dir: Path) -> Dict[str, Any]:
    df = df_all[df_all.model == model].copy()
    a01 = df[df.het == "a01"].copy()
    iid = df[df.het == "iid"].copy()

    y = a01["heldout_loss"].to_numpy(dtype=float)
    method = a01["method"].to_numpy()
    partition = a01["data_seed"].to_numpy()

    est = anova_components(y, method, partition)
    cis = bootstrap_components(y, method, partition)
    mixed = mixedlm_crosscheck(a01)

    vc_row = {
        "model": model,
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
        "MS_P": est["MS_P"],
        "MS_PM": est["MS_PM"],
        "MS_E": est["MS_E"],
        **mixed,
    }
    for pm in est["per_method"]:
        vc_row[f"s2_P_{pm['method']}"] = pm["s2_P_j"]
        vc_row[f"s2_E_{pm['method']}"] = pm["s2_E_j"]

    # I2 IID noise
    iid_vars = []
    for meth in METHODS:
        vals = iid[iid.method == meth]["heldout_loss"].to_numpy(dtype=float)
        iid_vars.append(float(np.var(vals, ddof=1)))
    # pooled: average of method variances (equal n per method within model)
    pooled = float(np.mean(iid_vars))
    iid_row = {
        "model": model,
        "pooled_iid_var": pooled,
        "s2_E_a01": est["s2_E"],
        "ratio_s2E_a01_over_iid": est["s2_E"] / pooled if pooled > 0 else float("nan"),
    }
    for meth, v in zip(METHODS, iid_vars):
        iid_row[f"iid_var_{meth}"] = v

    # I3
    k_values = [1, 2, 3, 5] if model == "tl" else [1, 2, 3]
    rank_rows, pair_rows = ranking_stability(a01, k_values)
    for r in rank_rows:
        r["model"] = model
    for r in pair_rows:
        r["model"] = model

    # I4
    power_rows, sd_pair, sd_unpair = draws_needed(est["s2_P"], est["s2_PM"], est["s2_E"])
    power_rows.extend(observed_gap_power(a01, sd_pair, sd_unpair))
    emp = empirical_sd_pair(a01)
    for r in power_rows:
        r["model"] = model
        r["sd_pair_empirical_mean"] = float(np.mean([e["sd_pair_empirical"] for e in emp]))
    for e in emp:
        e["model"] = model
        e["sd_pair_model"] = sd_pair

    # I5
    means, tests = method_means_and_tests(df)
    for r in means:
        r["model"] = model
    for r in tests:
        r["model"] = model

    # I6
    part_rows = partition_effects(model, a01)
    for r in part_rows:
        r["model"] = model
    spear = spearman_rows(part_rows)
    for r in spear:
        r["model"] = model
    comm = comm_fit(model, a01)
    for r in comm:
        r["model"] = model

    return {
        "vc": vc_row,
        "iid": iid_row,
        "rank": rank_rows,
        "pair_rank": pair_rows,
        "power": power_rows,
        "emp_sd": emp,
        "means": means,
        "tests": tests,
        "partition": part_rows,
        "spearman": spear,
        "comm": comm,
        "est": est,
        "rank_k3_paired_best": next(
            r["prob"]
            for r in rank_rows
            if r["k"] == 3 and r["protocol"] == "paired" and r["event"] == "best"
        ),
    }


def select_i7(results: Dict[str, Dict[str, Any]]) -> List[str]:
    """Return which I7 claim rows apply (may be multiple)."""
    claims = []
    for model, res in results.items():
        share_p = res["vc"]["share_P"]
        flip3 = res["rank_k3_paired_best"]
        if share_p >= 0.30 or flip3 >= 0.20:
            claims.append(
                f"{model}: row1 (partition share>={share_p:.3f} or 3-draw paired flip>={flip3:.3f})"
            )
        elif share_p < 0.10 and flip3 < 0.05:
            claims.append(
                f"{model}: row2 (partition share<{share_p:.3f} and flip<{flip3:.3f})"
            )
        else:
            claims.append(
                f"{model}: row3 in-between (share={share_p:.3f}, flip3_paired_best={flip3:.3f})"
            )
        if res["est"]["s2_PM"] > res["est"]["s2_P"] and res["est"]["s2_PM"] > 0:
            claims.append(f"{model}: row4 interaction s2_PM large relative to s2_P")

    # cross-scale CI overlap on share_P
    if "tl" in results and "l3" in results:
        tl = results["tl"]["vc"]
        l3 = results["l3"]["vc"]
        # non-overlapping CIs?
        lo1, hi1 = tl["share_P_ci_lo"], tl["share_P_ci_hi"]
        lo2, hi2 = l3["share_P_ci_lo"], l3["share_P_ci_hi"]
        overlap = not (hi1 < lo2 or hi2 < lo1)
        # direction differ: point estimates on opposite sides meaningfully
        if not overlap:
            claims.append("cross-scale: row5 TinyLlama and LLaMA shares differ (non-overlapping CIs)")
        else:
            claims.append("cross-scale: row6 overlapping CIs across scales")
    return claims


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default="analysis/runs.csv")
    parser.add_argument("--out-dir", default="analysis")
    args = parser.parse_args()
    runs_path = Path(args.runs)
    if not runs_path.is_absolute():
        runs_path = REPO_ROOT / runs_path
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir

    df = pd.read_csv(runs_path)
    results = {}
    vc_rows, iid_rows, rank_rows, pair_rows, power_rows = [], [], [], [], []
    emp_rows, mean_rows, test_rows = [], [], []
    part_rows, spear_rows, comm_rows = [], [], []

    for model in ("tl", "l3"):
        print(f"=== analyzing {model} ===", flush=True)
        res = analyze_model(df, model, out_dir)
        print(f"  done {model}: s2_P={res['est']['s2_P']:.6g} share_P={res['vc']['share_P']:.4f}", flush=True)
        results[model] = res
        vc_rows.append(res["vc"])
        iid_rows.append(res["iid"])
        rank_rows.extend(res["rank"])
        pair_rows.extend(res["pair_rank"])
        power_rows.extend(res["power"])
        emp_rows.extend(res["emp_sd"])
        mean_rows.extend(res["means"])
        test_rows.extend(res["tests"])
        part_rows.extend(res["partition"])
        spear_rows.extend(res["spearman"])
        comm_rows.extend(res["comm"])

    write_csv(out_dir / "variance_components.csv", vc_rows)
    write_csv(out_dir / "iid_noise.csv", iid_rows)
    write_csv(out_dir / "rank_flip.csv", rank_rows)
    write_csv(out_dir / "rank_flip_pairs.csv", pair_rows)
    write_csv(out_dir / "power.csv", power_rows)
    write_csv(out_dir / "sd_pair_empirical.csv", emp_rows)
    write_csv(out_dir / "method_means.csv", mean_rows)
    write_csv(out_dir / "method_pairwise.csv", test_rows)
    write_csv(out_dir / "partition_effects.csv", part_rows)
    write_csv(out_dir / "partition_spearman.csv", spear_rows)
    write_csv(out_dir / "comm.csv", comm_rows)

    claims = select_i7(results)
    (out_dir / "i7_selected_claims.txt").write_text(
        "\n".join(claims) + "\n", encoding="utf-8"
    )
    print("I7 selected:")
    for c in claims:
        print(" ", c)


if __name__ == "__main__":
    main()
