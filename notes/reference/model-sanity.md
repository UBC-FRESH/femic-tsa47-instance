# Model sanity audit

Date: 2026-10-24
Dataset: `runtime/tsa47_full/matrix`
Benchmark: `runtime/tsa47_full/runs/opening_first`

## Species composition

The compiled `feature.Area.og1.*` accounts match the coastal CWH/MH mix. Every
species with area has a nonzero account and a resolved curve. The
runtime-signal gate passes.

## Managed area

- Block area: 692,811.84 ha.
- Managed area: 145,256 ha.
- Managed area is preserved by the safe sliver merge.

## Benchmark

- Openings: 8,636.
- Scheduled blocks: 17,365.
- All ten decade targets met at the published 830,500 m3/yr AAC.
- The opening-first schedule fills the 5-40 ha class and covers every managed
  AU.

## Zero-harvest AUs

The opening-first schedule covers every managed AU. There are no zero-harvest
AUs and `config/harvest_coverage.allowlist.json` is empty. The earlier strict
volume-only schedule left small AUs unselected; that result is retained with
the dated VDYP-transform runtime.

## Accuracy validation

- Current TSR height bias -0.55 m, MAE 1.38 m, RMSE 2.53 m against observed immature single-species RESULTS cover heights.
- RESULTS species are not more accurate.
- Volume/DBH/mortality are not yet validated.

## Status

Pass. The compiled runtime signal is complete, the safe merge preserves area and
managed area, and the strict and coverage benchmarks both meet the AAC.
