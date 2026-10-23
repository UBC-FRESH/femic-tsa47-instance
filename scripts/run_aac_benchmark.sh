#!/usr/bin/env bash
# Run the ten-decade AAC benchmark for the calibrated TSA 47 model.
#
# The search starts from the target-driven greedy seed and writes a run
# directory under the model's runs tree, so the web UI lists it.
set -euo pipefail

INSTANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_DIR="${MODEL_DIR:-$INSTANCE_ROOT/runtime/tsa47_full}"
DATASET="${DATASET:-$MODEL_DIR/matrix}"
TARGETS="${TARGETS:-$INSTANCE_ROOT/config/targets.tsa47_full.yaml}"
OUT="${OUT:-$MODEL_DIR/runs/aac_benchmark}"
YEARS="${YEARS:-100}"
ITERATIONS="${ITERATIONS:-5000}"
PATIENCE="${PATIENCE:-500}"
SEED="${SEED:-42}"
THREADS="${THREADS:-8}"
TIME_LIMIT="${TIME_LIMIT:-00:30:00}"

args=(
  optimize
  --dataset "$DATASET"
  --targets "$TARGETS"
  --out "$OUT"
  --years "$YEARS"
  --iterations "$ITERATIONS"
  --patience "$PATIENCE"
  --seed "$SEED"
  --threads "$THREADS"
  --time-limit "$TIME_LIMIT"
  --seed-greedy
)

cd "$INSTANCE_ROOT"
exec python -m ws4.cli "${args[@]}"
