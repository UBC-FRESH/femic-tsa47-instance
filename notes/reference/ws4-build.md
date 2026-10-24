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
| Input fragments | 74,170 |
| Blocks after safe merge | 73,659 |
| Compiled fragments | 97,529 |
| Block area | 692,811.84 ha |
| Managed area | 145,256 ha |

## Safe sliver cleanup

`scripts/merge_slivers.py` merges only small blocks that preserve model
semantics: same AU, same IFM, same origin, area-weighted age within 20 years,
and both blocks with `RETENTION = 0`. Retention/IFM split fragments are never
merged, and isolated small blocks are kept.

| Measure | Value |
| --- | ---: |
| Small-block cutoff | 1.0 ha |
| Blocks merged | 511 |
| Area merged | 255.78 ha |
| Net area change | 0.0 ha |
| Skipped | age 210, different AU 1,667, different IFM 215, different origin 39, host-is-candidate 52, no touching neighbour 710, retention 58 |

## Benchmark

The benchmark of record is the TSR-consistent opening-first run at
`runtime/tsa47_full/runs/opening_first`. `scripts/build_tsr_lane.sh` builds
the BatchTIPSY curves, exports Patchworks, merges safe slivers, compiles the
matrix, and runs the opening-first schedule.

The run schedules 8,636 openings on 17,365 blocks, covering
103,413.3 ha with a 5.0-40.0 ha opening range. Patch area is
218,872.3 ha, all of it in the 5-40 ha class. All ten decades are inside the
8,305,000-8,306,000 m3 band; the realized decade volumes are 8,305,578.9-8,305,999.0 m3.

The opening-first schedule covers all 18 managed AUs, so
`scripts/check_harvest_coverage.py` reports no gaps and the allowlist is
unused. The earlier VDYP-transform runtime is retained at
`runtime/tsa47_full_vdyp_20261023` for comparison.

## Validation

- `ws4 build` and `ws4 validate` pass on the merged matrix.
- `scripts/check_runtime_signal.py` passes.
- `scripts/check_harvest_coverage.py` passes on the coverage run.
- The UI geometry is rendered from the merged fragments.

## UI geometry levels

The build writes two UI geometry files:

- `fragments.geojson` — 100 m simplified block layer, served by default.
- `fragments_full.geojson` — unsimplified block layer, retained for detail.

The overview is 22.6 MiB; the full layer is 93.0 MiB. The 100 m
overview is an interim scale fix, not a substitute for viewport or tiled
serving.

## Related dataset

The sibling instance is documented in
`notes/reference/related-instances.md`.
