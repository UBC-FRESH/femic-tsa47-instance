#!/usr/bin/env bash
# Build the full TSA 47 ws4 model after `femic run` has produced the upstream
# bundle and checkpoint. The TSA is the whole model; there are no part flags.
set -euo pipefail

INSTANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$INSTANCE_ROOT"

RUN_ID="${RUN_ID:-tsa47_full_20261023}"
CHECKPOINT="${CHECKPOINT:-data/vri_vclr1p_checkpoint8.feather}"
PATCHWORKS_OUT="${PATCHWORKS_OUT:-output/patchworks_tsa47_full}"
MODEL_DIR="${MODEL_DIR:-runtime/tsa47_full}"
TARGET_AGE="${TARGET_AGE:-60}"
YEARS="${YEARS:-100}"
CALIBRATE_THLB="${CALIBRATE_THLB:-0}"
THLB_TARGET_HA="${THLB_TARGET_HA:-145256}"
IFM_SOURCE_COL="${IFM_SOURCE_COL:-}"
MERGE_SLIVERS="${MERGE_SLIVERS:-1}"
SLIVER_CUTOFF_HA="${SLIVER_CUTOFF_HA:-1.0}"
SLIVER_AGE_TOLERANCE="${SLIVER_AGE_TOLERANCE:-20}"
LAND_BASE_AOI="${LAND_BASE_AOI:-data/source/aoi/tsa47_full.gpkg}"

mkdir -p "$MODEL_DIR" "$MODEL_DIR/schedules" "$MODEL_DIR/runs" "$MODEL_DIR/evidence"

if [ "$CALIBRATE_THLB" = "1" ]; then
  if [ -z "$THLB_TARGET_HA" ]; then
    echo "CALIBRATE_THLB=1 requires THLB_TARGET_HA" >&2
    exit 2
  fi
  CALIBRATED_CHECKPOINT="$MODEL_DIR/thlb_calibrated_checkpoint.feather"
  python scripts/calibrate_thlb_proportion.py \
    --checkpoint "$CHECKPOINT" \
    --target-ha "$THLB_TARGET_HA" \
    --out-checkpoint "$CALIBRATED_CHECKPOINT" \
    --summary "$MODEL_DIR/evidence/thlb_calibration.json"
  CHECKPOINT="$CALIBRATED_CHECKPOINT"
  IFM_SOURCE_COL="thlb_raw_calibrated"
fi

python -m femic export patchworks \
  --tsa 47 \
  --bundle-dir data/model_input_bundle \
  --checkpoint "$CHECKPOINT" \
  --ifm-mode proportional \
  ${IFM_SOURCE_COL:+--ifm-source-col "$IFM_SOURCE_COL"} \
  --output-dir "$PATCHWORKS_OUT"

FRAGMENTS="$PATCHWORKS_OUT/fragments/fragments.shp"
if [ "$MERGE_SLIVERS" = "1" ]; then
  MERGED_DIR="$PATCHWORKS_OUT/fragments_merged"
  python scripts/merge_slivers.py \
    --fragments "$FRAGMENTS" \
    --out "$MERGED_DIR/fragments.shp" \
    --cutoff-ha "$SLIVER_CUTOFF_HA" \
    --age-tolerance "$SLIVER_AGE_TOLERANCE" \
    > "$MODEL_DIR/evidence/sliver_merge.json"
  FRAGMENTS="$MERGED_DIR/fragments.shp"
fi

python -m ws4.cli build \
  --xml "$PATCHWORKS_OUT/forestmodel.xml" \
  --fragments "$FRAGMENTS" \
  --out "$MODEL_DIR/matrix"

python -m ws4.cli validate --dataset "$MODEL_DIR/matrix"

python scripts/build_baseline_schedule.py \
  --dataset "$MODEL_DIR/matrix" \
  --out "$MODEL_DIR/schedules/baseline.csv" \
  --target-age "$TARGET_AGE"

python -m ws4.cli simulate \
  --dataset "$MODEL_DIR/matrix" \
  --schedule "$MODEL_DIR/schedules/baseline.csv" \
  --out "$MODEL_DIR/runs/baseline" \
  --years "$YEARS"

python -m ws4.cli report \
  --run "$MODEL_DIR/runs/baseline" \
  --targets config/targets.tsa47_full.yaml

python scripts/prepare_ws4_ui.py \
  --fragments "$FRAGMENTS" \
  --out "$MODEL_DIR/fragments_full.geojson" \
  --simplify-m 0

python scripts/prepare_ws4_ui.py \
  --fragments "$FRAGMENTS" \
  --out "$MODEL_DIR/fragments.geojson" \
  --simplify-m "${UI_SIMPLIFY_M:-100}"

python scripts/prepare_land_base.py \
  --aoi "$LAND_BASE_AOI" \
  --out "$MODEL_DIR/land_base.geojson"

echo "full TSA 47 model built under $MODEL_DIR"
