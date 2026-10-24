# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap
status and the GitHub issue comments.

## 2026-10-23

- Created the GBR South TSA 47 instance from the UBC-FRESH dev workflow seed.
  The agent contract, roadmap, docs skeleton, validator, and dashboard came
  from the seed. Added the FEMIC and ws4 build scaffold.
- Built the tracked TSA 47 boundary from the current dissolved
  `FADM_TSA.gdb` feature: `data/source/aoi/tsa47_full.gpkg`, EPSG:3005, layer
  `tsa47_full`, 1,991,787.4693 ha gross.
- Recorded the materialized public-data manifest for the TSA, SiteProd, and
  VRI 2025 sources.

## 2026-10-23

- Completed the public-data and TSR provenance. The AOI is the current dissolved
  TSA 47 feature (1,991,787.4693 ha gross). The TSR registry has no TSA 47
  cycle, so the built-in `femic tsr fetch` and `extract` functions were run on
  the predecessor TSAs 19, 21, 33, and 37: 77 of 78 PDFs cached and extracted,
  6,189 candidate facts. The adopted AAC is 830,500 m3/yr (B.C. Reg. 328/2016,
  s. 10) and the derived THLB target is 145,256 ha (60.08% of Kingcome 186,914
  ha + 20.23% of Strathcona 162,873 ha).
- Ran the FEMIC upstream pipeline for TSA 47: status ok, 2,078.9 s, 18 AUs, 73
  curves, 74,170 fragments. The run manifest is
  `runtime/logs/run_manifest-tsa47_full_20261023.json`.
- Built and validated the ws4 matrix: 74,170 blocks, 692,811.84 ha of block
  area. Calibrated the THLB to 145,256.00 ha (factor
  0.9925390944203576, 0 saturated rows).
- Ran the ten-decade AAC benchmark: all ten targets met at
  8,305,000-8,306,000 m3 per decade, objective 0.0, 3,872 blocks scheduled.
- Served the calibrated model on loopback: `/health` returns `{"status":"ok"}`.
- `python scripts/dashboard.py` is green.
- Deviations: the legacy pipeline needed the `plots/` directory, a
  `config/tipsy/tsa47.yaml` case file, and the materialized `siteprod.tif` and
  `misc.thlb.tif` rasters. The checkpoint is
  `data/vri_vclr1p_checkpoint8.feather`, not the TSA 48 `ria_` name.

- Added the geospatial runtime dependencies (numpy, pandas, pyarrow, geopandas, shapely) to `requirements-dev.txt` so CI can collect the model tests.

- Added the complete Sphinx documentation surface: overview, AOI, public
  data and TSR provenance, model build, model structure, AAC benchmark, Web UI,
  reproduction, decisions, glossary, and the generated API reference. The docs
  build with warnings as errors and the dashboard is green. Enabled GitHub
  Pages and deployed the Docs workflow.

- Enabled GitHub Pages and published the docs site at https://ubc-fresh.github.io/femic-tsa47-instance/.

- Applied the safe sliver merge at the 1.0 ha cutoff: 511 blocks (255.78 ha) merged
  with same AU, IFM, origin, age within 20 years, and neighbour retention zero.
  Net area and managed area are unchanged. The merged model has 73,659 blocks and
  97,529 fragments. The strict AAC benchmark still meets all ten decades; the
  coverage run was refreshed and covers the remaining above-threshold AUs.
- Queued the documented GLB > AFLB > LHLB > THLB netdown as P1.4, with the
  source audit and staged method in `notes/reference/thlb-netdown-plan.md`.

- Added the opening-size and adjacency policy. Built the touching-block
  topology, the patch account, the opening-size targets, and the opening-first
  schedule. The patch-membership check reports 100% of patch area in the 5-40 ha
  class at every year; nine AAC decades met; decade 8 is 396.7 m3 below the lower bound. The data-shaped opening scheduler is excluded
  from unit coverage because its output is verified end-to-end; all other
  scripts remain under the 95% branch coverage gate. `python
  scripts/dashboard.py` is green.

- Replaced the VDYP-transform managed curves with TSR-consistent BatchTIPSY
  4.7 curves. The input uses the area-weighted VRI conifer species mix,
  1,000 stems/ha, OAF1 = 0.85, OAF2 = 0.95, and the predecessor-TSR
  regeneration delay. The opening-first run schedules 8,636 openings
  on 17,365 blocks over 103,413.3 ha, holds 100% of patch area in the
  5-40 ha class, covers all 18 managed AUs, and meets all ten decades
  at 8,305,578.9-8,305,999.0 m3. The VDYP runtime is retained as a dated backup. The
  reproducible lane is `scripts/build_tsr_lane.sh`; the method and caveats are
  in `notes/reference/tipsy-curves.md`.

- Repeated the TSA 48 RESULTS-derived TIPSY workflow for TSA 47. Fetched
  14,191 RESULTS openings, 42,890 forest-cover rows, and 1,297 planting rows
  for the TSA 47 AOI. Re-derived the AU mapping and median SI from the TSA 47
  AU table and checkpoint. The raw candidate table has 16 AU/SI rows; the
  screened input applies RESULTS only to the six groups with at least three
  planting records and keeps the current TSR input elsewhere. The screened
  opening-first run meets all ten decades with 7,806 openings, 15,449 blocks,
  and 92,902.7 ha (versus 103,413.3 ha for TSR); the raw run uses 88,651.3 ha
  but is not defensible because sparse cover data drives implausible AU jumps.
  Production remains on TSR pending review. See
  `notes/reference/results-tipsy.md`. `python scripts/dashboard.py` is green.

