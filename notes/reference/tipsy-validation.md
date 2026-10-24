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
