# RESULTS-derived TIPSY inputs: TSA 47

Date: 2026-10-24
Status: analysis complete; production TSR lane unchanged pending review.

## Purpose

Repeat the TSA 48 RESULTS-derived TIPSY analysis for TSA 47. The TSA 48 script
and tests are the workflow template; the TSA 47 AOI, AU table, site-index
medians, species mix, density, and genetic-worth values are re-derived here.

## Data

Fetched with `femic data bcdc-fetch` for the TSA 47 AOI bbox:

- RESULTS openings: 14,191 features
- RESULTS forest cover: 42,890 features
- RESULTS planting: 1,297 features

The layers are under `data/downloads/bcdc/` and are not tracked.

## Method

1. Filter openings to the TSA 47 AOI.
2. Select the latest/most complete forest-cover row per opening.
3. Map openings to the TSA 47 AUs by leading species and the checkpoint-derived
   median site index for each `(stratum, SI class)`.
4. Aggregate species composition, planting density, site index, genetic worth,
   and regeneration context.
5. Do **not** use overstory total stems as regeneration density. Where no
   planting record exists, the candidate density is blank and the base TIPSY
   input density is retained.
6. Screen to AU/SI groups with at least three planting records for the
   defensible comparison.

Genetic worth uses the Kingcome TSR 3 future-regime values: Cw/Fd 3%, others 0%.
OAF1 = 0.85 and OAF2 = 0.95.

## Candidate coverage

- 16 `(stratum, SI)` candidate rows.
- 6 rows with at least three planting records:
  CWH_CW L/M/H, CWH_FD H, CWH_HW M/H.
- 5 rows with one or two planting records.
- 5 rows with no planting record: CWH_BA L/M/H, CWH_YC H/M, MH_HM H, plus
  CWH_HW L and CWH_FD L.

The no-planting rows show implausible yield jumps when cover-derived species
and SI are used as a future prescription. They are retained in the raw
candidate table but excluded from the screened input.

## Results

All three scenarios meet the ten-decade 8,305,000-8,306,000 m3 band with 100% of
patch area in the 5-40 ha class.

| Scenario | Openings | Blocks | Scheduled area | Patch area |
| --- | ---: | ---: | ---: | ---: |
| Current TSR | 8,636 | 17,365 | 103,413.3 ha | 218,872.3 ha |
| RESULTS screened (>=3 planting) | 7,806 | 15,449 | 92,902.7 ha | 193,521.9 ha |
| RESULTS raw | 7,320 | 14,585 | 88,651.3 ha | 184,387.2 ha |

The screened scenario uses RESULTS for six AU/SI groups and retains the current
TSR input for the rest. It reduces scheduled area by about 10% relative to the
current TSR lane.

## Caveats

- RESULTS planting coverage is sparse: only 1,297 planting records for 14,191
  openings.
- The forest-cover species mix is the existing stand composition, not a
  regeneration prescription.
- The median SI is from the selected cover row; sparse AUs can shift by several
  metres.
- The stocking guide has not yet been used to filter species suitability.
- The raw RESULTS scenario is an upper-bound sensitivity, not a replacement for
  the benchmark of record.

## Files

- `scripts/build_results_tipsy_inputs.py`
- `tests/test_build_results_tipsy_inputs.py`
- `config/tsr/tipsy_au_results_candidates.tsa47.csv`
- `config/tsr/tipsy_au_results_candidates.tsa47_screened.csv`
- `config/tsr/tipsy_au_results_tsr_comparison.tsa47.csv`
- Candidate input: `tipsy_io/runs/03_input-tsa47_results_screened.csv`
- Screened run: `runtime/tsa47_results_screened/runs/opening_first`

## Commands

```bash
python scripts/build_results_tipsy_inputs.py \
  --download-root data/downloads/bcdc \
  --aoi data/source/aoi/tsa47_full.gpkg \
  --out config/tsr/tipsy_au_results_candidates.tsa47.csv \
  --tipsy-input tipsy_io/runs/03_input-tsa47_results.csv \
  --base-input data/03_input-tsa47.csv \
  --au-table data/model_input_bundle/au_table.csv \
  --checkpoint runtime/tsa47_full_vdyp_20261023/thlb_calibrated_checkpoint.feather \
  --fallback-density 1000
```

The screened input is written by filtering the candidate table to
`planting_opening_count >= 3` and applying it to the base input.
