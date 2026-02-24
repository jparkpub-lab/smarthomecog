SMC2026 Confound-Aware Coverage Audit — Generated Code Bundle (v7)

This bundle contains two things:

1) paper_overleaf/
   The final LaTeX + figures package (Overleaf-ready) corresponding to:
   - SMC2026_ConfoundAware_FINAL_v7_margin_fixed.pdf
   - SMC2026_ConfoundAware_LaTeX_Overleaf_FINAL_v7_margin_fixed.zip

2) code/
   Standalone, self-contained scripts that reproduce the audit numbers reported in the paper
   from the 3 OOF prediction CSVs (CASAS-MCI, CASAS-DX1, TIHM-Agitation), plus an optional
   PDF reference/citation consistency check.

Quick start (recommended)
-------------------------
From *any* directory:

  bash code/run_validation.sh \
    /ABS/PATH/TO/CASAS_MCI_LOCKEDTASK_cov3_covpp_all_oof_preds.csv \
    /ABS/PATH/TO/CASAS_DX1_LOCKEDTASK_cov3_covpp_all_oof_preds.csv \
    /ABS/PATH/TO/TIHM_Agitation_oof_preds_cov3_covpp_all_CANON.csv \
    [optional:/ABS/PATH/TO/SMC2026_ConfoundAware_FINAL_v7_margin_fixed.pdf]

Outputs
-------
All outputs are written to: ./local_audits/
This matches the GitHub description instructions used in the reproducibility checklist.

Dependencies
------------
- Python 3.9+ recommended
- Required packages for OOF validation: numpy, pandas
- Required package for optional PDF reference check: PyPDF2

Install:
  python3 -m pip install -r code/requirements.txt

Notes
-----
- The SHA-256 check is done in Python (no macOS/Linux tool differences).
- Metric computation uses a tie-aware rank-based AUC implementation to match the values
  used for the paper audit.
