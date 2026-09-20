#!/usr/bin/env python3
"""O12-2: compare regenerated vs committed analysis at manuscript precision.

For each paper-cited analysis claim (V9 registry), round archive and regen
values to the digits printed in the paper and report mismatches.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]


def _rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _row(path: Path, **filters: str) -> Dict[str, str]:
    for r in _rows(path):
        if all(str(r.get(k)) == str(v) for k, v in filters.items()):
            return r
    raise KeyError(f"{path.name} no row {filters}")


def _round_n(x: float, nd: int) -> float:
    return float(round(x, nd)) if nd > 0 else float(round(x))


Extractor = Callable[[Path], Tuple[Any, int]]
# returns (value, decimal_places); decimal_places=-1 means exact string/bool compare


def _extractors() -> Dict[str, Extractor]:
    def share(col: str, model: str, nd: int) -> Extractor:
        return lambda d: (float(_row(d / "variance_components.csv", model=model)[col]), nd)

    def l3_p10(col: str, nd: int) -> Extractor:
        return lambda d: (
            float(_row(d / "variance_components_l3_p10.csv", label="I10_l3_p10")[col]),
            nd,
        )

    return {
        "tl_share_P": share("share_P", "tl", 3),
        "tl_share_PM": share("share_PM", "tl", 3),
        "tl_share_E": share("share_E", "tl", 3),
        "l3_share_PM": l3_p10("share_PM", 3),
        "l3_share_P_ci_includes_0": l3_p10("share_P_ci_lo", 0),
        "l3_trunc_P_p10": lambda d: (
            str(_row(d / "variance_components_l3_p10.csv", label="I10_l3_p10")["trunc_P"]).lower(),
            -1,
        ),
        "tl_flip_k3_paired": lambda d: (
            float(
                _row(d / "rank_flip.csv", model="tl", k="3", protocol="paired", event="best")[
                    "prob"
                ]
            ),
            3,
        ),
        "l3_flip_k3_paired_p10": lambda d: (
            float(
                _row(
                    d / "rank_flip_l3_p10.csv", k="3", protocol="paired", event="best"
                )["prob"]
            ),
            3,
        ),
        "tl_near_tie_n_paired": lambda d: (
            int(
                float(
                    _row(
                        d / "power.csv",
                        model="tl",
                        pair="fedit-flora",
                        kind="observed_gap",
                    )["n_paired"]
                )
            ),
            0,
        ),
        "l3_near_tie_n_paired": lambda d: (
            _row(
                d / "power_l3_p10.csv", pair="fedit-flora", kind="observed_gap"
            )["n_paired"],
            -1,
        ),
        "base_loss_tl": lambda d: (
            float(next(r["base_loss"] for r in _rows(d / "runs.csv") if r["model"] == "tl")),
            3,  # paper prints 2.121
        ),
        "base_loss_l3": lambda d: (
            float(next(r["base_loss"] for r in _rows(d / "runs.csv") if r["model"] == "l3")),
            3,  # paper prints 2.169
        ),
        "sd_pair_tl": lambda d: (
            float(
                _row(
                    d / "power.csv", model="tl", kind="preregistered_delta", delta="0.005"
                )["sd_pair_model"]
            ),
            5,  # 0.00282
        ),
        "sd_pair_l3": lambda d: (
            float(
                _row(
                    d / "power_l3_p10.csv", kind="preregistered_delta", delta="0.005"
                )["sd_pair_model"]
            ),
            5,  # 0.00770
        ),
        "tl_near_tie_unpaired": lambda d: (
            int(
                float(
                    _row(
                        d / "power.csv",
                        model="tl",
                        pair="fedit-flora",
                        kind="observed_gap",
                    )["n_unpaired_per_method"]
                )
            ),
            0,
        ),
        "l3_near_tie_unpaired": lambda d: (
            _row(
                d / "power_l3_p10.csv", pair="fedit-flora", kind="observed_gap"
            )["n_unpaired_per_method"],
            -1,
        ),
        "method_means_tl_flora": lambda d: (
            float(
                _row(d / "method_means.csv", model="tl", method="flora", het="a01")["mean"]
            ),
            4,  # 1.6957
        ),
        "method_means_l3_p10_n20": lambda d: (
            int(
                float(
                    _row(d / "method_means.csv", model="l3", method="fedit", het="a01")["n"]
                )
            ),
            0,
        ),
        "stack_effect_l3_mean": lambda d: (
            float(
                _row(d / "stack_effect.csv", row_kind="summary", label="l3/a01")["mean_delta"]
            ),
            4,  # 8.4e-4 → compare at 1e-4
        ),
        "comm_v6_match": lambda d: (
            max(float(r["max_abs_err_vs_v6"]) for r in _rows(d / "comm.csv")),
            0,
        ),
        "ffa_slope_tl": lambda d: (
            float(
                _row(d / "comm.csv", model="tl", method="ffa_lora", het="a01")[
                    "fit_slope_per_active"
                ]
            ),
            4,  # 98.3125
        ),
        "n_runs_204": lambda d: (sum(1 for _ in _rows(d / "runs.csv")), 0),
        # Primary I1 LLaMA shares (paper / i7) — not only p=10
        "l3_i1_share_P": lambda d: (
            float(_row(d / "variance_components.csv", model="l3")["share_P"]),
            3,
        ),
        "l3_i1_share_PM": lambda d: (
            float(_row(d / "variance_components.csv", model="l3")["share_PM"]),
            3,
        ),
    }


# Expected manuscript-printed values (for the extra I1 LLaMA rows).
EXPECTED: Dict[str, Any] = {
    "l3_i1_share_P": 0.227,
    "l3_i1_share_PM": 0.764,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--committed", type=Path, required=True)
    ap.add_argument("--regenerated", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()

    lines = ["claim_id\tndigits\tarchive\tregen\texpected\tstatus"]
    mismatches: List[str] = []
    for cid, fn in _extractors().items():
        try:
            a_raw, nd = fn(args.committed)
            b_raw, _ = fn(args.regenerated)
        except Exception as exc:  # noqa: BLE001
            mismatches.append(f"{cid}: {exc}")
            lines.append(f"{cid}\t-\tERR\tERR\t-\tFAIL")
            continue

        if nd < 0:
            ok = str(a_raw) == str(b_raw)
            a_s, b_s = str(a_raw), str(b_raw)
            exp = EXPECTED.get(cid, "")
        elif isinstance(a_raw, int) and isinstance(b_raw, int):
            ok = a_raw == b_raw
            a_s, b_s = str(a_raw), str(b_raw)
            exp = EXPECTED.get(cid, "")
            if cid in EXPECTED:
                ok = ok and a_raw == EXPECTED[cid]
        else:
            a_s = _round_n(float(a_raw), nd)
            b_s = _round_n(float(b_raw), nd)
            ok = a_s == b_s
            exp = EXPECTED.get(cid)
            if exp is not None:
                ok = ok and a_s == _round_n(float(exp), nd)
            # stack_effect printed as 8.4e-4
            if cid == "stack_effect_l3_mean":
                ok = math.isclose(float(a_raw), float(b_raw), rel_tol=0, abs_tol=5e-5)
                a_s, b_s = f"{float(a_raw):.4g}", f"{float(b_raw):.4g}"
                exp = "8.4e-4"
                ok = ok and math.isclose(float(a_raw), 8.4e-4, rel_tol=0, abs_tol=5e-5)

        status = "OK" if ok else "FAIL"
        lines.append(f"{cid}\t{nd}\t{a_s}\t{b_s}\t{exp}\t{status}")
        if not ok:
            mismatches.append(f"{cid}: archive={a_s} regen={b_s} expected={exp}")

    text = "\n".join(lines) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"MANUSCRIPT_PRECISION_MISMATCHES={len(mismatches)}")
    for m in mismatches:
        print(f"MISMATCH {m}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
