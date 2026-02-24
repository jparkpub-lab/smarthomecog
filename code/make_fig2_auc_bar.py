\
#!/usr/bin/env python3

"""
Regenerate Figure 2 (AUC bar chart) directly from the Table II values.

This is intentionally standalone: it does NOT require access to private datasets.
It simply re-plots the AUC values reported in the paper.

Usage:
  python3 make_fig2_auc_bar.py --out fig2_auc_bar.png
"""
import argparse

import matplotlib.pyplot as plt
import numpy as np


AUC = {
    "CASAS-MCI": {"Cov3": 0.536756, "CovPP": 0.531548, "All": 0.595387},
    "CASAS-DX1": {"Cov3": 0.780540, "CovPP": 0.851989, "All": 0.857670},
    "TIHM":      {"Cov3": 0.808973, "CovPP": 0.913828, "All": 0.913777},
}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fig2_auc_bar.png", help="Output PNG path")
    return ap.parse_args()


def main():
    args = parse_args()

    datasets = list(AUC.keys())
    models = ["Cov3", "CovPP", "All"]

    x = np.arange(len(datasets))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9.5, 3.2), dpi=150)

    for i, m in enumerate(models):
        vals = [AUC[d][m] for d in datasets]
        ax.bar(x + (i - 1) * width, vals, width, label=m)
        for j, v in enumerate(vals):
            ax.text(x[j] + (i - 1) * width, v + 0.01, f"{v:.4f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylim(0.45, 1.0)
    ax.set_ylabel("AUC")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(args.out, bbox_inches="tight")
    print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
