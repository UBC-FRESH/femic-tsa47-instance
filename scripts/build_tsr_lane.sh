#!/usr/bin/env bash
# Build a TSR-consistent GBR model lane from the calibrated checkpoint.
#
# The lane derives a VRI species mix, writes a TSR-consistent BatchTIPSY
# input, runs BatchTIPSY under the documented Wine lane, replaces the treated
# curves in a bundle copy, and rebuilds the ws4 model. It does not overwrite
# the VDYP-transform production runtime.
set -euo pipefail

INSTANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$INSTANCE_ROOT"

TSA="${TSA:?Set TSA to 46 or 47}"
if [ "$TSA" = "46" ]; then
  DENSITY="${DENSITY:-4444}"
  TARGET_PER_DECADE="${TARGET_PER_DECADE:-8031000}"
  REGEN_DELAY="${REGEN_DELAY:-}"
else
  DENSITY="${DENSITY:-1000}"
  TARGET_PER_DECADE="${TARGET_PER_DECADE:-8306000}"
  REGEN_DELAY="${REGEN_DELAY:-1}"
fi

CHECKPOINT="${CHECKPOINT:-runtime/tsa${TSA}_full/thlb_calibrated_checkpoint.feather}"
if [ ! -f "$CHECKPOINT" ] && [ -f "runtime/tsa${TSA}_full_vdyp_20261023/thlb_calibrated_checkpoint.feather" ]; then
  CHECKPOINT="runtime/tsa${TSA}_full_vdyp_20261023/thlb_calibrated_checkpoint.feather"
fi
SOURCE_INPUT="${SOURCE_INPUT:-data/03_input-tsa${TSA}.csv}"
BUNDLE="${BUNDLE:-data/model_input_bundle}"
TSR_BUNDLE="${TSR_BUNDLE:-data/model_input_bundle_tsr}"
PATCHWORKS_OUT="${PATCHWORKS_OUT:-output/patchworks_tsa${TSA}_tsr}"
MODEL_DIR="${MODEL_DIR:-runtime/tsa${TSA}_tsr}"
BTC_EXE="${BTC_EXE:-tipsy_io/btc_install/tipsybtc-wine.sh}"
SCRATCH_DIR="${SCRATCH_DIR:-tipsy_io/scratch/tsa${TSA}_tsr}"
TIPY_RUN_ID="${TIPY_RUN_ID:-tsa${TSA}_tipsy_tsr}"
TOPOLOGY="${TOPOLOGY:-runtime/tsa${TSA}_full/topology.csv}"

python scripts/build_tsr_tipsy_input.py \
  --tsa "$TSA" \
  --checkpoint "$CHECKPOINT" \
  --source-input "$SOURCE_INPUT" \
  --density "$DENSITY" \
  ${REGEN_DELAY:+--regen-delay "$REGEN_DELAY"} \
  --out "tipsy_io/runs/03_input-tsa${TSA}_tsr.csv"

python scripts/run_tsr_tipsy.py \
  --tsa "$TSA" \
  --input "tipsy_io/runs/03_input-tsa${TSA}_tsr.csv" \
  --curves "tipsy_io/runs/curves_tsa${TSA}_tsr.csv" \
  --output "tipsy_io/runs/04_output-tsa${TSA}_tsr.csv" \
  --error "tipsy_io/runs/04_error-tsa${TSA}_tsr.csv" \
  --btc-exe "$BTC_EXE" \
  --scratch-dir "$SCRATCH_DIR" \
  --run-id "$TIPY_RUN_ID"

python scripts/build_tsr_bundle.py \
  --bundle-dir "$BUNDLE" \
  --curves "tipsy_io/runs/curves_tsa${TSA}_tsr.csv" \
  --out "$TSR_BUNDLE"

BUNDLE_DIR="$TSR_BUNDLE" \
CHECKPOINT="$CHECKPOINT" \
IFM_SOURCE_COL="thlb_raw_calibrated" \
PATCHWORKS_OUT="$PATCHWORKS_OUT" \
MODEL_DIR="$MODEL_DIR" \
bash "scripts/build_full_tsa${TSA}_model.sh"

mkdir -p "$MODEL_DIR/schedules" "$MODEL_DIR/runs"
python scripts/build_opening_schedule.py \
  --dataset "$MODEL_DIR/matrix" \
  --topology "$TOPOLOGY" \
  --out "$MODEL_DIR/schedules/opening_first.csv" \
  --years 100 \
  --min-area 5 \
  --max-area 40 \
  --target-per-decade "$TARGET_PER_DECADE" \
  --intermediate-share 0

python -m ws4.cli simulate \
  --dataset "$MODEL_DIR/matrix" \
  --schedule "$MODEL_DIR/schedules/opening_first.csv" \
  --out "$MODEL_DIR/runs/opening_first" \
  --years 100 \
  --topology "$TOPOLOGY" \
  --patch-accounts "config/patch_accounts.tsa${TSA}_full.yaml" \
  --patch-membership

python -m ws4.cli report \
  --run "$MODEL_DIR/runs/opening_first" \
  --targets "config/targets.tsa${TSA}_full_opening.yaml"

echo "TSR lane built under $MODEL_DIR"
