# Predecessor TSR netdown workbench

This directory holds the transcribed land-base ladders for the TSRs that
preceded the GBR North (TSA 46) and GBR South (TSA 47) TSAs, plus the public
GBR order planning data check.

## Status

| Predecessor | Code | Table | Status |
| --- | --- | --- | --- |
| North Coast | 21 | TSR 2007 Data Package, Table 2.1 (p. 9) | transcribed, 25,109 ha source residual |
| Mid Coast | 19 | TSR 2011 Data Package, Table 3 (p. 8) | transcribed, reconciles |
| Kingcome | 33 | TSR 2010 Data Package, Table 3 (pp. 14-15) | transcribed, reconciles |
| Strathcona | 37 | TSR 2005 Analysis Report, Table 5 (p. 14) | transcribed, reconciles; 2012 anchor differs by 2,419 ha |

The CSVs are transcriptions of published tables, not model output. The `stage`
column uses the FEMIC grammar:

- `glb_to_aflb`
- `aflb_to_lhlb`
- `lhlb_to_thlb`
- `reference`

## Reconciliation notes

- Mid Coast reconciles: PFLB `1,023,508 - 888,218 = 135,290` versus the
  published spatial THLB `135,293` (3 ha rounding); non-spatial removals
  `10,689` bring it to `124,604` versus `124,605`; future roads and TL
  reversion bring it to `129,659`.
- Kingcome reconciles: `376,452 - 168,278 = 208,174` (~`208,175` Pre-EBM THLB),
  and `208,175 - 26,123 = 182,052` EBM THLB.
- Strathcona's 2005 ladder reconciles: `346,826 - 186,372 = 160,454` current
  THLB, then `-776` future roads = `159,678`. The 2012 current THLB anchor is
  `162,873`, a `+2,419 ha` version difference.
- North Coast does **not** reconcile: `850,794 - 730,095 = 120,699` versus the
  published `145,808` current THLB. The `25,109 ha` residual is flagged in the
  CSV. Do not force it to balance.

## Apportionment to the GBR TSAs

- TSA 46 is the union of North Coast and Mid Coast.
  - Rationale/current target: `145,808 + 123,162 = 268,970 ha`.
  - Netdown-table anchor: `145,808 + 124,605 = 270,413 ha` (`+1,443 ha`).
- TSA 47 is the mainland portion of Kingcome and Strathcona, using the boundary
  overlap fractions `0.6008138789` and `0.2023382745`.
  - Rationale/current target: `145,256 ha`.
  - Kingcome table + 2005 Strathcona ladder: `141,845 ha`.
  - Kingcome table + 2012 Strathcona anchor: `142,335 ha`.

The spread is caused by using the AAC rationale/current THLB values versus the
analysis-table values, and by the 2005 vs 2012 Strathcona version.

## Public GBR order planning data

The UBC Borealis dataset **Great Bear Rainforest - landscape level planning
data** (`doi:10.5683/SP2/GY2QJH`, CC BY-NC-SA 4.0) is a 2016 GBR-order planning
dataset, not the legal TSR model. Its `Res_v1CN.shp` shapefile has a
`rollup = 'THLB'` class.

| Area | Spatial planning THLB |
| --- | ---: |
| TSA 46 | 329,724.9 ha |
| TSA 47 | 267,139.9 ha |
| North Coast TSA | 162,197.8 ha |
| Mid Coast TSA | 167,519.3 ha |
| Kingcome TSA | 229,307.9 ha |
| Strathcona TSA (GBR portion) | 37,868.0 ha |
| All 5 TSAs | 607,935.1 ha |

These are **spatial planning THLB** values. They are much higher than the
legal/effective TSR targets and use a different inventory/operability/land-base
definition. They are recorded as an overlay/upper-bound check, not as a
calibration target. The raw dataset is not committed because it is large and
CC BY-NC-SA; only these aggregate values are recorded.

## Next steps

1. Apply the GBR land-use order overlay to the predecessor ladders, using the
   Borealis spatial classes as a cross-check.
2. Decide the authoritative anchor and replace the calibration target.
3. Compare the reconstructed result to the official SELES/STSM model when it is
   obtained.
