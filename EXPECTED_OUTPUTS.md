Expected checksums (SHA-256)
----------------------------
These correspond to the *author* OOF CSVs used for the paper audit.

CASAS_MCI_LOCKEDTASK_cov3_covpp_all_oof_preds.csv
  feb250aafe8ca31e4fcffb26c5a5a5ebcd64c69c72b32fe45ac26e286df054a2

CASAS_DX1_LOCKEDTASK_cov3_covpp_all_oof_preds.csv
  34896b21591e4aa7d4670517c1935b1d8eff21f2dfe4f3a79da11d88208ffe4b

TIHM_Agitation_oof_preds_cov3_covpp_all_CANON.csv
  341ccb3832ce2ea08ec7bfb79fbc3243579b3f464852339bc4eae4ab2eacffa9

Expected dataset audit counts
-----------------------------
CASAS-MCI OOF:
  rows=176, unique participants=176, positives=56, negatives=120, prevalence=0.318182

CASAS-DX1 OOF:
  rows=196, unique participants=196, positives=20, negatives=176, prevalence=0.102041

TIHM OOF:
  rows=2722, unique participants=56, positives=114, negatives=2608, prevalence=0.041881

Expected performance (AUC / AUPRC)
----------------------------------
CASAS-MCI:
  Cov3:  AUC=0.536756, AUPRC=0.359866
  CovPP: AUC=0.531548, AUPRC=0.371591
  All:   AUC=0.595387, AUPRC=0.454899
  Δ(All−Cov3): ΔAUC=+0.058631, ΔAUPRC=+0.095033
  gap-closed:  AUC=-0.088832, AUPRC=0.123385

CASAS-DX1:
  Cov3:  AUC=0.780540, AUPRC=0.328970
  CovPP: AUC=0.851989, AUPRC=0.677191
  All:   AUC=0.857670, AUPRC=0.591895
  Δ(All−Cov3): ΔAUC=+0.077131, ΔAUPRC=+0.262925
  gap-closed:  AUC=0.926335, AUPRC=1.324411

TIHM:
  Cov3:  AUC=0.808973, AUPRC=0.234876
  CovPP: AUC=0.913828, AUPRC=0.347920
  All:   AUC=0.913777, AUPRC=0.347185
  Δ(All−Cov3): ΔAUC=+0.104804, ΔAUPRC=+0.112309
  gap-closed:  AUC=1.000481, AUPRC=1.006543
