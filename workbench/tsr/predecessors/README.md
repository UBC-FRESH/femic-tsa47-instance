# Predecessor TSR netdown workbench

This directory holds the transcribed land-base ladders for the TSRs that
preceded the GBR North (TSA 46) and GBR South (TSA 47) TSAs.

## Status

| Predecessor | Code | Table | Status |
| --- | --- | --- | --- |
| North Coast | 21 | TSR 2007 Data Package, Table 2.1 (p. 9) | transcribed, with a source residual |
| Kingcome | 33 | TSR 2010 Data Package, Table 3 (pp. 14-15) | transcribed, reconciles |
| Mid Coast | 19 | TSR 2011 Data Package, multiple section tables | pending assembly |
| Strathcona | 37 | TSR 2012 Data Package, multiple section tables | pending assembly |

`tsa21_north_coast_netdown.csv` and `tsa33_kingcome_netdown.csv` are
transcriptions of the published tables, not model output. The `stage` column
uses the FEMIC grammar:

- `glb_to_aflb`
- `aflb_to_lhlb`
- `lhlb_to_thlb`
- `reference`

## Reconciliation notes

- Kingcome reconciles: `376,452 - 168,278 = 208,174` (~`208,175` current
  Pre-EBM THLB), and `208,175 - 26,123 = 182,052` current EBM THLB.
- North Coast does **not** reconcile in the published table:
  `850,794 - 730,095 = 120,699`, while the table reports `145,808` current
  THLB. The difference is 25,109 ha and is flagged in the CSV. Do not force it
  to balance; find the omitted addition or overlap before using it.
- The TSR 2012 Strathcona data package does not contain a single summary table
  in the form of Kingcome Table 3; its ladder must be assembled from the
  ownership, operability, low-site, problem-type, riparian, wildlife, OGMA and
  EBM tables, plus the AAC rationale.

## Provenance

The PDFs are cached under `~/.femic/tsr/corpus/tsa/` after `femic tsr fetch`.
They are not committed. The source page is in every CSV row.

## Next steps

1. Assemble Mid Coast (TSA 19) from the TSR 2011 data package and rationale.
2. Assemble Strathcona (TSA 37) from the TSR 2012 data package and rationale.
3. Clip the predecessor ladders to the current GBR 46/47 boundaries.
4. Apply the GBR land-use order overlay.
5. Reconcile GLB >= AFLB >= LHLB >= THLB and compare to the current targets.

The official GBR SELES/STSM model, if obtained, replaces the reconstructed
ladder as the primary source and becomes the comparison target.
