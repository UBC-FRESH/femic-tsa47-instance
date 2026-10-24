# Independent TIPSY height validation: TSA 47

Date: 2026-10-24
Status: first independent accuracy check; production unchanged.

## Why this exists

Area-to-AAC is not a measure of model accuracy. This check compares TIPSY
height-age predictions with observed RESULTS forest-cover heights at the same
age. It does not use the AAC target.

## Data and matching

- Observed source: RESULTS forest cover, 42,890 rows for the TSA 47 AOI.
- Filter: immature single-species stands, leading species >=80%, age 5-80,
  observed height >=1.3 m.
- Matched observations: 3,472.
- AU assignment: BEC + leading species + checkpoint-derived SI class.
- Prediction: linear interpolation of the TIPSY height curve at the observed
  age.

## Result

Current TSR curves:

- n = 3,472
- bias = **-0.55 m**
- MAE = **1.38 m**
- RMSE = **2.53 m**

Dominant CWH_HW H:

- age 5-15: n=2,125, observed 4.12 m, predicted 3.79 m, bias **-0.33 m (-8%)**
- age 16-30: n=60, bias +0.65 m
- age 31-50: n=27, bias -3.21 m
- age 51-80: n=221, observed 32.27 m, predicted 30.51 m, bias **-1.76 m (-5.5%)**

CWH_HW M, age 5-15: n=226, bias **-1.02 m (-28%)**.

RESULTS-screened curves, same observations:

- bias = **-0.34 m**
- MAE = **1.36 m**
- RMSE = **2.48 m**

The RESULTS curves are marginally closer overall, but the improvement is small
and the RESULTS input uses cover-derived species composition, so this is not a
clean out-of-sample comparison.

## Interpretation

The current TSR height curves are close for the dominant CWH_HW H young stands
and slightly conservative at older ages. CWH_HW M is the weakest well-sampled
cell. This is an accuracy signal, not a reason to choose the curve set that
needs less area.

## Site-index attribution

The CWH_HW H height bias is small because the SI gap is small:

| Age class | n | Observed SI | Checkpoint SI | Gap | Height bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5-15 | 2,125 | 28.0 m | 26.3 m | +1.7 m | -0.33 m |
| 51-80 | 221 | 28.0 m | 26.3 m | +1.7 m | -1.76 m |

CWH_HW M at ages 5-15 has observed SI 19.0 m versus checkpoint 17.0 m
(+2.0 m) and a -1.02 m height bias. The pattern is the same as TSA 46: the
checkpoint AU median understates the managed/harvested stand SI, but the gap is
much smaller in TSA 47.

## Holdout managed-SI test

A deterministic opening-id split (80% training, 20% holdout) was used to
estimate a managed-stand SI for each AU/SI cell. Species and density were held
at the current TSR input; only SI changed. The holdout observations were not
used to estimate SI.

| Curve set | n | Bias | MAE | RMSE |
| --- | ---: | ---: | ---: | ---: |
| Current TSR | 845 | -0.56 m | 1.52 m | 3.06 m |
| Managed SI | 845 | +0.13 m | 1.60 m | 3.04 m |

Bias improves, but MAE gets slightly worse and RMSE is essentially unchanged. TSR is already close; managed SI overcorrects TSA 47.

This is an accuracy experiment only; no production curve or AAC target was
changed.

## Volume and DBH data limitation

RESULTS `I_BASAL_AREA` is mostly a 1.0 placeholder, so observed quadratic-mean
DBH cannot be computed reliably. The public PSP layer is
`WHSE_FOREST_VEGETATION.ISMC_PSP_ACTIVE_SITES_SP`, which contains active plot
locations, not remeasured tree measurements. No CMI/PSP measurement table is
materialized in the public-data tree. Volume, DBH, and mortality validation
therefore remain a separate data-acquisition task.

## Public PSP/CMI data

The volume/DBH blocker is now a data-acquisition gap, not a data-absence gap.
BC FAIB publishes plot- and tree-level ground-plot compilations at:

``https://www.for.gov.bc.ca/ftp/HTS/external/!publish/ground_plot_compilations/psp/``

Available tables include:

- `faib_header.csv` — site coordinates, BEC, TSA, sample type.
- `faib_sample_byvisit.csv` — visit years and projected ages.
- `faib_compiled_smries.csv` — plot-level volume, basal area, QMD, stems by
  utilization limit.
- `faib_compiled_spcsmries.csv` — species-level volume/BA/QMD/stems.
- `faib_compiled_spcsmries_siteage.csv` — species age, top height, and SI.

For TSA 47:

- 30 PSP/CMI sites, 244 visits
- 1,217 visit rows with merchantable volume and QMD
- 410 rows with leading-species top height
- sample types: 3 natural-growth PSP, 27 experimental PSP

This unblocks a real volume/DBH validation table, but not a clean one: TIPSY is
a managed-stand model, natural-growth PSP is unmanaged, and experimental PSP
may carry treatments. The validation must report sample type separately and
use the 12.5 cm utilization limit consistently.

## Nemora ground-plot validation

The managed/young-stand check now uses Nemora's FAIB HPS pipeline and the non-PSP
GBR South compilation:

- `nemora ingest-faib-hps` prepared 1,284 plots / 8,255 live trees from the
  CMI, YSM, NFI, and VRI plots.
- AU matching uses BEC + leading species + checkpoint SI.
- Volume is compared at the 12.5 cm utilization limit.
- Stems use TIPSY `StemCount125`.
- DBH is approximate: TIPSY `DBHg000` is all-stem QMD, while PSP `QMD_LS` is at
  12.5 cm.

| Sample type | n | Volume bias | Volume MAE | DBH bias | Height bias | Stems bias |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VRI | 365 | -75.3 m3/ha | 138.8 m3/ha | -2.6 cm | -1.7 m | -158.7 sph |
| YSM | 11 | -44.5 m3/ha | 70.5 m3/ha | -4.0 cm | -2.1 m | -276.8 sph |
| CMI | 4 | -104.6 m3/ha | 106.9 m3/ha | +2.9 cm | -4.0 m | -455.1 sph |
| NFI | 6 | -258.7 m3/ha | 258.7 m3/ha | -2.1 cm | -2.8 m | -231.4 sph |

The VRI sample is large enough to show a consistent **underprediction** of
volume, DBH, height, and stems by the current TSR curves. VRI plots are
inventory audit plots, not remeasured PSP/CMI plots; YSM/CMI/NFI are stronger
sample types but have small counts. This is a real accuracy signal, not an AAC
tuning result.

The non-PSP `PLOT` field uses codes (`I/W/E/N/S`), but Nemora's HPS loader
expects integer plot ids. A staged code-to-index copy was used for this run.
That is a Nemora ingest limitation, not a property of the forest data.

## Caveats

- Height only. Volume, DBH, and mortality are not validated here.
- RESULTS cover is an inventory observation, not a remeasured PSP/CMI plot.
- Single-species filter excludes mixed stands.
- TIPSY age and observed total age are assumed comparable; regeneration delay
  is not adjusted.
- The RESULTS curves are not independent of the cover observations used to
  derive their species mix.

## Files

- `scripts/validate_tipsy_height.py`
- `tests/test_validate_tipsy_height.py`
- `config/tsr/tipsy_height_validation.tsa47.csv`
- `config/tsr/tipsy_height_validation_summary.tsa47.csv`
- `config/tsr/tipsy_height_validation_results.tsa47.csv`
- `config/tsr/tipsy_height_validation_results_summary.tsa47.csv`
