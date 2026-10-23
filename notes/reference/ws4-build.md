# Full TSA 47 ws4 build evidence

The model is built by `scripts/build_full_tsa47_model.sh` from the FEMIC
export. The Patchworks XML/fragments pair is an interchange input to
`ws4 build`; Patchworks is not the runtime lane.

## Command

```bash
MODEL_DIR=runtime/tsa47_full \
PATCHWORKS_OUT=output/patchworks_tsa47_full \
CALIBRATE_THLB=1 \
THLB_TARGET_HA=145256 \
scripts/build_full_tsa47_model.sh
```

## Dataset

| Table | Value |
| --- | ---: |
| AU count | 18 |
| Curves | 73 |
| Fragments exported | 74,170 |
| Blocks compiled | 74,170 |
| Block area | 692,811.84 ha |
| Managed area, uncalibrated | 146,347.89 ha |
| Managed area, calibrated | 145,256.00 ha |
| Calibration factor | 0.9925390944203576 |
| Saturated rows | 0 |

The calibrated THLB is the derived predecessor-value target in
`config/tsr/overlay.yaml`: 60.08% of the former Kingcome current EBM THLB
(186,914 ha) plus 20.23% of the former Strathcona current THLB (162,873 ha),
giving 145,256 ha.

## Benchmark

`scripts/run_aac_benchmark.sh` runs the ten-decade benchmark with the
target-driven greedy seed. `config/targets.tsa47_full.yaml` asks for
8,305,000-8,306,000 m3 per decade at 830,500 m3/yr.

Result: all ten decades met, objective 0.0, 3,872 blocks scheduled, 5,000
iterations, 500 patience, seed 42. The report is
`runtime/tsa47_full/runs/aac_benchmark/report_targets.csv`.

The baseline schedule is a clearcut-at-age-60 reference, not the benchmark. It
dumps all mature stands in the first decade and is reported only as a
reproducible starting point.

## Validation

- `ws4 build` and `ws4 validate` pass on the full matrix.
- The UI geometry has one feature per block and the land base is the TSA 47 AOI.
- `runtime/tsa47_full/evidence/thlb_calibration.json` records the calibration.

## Related dataset

The GBR North TSA 46 model is built independently in
`UBC-FRESH/femic-tsa46-instance`. See
`notes/reference/related-instances.md`.
