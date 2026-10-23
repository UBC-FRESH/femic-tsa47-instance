# FEMIC Great Bear Rainforest South TSA 47 Instance

Public FEMIC and ws4 model instance for the Great Bear Rainforest South TSA 47
area of interest. FEMIC rebuilds the inventory and yield curves from public BC
data; ws4 compiles the model, runs the benchmark, and serves the web UI. This
repository is tracked in `femic` as the `external/femic-tsa47-instance`
submodule.

## Runtime lane

**ws4 is the primary runtime.** The Patchworks XML/fragments package is an
interchange input to `ws4 build`, not the runtime lane.

## Related instance

This repository is deliberately related to
**[`UBC-FRESH/femic-tsa47-instance`](https://github.com/UBC-FRESH/femic-tsa47-instance)**,
the Great Bear Rainforest South TSA 47 model. They share the same public
inventory, FEMIC export lane, and GBR legal framework, but they are
**independent datasets and runtimes**:

- this repository owns the GBR South boundary, AAC, THLB, and benchmark;
- `femic-tsa47-instance` owns the GBR South boundary, AAC, THLB, and benchmark;
- neither repository requires the other to build or run.

## Status

Bootstrap: the repository, AOI, public-data manifest, and build scaffold are in
place. The upstream FEMIC run and the ws4 model build follow the phases in
`ROADMAP.md`.

## AOI

The tracked boundary is `data/source/aoi/tsa47_full.gpkg` (EPSG:3005, layer
`tsa47_full`, **1,991,787.47 ha gross**). It is the single current dissolved
FADM TSA 47 feature: no supply-block code and no retirement date. The gross area
includes ocean and foreshore; the VRI block area is the forested subset.

## Model

The model is built by `scripts/build_full_tsa47_model.sh`:

```bash
MODEL_DIR=runtime/tsa47_full \
PATCHWORKS_OUT=output/patchworks_tsa47_full \
CALIBRATE_THLB=1 \
THLB_TARGET_HA=145256 \
scripts/build_full_tsa47_model.sh
```

The script exports the FEMIC inventory, compiles and validates the ws4 matrix,
builds the baseline schedule, simulates and reports the run, and writes the
exact UI geometry and land-base underlay.

## Benchmark

`config/targets.tsa47_full.yaml` carries ten per-decade targets with an
**8,305,000–8,306,000 m3** band around the published **830,500 m3/yr** AAC
(B.C. Reg. 328/2016, effective January 1, 2017).

## Web UI

```bash
./serve_tsa47_calibrated.sh
```

The service listens on `http://127.0.0.1:8018/`. `PORT=...` overrides the
default. The script passes `--crs EPSG:3005`, `--allow-runs`, `--allow-agent`,
the exact block geometry, and the AOI land-base underlay.

The service binds loopback only. ws4 has no authentication; do not expose it
without a trusted proxy. MapLibre projects the EPSG:3005 geometry to WGS84 in
the browser.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Agent operating contract and project-specific rules |
| `ROADMAP.md` | Phases, tasks, and GitHub issue map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `config/` | FEMIC run profile, TSA targets, TIPSY scaffold, Patchworks export config |
| `data/source/aoi/` | Tracked public AOI boundary |
| `scripts/` | AOI, build, calibration, schedule, UI and serve scripts |
| `docs/` | Sphinx site and RTFM surface |
| `notes/` | AOI decisions, reference notes and reports |
| `tests/` | Unit and contract tests |

## Public-data boundary

This repository is public. Do not add raw private financial spreadsheets,
private tenure data, credentials, or machine-specific paths. The public model
uses published BC data and public cost/price bases.

## License

MIT. See `LICENSE`.
