\
#!/usr/bin/env python3

import argparse
import os
from typing import List

import pandas as pd


COV3_EXPECTED_COLS = ["event_count", "active_hours", "unique_rooms"]


def parse_args():
    ap = argparse.ArgumentParser(
        description="Audit an OOF prediction table for paper-reported counts and label prevalence."
    )
    ap.add_argument("--path", required=True, help="Path to OOF predictions table (.csv/.feather/.parquet)")
    ap.add_argument("--name", required=True, help="Human-readable dataset name (printed in header)")
    ap.add_argument("--subject-col", required=True, help="Subject identifier column (e.g., participant_id)")
    ap.add_argument("--label-cols", required=True, nargs="+", help="Label column(s) to summarize (e.g., y_true)")
    return ap.parse_args()


def read_table(path: str) -> pd.DataFrame:
    if not path:
        raise SystemExit("Empty --path. Did you forget to set your variable?")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".feather":
        return pd.read_feather(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    raise SystemExit(f"Unsupported extension {ext}. Supported: .csv, .feather, .parquet")


def print_label_distribution(df: pd.DataFrame, col: str) -> None:
    if col not in df.columns:
        print(f"- {col}: MISSING")
        return

    s = df[col]
    missing = int(s.isna().sum())
    uniq = int(s.nunique(dropna=True))

    print(f"- {col}: missing={missing}, unique={uniq}")
    vc = s.value_counts(dropna=False)
    # Print in a stable order if binary-ish; else by value_counts order.
    try:
        # attempt numeric sort for values like 0/1
        keys = sorted(vc.index.tolist(), key=lambda x: float(x))
        for k in keys:
            print(f"  {k}: {int(vc[k])}")
    except Exception:
        for k, v in vc.items():
            print(f"  {k}: {int(v)}")

    # Binary summary (interprets >0 as positive)
    try:
        y = pd.to_numeric(s, errors="coerce")
        pos = int((y > 0).sum())
        neg = int((y == 0).sum())
        denom = pos + neg
        prev = (pos / denom) if denom else float("nan")
        print(f"  binary summary: pos(1)={pos}, neg(0)={neg}, prevalence={prev:.4f}")
    except Exception:
        pass


def main():
    args = parse_args()
    df = read_table(args.path)

    print("\n" + "=" * 64)
    print(f"{args.name}: {os.path.basename(args.path)}")
    print("=" * 64)
    print(f"rows: {len(df)}")

    if args.subject_col not in df.columns:
        print(
            f"WARNING: subject_col '{args.subject_col}' not found. "
            "Use --list-columns to inspect."
        )
        print("\nCOLUMNS:")
        for c in df.columns:
            print(c)
        raise SystemExit(2)

    print(f"unique {args.subject_col}: {df[args.subject_col].nunique()}")

    print("\nLABEL DISTRIBUTIONS:")
    for col in args.label_cols:
        print_label_distribution(df, col)

    # Keep parity with earlier audit output: mention missing Cov3 columns in OOF tables.
    missing_cov3 = [c for c in COV3_EXPECTED_COLS if c not in df.columns]
    print("\nCOV3 SUMMARY (overall):")
    if missing_cov3:
        print(f"Cov3 columns missing (skipping): {missing_cov3}")
    else:
        # If the columns exist, print their simple summary (min/max/mean).
        desc = df[COV3_EXPECTED_COLS].describe().loc[["min", "mean", "max"]]
        print(desc.to_string())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
