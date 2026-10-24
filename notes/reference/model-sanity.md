# Model sanity audit

Date: 2026-10-24
Dataset: `runtime/tsa47_full/matrix`
Benchmark: `runtime/tsa47_full/runs/aac_benchmark`

## Species composition

The compiled `feature.Area.og1.*` accounts match the coastal CWH/MH mix. Every
species with area has a nonzero account and a resolved curve. The
runtime-signal gate passes.

## Managed area

- Block area: 692,811.84 ha.
- Managed area: 145,256 ha.
- Managed area is preserved by the safe sliver merge.

## Benchmark

- Unique blocks harvested: 3,872.
- Events: 5,327.
- All ten decade targets met at the published AAC.
- Coverage run: 3,951 blocks, 5,409 events, ten decades
  met.

## Zero-harvest AUs

The strict volume-only benchmark leaves these managed AUs unselected:

- 4701002 (139.2 ha), 4701005 (111.4 ha)

They are allowlisted in `config/harvest_coverage.allowlist.json` with the reason
that the coverage run harvests them. The coverage gate passes on the coverage
run with no allowlist.

## Status

Pass. The compiled runtime signal is complete, the safe merge preserves area and
managed area, and the strict and coverage benchmarks both meet the AAC.
