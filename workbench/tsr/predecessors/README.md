# Predecessor TSR netdown workbench

This directory holds the transcribed land-base ladders for the TSRs that
preceded the GBR North (TSA 46) and GBR South (TSA 47) TSAs.

## Status

| Predecessor | Code | Table | Status |
| --- | --- | --- | --- |
| North Coast | 21 | TSR 2007 Data Package, Table 2.1 (p. 9) | transcribed, 25,109 ha source residual |
| Mid Coast | 19 | TSR 2011 Data Package, Table 3 (p. 8) | transcribed, reconciles |
| Kingcome | 33 | TSR 2010 Data Package, Table 3 (pp. 14-15) | transcribed, reconciles |
| Strathcona | 37 | TSR 2012 Data Package, sections 5.3-5.17 | anchor only; no summary table |

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
- North Coast does **not** reconcile: `850,794 - 730,095 = 120,699` versus the
  published `145,808` current THLB. The `25,109 ha` residual is flagged in the
  CSV. Do not force it to balance.
- Strathcona has no single summary table in the TSR 2012 data package. The CSV
  records the published current THLB (`162,873`) and future THLB (`156,806`),
  plus two component reductions, and leaves the staged ladder pending.

## Apportionment to the GBR TSAs

- TSA 46 is the union of North Coast and Mid Coast.
  - Current calibration target: `145,808 + 123,162 = 268,970 ha`.
  - Table-based anchor: `145,808 + 124,605 = 270,413 ha` (`+1,443 ha`).
- TSA 47 is the mainland portion of Kingcome and Strathcona, using the boundary
  overlap fractions `0.6008138789` and `0.2023382745`.
  - Current calibration target: `0.6008 x 186,914 + 0.2023 x 162,873 =
    145,256 ha`.
  - Table-based anchor: `0.6008 x 182,052 + 0.2023 x 162,873 = 142,335 ha`
    (`-2,921 ha`).

The difference is caused by using the AAC rationale/current effective THLB
values versus the TSR analysis-table values. Do **not** change the calibration
until a reviewed decision picks the authoritative anchor. The official SELES
model would resolve it.

## Next steps

1. Assemble the full Strathcona ladder from the TSR 2012 data package and
   rationale.
2. Apply the GBR land-use order overlay to the predecessor ladders.
3. Decide the authoritative anchor and replace the calibration target.
4. Compare the reconstructed result to the official SELES/STSM model when it is
   obtained.
