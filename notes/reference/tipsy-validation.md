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
