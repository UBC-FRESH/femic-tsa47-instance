#!/usr/bin/env bash
# Watch the TSA 47 AAC benchmark converge in the ws4 watcher.
#
# This is observational: it does not persist a run. Set SEED_GREEDY=0 to start
# from an empty schedule.
set -euo pipefail

INSTANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATASET="${DATASET:-$INSTANCE_ROOT/runtime/tsa47_full/matrix}"
TARGETS="${TARGETS:-$INSTANCE_ROOT/config/targets.tsa47_full.yaml}"
ACCOUNT="${ACCOUNT:-product.Yield.managed.Total}"
PERIOD_WIDTH="${PERIOD_WIDTH:-10}"
YEARS="${YEARS:-100}"
ITERATIONS="${ITERATIONS:-2000}"
REFRESH="${REFRESH:-2}"
SEED="${SEED:-42}"
SEED_GREEDY="${SEED_GREEDY:-1}"
PLAIN="${PLAIN:-0}"

args=(
  watch
  --dataset "$DATASET"
  --targets "$TARGETS"
  --account "$ACCOUNT"
  --period-width "$PERIOD_WIDTH"
  --years "$YEARS"
  --iterations "$ITERATIONS"
  --refresh "$REFRESH"
  --seed "$SEED"
)

if [ "$SEED_GREEDY" = "1" ]; then
  args+=(--seed-greedy)
fi
if [ "$PLAIN" = "1" ]; then
  args+=(--plain)
fi

cd "$INSTANCE_ROOT"
exec python -m ws4.cli "${args[@]}"
