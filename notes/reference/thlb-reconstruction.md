# THLB reconstruction progress: TSA 47

Status: four predecessor ladders transcribed; a public GBR-order planning
dataset checked; the calibration target is unchanged.

## Automatic recipe build

`femic tsr recipe-init` and `femic tsr thlb-netdown-build` were run on Mid Coast
as a trial. The builder found only 4 compiled steps, all context, with zero
GLB/AFLB/LHLB/THLB stage rows. The older TSR PDFs are not parsed into structured
land-base rows by the canonical fact pool. The automatic path is not sufficient
for these predecessors.

## Transcribed or anchored

- North Coast (21): TSR 2007 Data Package Table 2.1, p. 9. Transcribed; 25,109 ha
  source residual.
- Mid Coast (19): TSR 2011 Data Package Table 3, p. 8. Transcribed; reconciles.
- Kingcome (33): TSR 2010 Data Package Table 3, pp. 14-15. Transcribed;
  reconciles.
- Strathcona (37): TSR 2005 Analysis Report Table 5, p. 14. Transcribed;
  reconciles to 160,454 ha. The 2012 current THLB anchor is 162,873 ha.

## Anchor comparison

| Anchor | TSA 46 | TSA 47 |
| --- | ---: | ---: |
| Rationale/current target | 268,970 ha | 145,256 ha |
| Predecessor netdown tables | 270,413 ha | 141,845-142,335 ha |
| Borealis GBR order spatial THLB | 329,724.9 ha | 267,139.9 ha |

The Borealis dataset is a **2016 GBR-order planning dataset**, not the legal TSR
model. Its `rollup = 'THLB'` values are spatial planning THLB, much higher than
the legal/effective targets and based on a different inventory/operability/
land-base definition. It is an overlay/upper-bound check, not a calibration
target.

## Decision

Keep the current predecessor-derived target for now. The netdown tables give a
narrow sensitivity band; the Borealis spatial THLB is an upper bound. The
official SELES/STSM model and the GBR legal-order overlay are needed before the
calibration target is replaced.

## Next steps

- Apply the GBR land-use order overlay to the predecessor ladders, using the
  Borealis spatial classes as a cross-check.
- Decide the authoritative anchor and replace the calibration target.
- Compare to the official SELES/STSM model when available.

The model still uses the predecessor-derived target and the safe sliver merge.
No calibration change has been applied.
