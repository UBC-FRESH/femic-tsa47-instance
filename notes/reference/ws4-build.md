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

`scripts/run_aac_benchmark.sh` runs the ten-decade benchmark with the
target-driven greedy seed. `config/targets.tsa47_full.yaml` asks for the
published 830,500 m3/yr.

The strict benchmark schedules 3,872 blocks with
5,327 events and meets all ten decades with objective 0.0.

The coverage run schedules 3,951 blocks with 5,409
events, meets all ten decades, and covers the remaining above-threshold AUs:
4701002 (139.2 ha), 4701005 (111.4 ha).

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
