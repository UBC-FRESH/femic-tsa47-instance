# THLB reconstruction progress: TSA 47

Status: first slice transcribed. The current model still uses the
predecessor-derived THLB target; no calibration change has been applied.

## Automatic recipe build

`femic tsr recipe-init` and `femic tsr thlb-netdown-build` were run on the
predecessor TSA 19 (Mid Coast) as a trial. The builder found only 4 compiled
steps, all context, with **zero** GLB/AFLB/LHLB/THLB stage rows. The older TSR
PDFs are not parsed into structured land-base rows by the canonical fact pool.
The automatic path is therefore not sufficient for these four predecessors.

## Transcribed tables

- North Coast (21), TSR 2007 Data Package, Table 2.1, page 9:
  `workbench/tsr/predecessors/tsa21_north_coast_netdown.csv`.
- Kingcome (33), TSR 2010 Data Package, Table 3, pages 14-15:
  `workbench/tsr/predecessors/tsa33_kingcome_netdown.csv`.

Kingcome reconciles. North Coast has a 25,109 ha residual in the published
table and is flagged rather than forced.

## Remaining work

- Mid Coast (19): assemble the ladder from the TSR 2011 data package sections
  and rationale.
- Strathcona (37): assemble the ladder from the TSR 2012 data package sections
  and rationale; there is no single summary table.
- Clip and apportion to the current GBR boundaries.
- Apply the GBR land-use order overlay.
- Reconcile and replace the calibration target.

## SELES lead

The public SELES publication list records A. Fall's 2022 GBR LUO 2021 Analysis
Update Memos 1 and 7, the STSM v2022 documentation, and the 2015 GBR LUO review
analysis. The TSR model archive itself is not in the standard provincial TSR
folder. The data request list is in `notes/reference/thlb-netdown-plan.md`.

Until the official model arrives, the reconstructed lane is labelled
**reconstructed**, not official, and is the comparison target.
