\
#!/usr/bin/env python3

import argparse
import json
import math
import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def to_binary(y: np.ndarray) -> np.ndarray:
    """
    Convert a label array to {0,1} with a conservative mapping:
      - bool -> int
      - numeric -> 1 if >0 else 0
      - string -> 1 if in {"1","true","t","yes","y","pos","positive"} else 0
    """
    y = np.asarray(y)
    if y.dtype == bool:
        return y.astype(int)

    # Try numeric conversion first
    try:
        y_num = y.astype(float)
        return (y_num > 0).astype(int)
    except Exception:
        y_str = np.char.lower(y.astype(str))
        return np.isin(y_str, ["1", "true", "t", "yes", "y", "pos", "positive"]).astype(int)


def auc_roc(y: np.ndarray, s: np.ndarray) -> float:
    """
    Tie-aware ROC AUC using rank statistics (equivalent to Mann–Whitney U / Wilcoxon rank-sum).
    This matches the earlier audit snippet and avoids dependency on sklearn.
    """
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    n1 = int(y.sum())
    n0 = int(len(y) - n1)
    if n1 == 0 or n0 == 0:
        return float("nan")

    order = np.argsort(s)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(y) + 1, dtype=float)

    # average ranks for ties
    s_sorted = s[order]
    i = 0
    while i < len(y):
        j = i
        while j + 1 < len(y) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        if j > i:
            avg = (i + 1 + j + 1) / 2.0
            ranks[order[i : j + 1]] = avg
        i = j + 1

    sum_pos_ranks = ranks[y == 1].sum()
    return float((sum_pos_ranks - n1 * (n1 + 1) / 2.0) / (n0 * n1))


def average_precision(y: np.ndarray, s: np.ndarray) -> float:
    """
    Average Precision (AP), equivalent to AUPRC for a ranked list.
    Uses the conventional definition averaging precision at each positive.
    """
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    n1 = int(y.sum())
    if n1 == 0:
        return float("nan")

    order = np.argsort(-s, kind="mergesort")
    y_sorted = y[order]
    tp = np.cumsum(y_sorted == 1)
    precision = tp / (np.arange(len(y_sorted)) + 1)
    return float(precision[y_sorted == 1].sum() / n1)


def gap_closed(num: float, den: float) -> float:
    if den == 0 or math.isnan(den) or math.isnan(num):
        return float("nan")
    return float(num / den)


def read_expected(expected_json: str) -> Dict:
    with open(expected_json, "r", encoding="utf-8") as f:
        return json.load(f)


def report_one(path: str, name: str) -> Dict[str, Dict[str, float]]:
    df = pd.read_csv(path)

    id_col = "participant_id"
    y_col = "y_true"
    pred_cols = {"Cov3": "pred_cov3", "CovPP": "pred_covpp", "All": "pred_all"}

    for c in [id_col, y_col, *pred_cols.values()]:
        if c not in df.columns:
            raise SystemExit(f"{name}: missing required column '{c}'. Columns={list(df.columns)}")

    y = to_binary(df[y_col].to_numpy())

    results: Dict[str, Dict[str, float]] = {}
    print("=" * 88)
    print(f"{name}: {os.path.basename(path)}")
    print(f"rows: {len(df)}")
    print(f"unique {id_col}: {df[id_col].nunique()}")
    print(f"positives: {int(y.sum())} / {len(y)} (negatives: {len(y)-int(y.sum())}; prevalence={y.mean():.6f})")

    for m, c in pred_cols.items():
        auc = auc_roc(y, df[c].to_numpy())
        ap = average_precision(y, df[c].to_numpy())
        results[m] = {"AUC": float(auc), "AUPRC": float(ap)}
        print(f"{m:5s}  AUC={auc:.6f}   AUPRC(AP)={ap:.6f}")

    auc_cov3 = results["Cov3"]["AUC"]
    ap_cov3 = results["Cov3"]["AUPRC"]
    auc_covpp = results["CovPP"]["AUC"]
    ap_covpp = results["CovPP"]["AUPRC"]
    auc_all = results["All"]["AUC"]
    ap_all = results["All"]["AUPRC"]

    delta_auc = auc_all - auc_cov3
    delta_ap = ap_all - ap_cov3

    print("Δ(All - Cov3):")
    print(f"  ΔAUC   = {delta_auc:+.6f}")
    print(f"  ΔAUPRC = {delta_ap:+.6f}")

    gc_auc = gap_closed(auc_covpp - auc_cov3, auc_all - auc_cov3)
    gc_ap = gap_closed(ap_covpp - ap_cov3, ap_all - ap_cov3)

    print("Gap-closed ratio (CovPP - Cov3) / (All - Cov3):")
    print(f"  AUC   gap-closed = {gc_auc:.6f}")
    print(f"  AUPRC gap-closed = {gc_ap:.6f}")
    print()

    results["delta_all_minus_cov3"] = {"AUC": float(delta_auc), "AUPRC": float(delta_ap)}
    results["gap_closed"] = {"AUC": float(gc_auc), "AUPRC": float(gc_ap)}
    return results


def check_expected(results: Dict[str, Dict], expected: Dict, tol: float) -> None:
    exp_metrics = expected["metrics"]
    for dataset_name, exp in exp_metrics.items():
        if dataset_name not in results:
            raise SystemExit(f"[FAIL] Missing dataset in results: {dataset_name}")

        got = results[dataset_name]
        for block in ["Cov3", "CovPP", "All", "delta_all_minus_cov3", "gap_closed"]:
            for metric in ["AUC", "AUPRC"]:
                exp_val = float(exp[block][metric])
                got_val = float(got[block][metric])
                if not (abs(exp_val - got_val) <= tol):
                    raise SystemExit(
                        f"[FAIL] {dataset_name} {block} {metric}: expected {exp_val:.6f} got {got_val:.6f} (tol={tol})"
                    )
    print("[OK] Metric check PASSED (matches expected paper values).")


def parse_args():
    ap = argparse.ArgumentParser(description="Compute AUC/AUPRC from OOF predictions + gap-closed ratios.")
    ap.add_argument("casas_mci_oof", help="CASAS-MCI OOF predictions CSV")
    ap.add_argument("casas_dx1_oof", help="CASAS-DX1 OOF predictions CSV")
    ap.add_argument("tihm_oof", help="TIHM agitation OOF predictions CSV")
    ap.add_argument("--expected-json", default=os.path.join(os.path.dirname(__file__), "expected_values.json"))
    ap.add_argument("--check", action="store_true", help="Check against expected values in expected_values.json")
    ap.add_argument("--tol", type=float, default=None, help="Absolute tolerance for metric checks (default from json).")
    return ap.parse_args()


def main():
    args = parse_args()

    paths = {
        "CASAS-MCI OOF": args.casas_mci_oof,
        "CASAS-DX1 OOF": args.casas_dx1_oof,
        "TIHM OOF": args.tihm_oof,
    }
    for _, p in paths.items():
        if not os.path.exists(p):
            raise SystemExit(f"Missing file: {p}")

    all_results: Dict[str, Dict] = {}
    for name, path in paths.items():
        all_results[name] = report_one(path, name)

    if args.check:
        expected = read_expected(args.expected_json)
        tol = args.tol if args.tol is not None else float(expected["tolerance"]["metrics_abs"])
        check_expected(all_results, expected, tol)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
