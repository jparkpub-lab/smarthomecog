\
#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Standalone validation runner for the SMC2026 coverage/confound audit.
#
# Usage:
#   bash code/run_validation.sh <CASAS_MCI_OOF.csv> <CASAS_DX1_OOF.csv> <TIHM_OOF.csv> [paper.pdf]
#
# Output:
#   ./local_audits/   (created if missing)
# ------------------------------------------------------------

if [[ $# -lt 3 ]]; then
  echo "usage: bash code/run_validation.sh <CASAS_MCI_OOF.csv> <CASAS_DX1_OOF.csv> <TIHM_OOF.csv> [paper.pdf]" >&2
  exit 2
fi

CASAS_MCI_OOF="$1"
CASAS_DX1_OOF="$2"
TIHM_OOF="$3"
PAPER_PDF="${4:-}"

OUTDIR="local_audits"
mkdir -p "$OUTDIR"

echo "Repo/package root: $(pwd)"
echo

echo "Checking that OOF CSVs exist..."
ls -lh "$CASAS_MCI_OOF" "$CASAS_DX1_OOF" "$TIHM_OOF"
echo

echo "Running dataset audits (counts/prevalence) ..."
python3 code/oof_audit.py \
  --path "$CASAS_MCI_OOF" \
  --name "CASAS-MCI OOF" \
  --subject-col participant_id \
  --label-cols y_true \
| tee "$OUTDIR/casas_mci_oof_audit.txt"

python3 code/oof_audit.py \
  --path "$CASAS_DX1_OOF" \
  --name "CASAS-DX1 OOF" \
  --subject-col participant_id \
  --label-cols y_true \
| tee "$OUTDIR/casas_dx1_oof_audit.txt"

python3 code/oof_audit.py \
  --path "$TIHM_OOF" \
  --name "TIHM OOF" \
  --subject-col participant_id \
  --label-cols y_true \
| tee "$OUTDIR/tihm_oof_audit.txt"
echo

echo "Computing SHA-256..."
python3 code/sha256_check.py "$CASAS_MCI_OOF" "$CASAS_DX1_OOF" "$TIHM_OOF" | tee "$OUTDIR/oof_sha256.txt"
echo

echo "Strict SHA-256 check vs expected (paper/author files)..."
python3 code/sha256_check.py --check "$CASAS_MCI_OOF" "$CASAS_DX1_OOF" "$TIHM_OOF" | tee "$OUTDIR/oof_sha256_check.txt"
echo

echo "Computing AUC/AUPRC + gap-closed ratios (and checking expected values)..."
python3 code/metrics_from_oof.py "$CASAS_MCI_OOF" "$CASAS_DX1_OOF" "$TIHM_OOF" --check | tee "$OUTDIR/oof_metrics.txt"
echo

if [[ -n "$PAPER_PDF" ]]; then
  if [[ -f "$PAPER_PDF" ]]; then
    echo "Running PDF reference/citation validation..."
    python3 code/pdf_reference_check.py "$PAPER_PDF" | tee "$OUTDIR/pdf_reference_check.txt"
    echo
  else
    echo "WARNING: PAPER_PDF was provided but not found: $PAPER_PDF" >&2
  fi
else
  echo "Optional PDF validation:"
  echo "  To enable, pass a 4th argument:"
  echo "    bash code/run_validation.sh <mci.csv> <dx1.csv> <tihm.csv> /ABS/PATH/TO/paper.pdf"
  echo "  (Requires: python3 -m pip install PyPDF2)"
  echo
fi

echo "ALL VALIDATION STEPS COMPLETED ✅"
echo "Outputs are in: $(pwd)/$OUTDIR/"
