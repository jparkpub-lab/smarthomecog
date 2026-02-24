\
#!/usr/bin/env python3

"""
Regenerate Figure 3 (leakage audit counts) from the reported counts in the paper.

Usage:
  python3 make_fig3_leakage_counts.py --out fig3_leakage_counts.png
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np


COUNTS = {
    "R² > 0.3": 4,
    "R² > 0.5": 2,
    "R² > 0.7": 1,
}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fig3_leakage_counts.png", help="Output PNG path")
    return ap.parse_args()


def main():
    args = parse_args()

    labels = list(COUNTS.keys())
    vals = [COUNTS[k] for k in labels]

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=150)
    ax.bar(x, vals)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Number of features")
    ax.set_title("Leakage audit: Cov3 predictability of non-coverage features")
    ax.set_ylim(0, max(vals) + 1)

    for i, v in enumerate(vals):
        ax.text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=10)

    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out, bbox_inches="tight")
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
