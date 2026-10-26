# FEMIC Great Bear Rainforest South TSA 47 Instance

Public FEMIC and ws4 model instance for the Great Bear Rainforest South TSA 47
area of interest. FEMIC rebuilds the inventory and yield curves from public BC
data; ws4 compiles the model, runs the benchmark, and serves the web UI. This
repository is tracked in `femic` as the `external/femic-tsa47-instance`
submodule.

Terms are defined in the [glossary](https://ubc-fresh.github.io/femic-tsa47-instance/glossary.html).

## Runtime lane

**ws4 is the primary runtime.** The Patchworks XML/fragments package is an
interchange input to `ws4 build`, not the runtime lane.

## Related instance

This repository is deliberately related to
**[`UBC-FRESH/femic-tsa46-instance`](https://github.com/UBC-FRESH/femic-tsa46-instance)**,
the Great Bear Rainforest North TSA 46 model. They share the same public
inventory, FEMIC export lane, and GBR legal framework, but they are
**independent datasets and runtimes**:

- this repository owns the GBR South boundary, AAC, THLB, and benchmark;
- `femic-tsa47-instance` owns the GBR South boundary, AAC, THLB, and benchmark;
- neither repository requires the other to build or run.

## Status

The calibrated model is built and the ten-decade benchmark meets all ten
targets at 830,500 m3/yr. A safe sliver merge removed 511 blocks (256 ha)
without changing net area or managed area. The FEMIC run, ws4 matrix, benchmark,
and UI geometry are recorded in `notes/reference/ws4-build.md`. The managed curves are TSR-consistent BatchTIPSY 4.7 curves, not a VDYP
transform. The opening-first policy holds 100% of patch area in the 5-40 ha
class and all ten AAC decades met; see `notes/reference/opening-policy.md` and
`notes/reference/tipsy-curves.md`. The first independent height validation is recorded in `notes/reference/tipsy-validation.md`; TSR bias is `-0.55 m` with MAE `1.38 m`.

## AOI

The tracked boundary is `data/source/aoi/tsa47_full.gpkg` (EPSG:3005, layer
`tsa47_full`, **1,991.8 thousand ha gross**). It is the single current dissolved
FADM TSA 47 feature: no supply-block code and no retirement date. The gross area
includes ocean and foreshore; the VRI block area is the forested subset.

## Model

The calibrated model has **73,659 blocks**, **692.8 thousand ha** of block area,
and **145.3 thousand ha** of managed area. The calibration factor is
`0.993`; 0 rows saturate.

The production model is built by `scripts/build_tsr_lane.sh`:

```bash
TSA=47 bash scripts/build_tsr_lane.sh
```

The script exports the FEMIC inventory, compiles and validates the ws4 matrix,
builds the baseline schedule, simulates and reports the run, and writes the
exact UI geometry and land-base underlay.

## Benchmark

`config/targets.tsa47_full.yaml` carries ten per-decade targets with an
**8,305,000–8,306,000 m3** band around the published **830,500 m3/yr** AAC
(B.C. Reg. 328/2016, effective January 1, 2017). The `opening_first` run meets
all ten decades and covers all 18 managed AUs.

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
| `ROADMAP.md` | Project status and issue map |
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
