# Full TSA 47 ws4 build evidence

The model is built by `scripts/build_full_tsa47_model.sh` from the FEMIC
export. The Patchworks XML/fragments pair is an interchange input to
`ws4 build`; Patchworks is not the runtime lane.

## Command

```bash
MODEL_DIR=runtime/tsa47_full \
PATCHWORKS_OUT=output/patchworks_tsa47_full \
CALIBRATE_THLB=1 \
THLB_TARGET_HA=145,256 \
scripts/build_full_tsa47_model.sh
```

The script exports the inventory, compiles and validates the ws4 matrix,
builds the baseline schedule, simulates and reports the run, and writes the
exact UI geometry and land-base underlay.

## Status

Pending the FEMIC upstream run. This note is updated with the fragment count,
block count, block area, managed area, and the calibration factor at P3 and P4.
