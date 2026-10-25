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

- Added the first independent TIPSY height validation for TSA 47. Compared
  TIPSY height at age with 3,472 observed immature single-species RESULTS
  cover rows. Current TSR: bias -0.55 m, MAE 1.38 m, RMSE 2.53 m. RESULTS
  screened: bias -0.34 m, MAE 1.36 m, RMSE 2.48 m. The dominant CWH_HW H young
  stands are close; CWH_HW M is the weakest well-sampled cell. This is a
  height-only check and does not use the AAC target. See
  `notes/reference/tipsy-validation.md`.

- Documented the independent height validation in `docs/benchmark.rst`,
  `docs/decisions.rst`, `docs/model-build.rst`, `docs/reproduce.rst`, the
  README, and `notes/reference/`. Added observed SI and the checkpoint SI gap
  to the validation table. The dominant height bias is largely a site-index
  input issue: TSA 46 CWH_HW H observed 23.0 m versus checkpoint 16.3 m; TSA 47
  CWH_HW H observed 28.0 m versus checkpoint 26.3 m. The next test is an
  SI-stratified managed-land curve validated on held-out stands, not tuning to
  the AAC.

- Ran a holdout managed-SI experiment. Training 80% of observed openings to estimate managed-stand SI and validated on the held-out 20%, holding species and density at the current TSR input. TSA 46: TSR bias -0.56 m, MAE 1.52 m, RMSE 3.06 m; managed SI bias +0.13 m, MAE 1.60 m, RMSE 3.04 m. TSA 47: TSR bias -0.56 m, MAE 1.52 m, RMSE 3.06 m; managed SI bias +0.13 m, MAE 1.60 m, RMSE 3.04 m. Bias improves, but MAE gets slightly worse and RMSE is essentially unchanged. TSR is already close; managed SI overcorrects TSA 47. No production curve or AAC target was changed. See `notes/reference/tipsy-validation.md`.

- Recorded the volume/DBH data limitation for TSA 47: RESULTS basal area is mostly a 1.0 placeholder, and the public PSP layer is active plot locations only, not remeasured measurements. Height validation remains the available accuracy check; production stays on TSR.

- Found the public FAIB ground-plot compilation (PSP/CMI) with plot/tree volume, QMD, stems, age, and top height. TSA 47: 30 sites, 244 visits, 1,217 volume/DBH rows, 410 height rows (3 natural, 27 experimental). Added BTC `stand-structure-basic` support so DBH and stems can be emitted. Volume/DBH validation is now a defined next step, not a data-absence blocker.

- Ran the first Nemora-backed managed/young-stand validation on GBR South non-PSP plots. `nemora ingest-faib-hps` prepared 1,284 plots / 8,255 live trees; 365 VRI, 11 YSM, 4 CMI, and 6 NFI rows matched a TIPSY AU. VRI shows underprediction: volume bias -75.3 m3/ha (MAE 138.8), DBH -2.6 cm, height -1.7 m, stems -158.7 sph. DBH is approximate because TIPSY all-stem QMD is compared with 12.5 cm PSP QMD. VRI is an audit sample, not remeasured PSP/CMI; YSM/CMI/NFI are stronger but small. Production remains on TSR. See `notes/reference/tipsy-validation.md`.

- Expanded the Nemora ground-plot validation to the full non-PSP set. TSA 47 has 506 matched observations; VRI n=480, volume bias -45.6 m3/ha (MAE 151.7), DBH -4.4 cm, height -1.2 m, stems -103.1 sph. TSA 46 has 20 matched observations (CMI 8, NFI 6, YSM 6), still too sparse to quantify. Added `scripts/validate_tipsy_ground_plots.py` and tests; the table is reproducible from the Nemora HPS manifest and FAIB compiled summaries. See `notes/reference/tipsy-validation.md`.

- Upstreamed the non-PSP FAIB plot-id fix to Nemora (PR #5). HPS ingest now preserves string plot codes (`I/W/E/N/S`) instead of forcing integer ids. Direct ingest of the 105-plot GBR North set was verified without the staged code-to-index workaround.

- Diagnosed the TSA 47 ground-plot underprediction. VRI volume bias is concentrated at ages 16-80 (-23% to -27%) and is unbiased at 81-200 (+2%); CWH_HW L (-53%) and CWH_CW L (-37%) are the worst cells, while CWH_FD H overpredicts (+12%). YSM young stands are under-dense (observed 675 stems/ha vs predicted 365), with volume -28%, DBH -21%, and height -13%. This points to density/mortality, establishment, and management-origin questions, not a global yield correction. See `notes/reference/tipsy-validation.md`.

- Compared current TSR and managed-SI curves against the independent TSA 47 ground plots. Managed SI improves volume/DBH/height for YSM (volume -44.5 to +9.3 m3/ha; DBH -4.0 to -1.4 cm), CMI, and NFI, but overcorrects VRI audits (volume -45.6 to +49.7). Stems barely change (YSM -276.8 to -181.0 sph; VRI -103.1 to -107.4). This supports an origin split between managed/young stands and VRI audit/average stands, not a global SI correction. Production remains on TSR. See `notes/reference/tipsy-validation.md`.

- Ran the P1.8 density diagnostic for TSA 47. Scaling initial density for the managed-sample AUs from 1.0x to 1.5x/2.0x reduces the YSM stem bias from -276.8 to -99.3 sph and volume bias from -44.5 to -30.0 m3/ha, but worsens DBH from -4.0 to -6.4 cm and leaves height unchanged. VRI audits overcorrect from -103.1 to +97.8 sph. Density is a partial lever, not a clean correction; mortality/ingrowth and establishment composition remain. No production change or AAC tuning. See `notes/reference/density-diagnostic.md`.

- P35: track `config/dataset_quality.yaml`, copy it beside the matrix after `ws4 build`,
  and gate the full model build with `ws4 quality --check`. The docs link the model
  limitations page and the VDYP/THLB caveats.

- P36: the FreshForge workflow adds `femic.ws4_quality` after dataset validation. It copies
  `config/dataset_quality.yaml` and fails the workflow when `ws4 quality --check` is not ok.

- P38: package the `tsa47.ws4` FreshForge provider with build, validate, baseline-schedule,
  and simulate nodes; add the entry point and command tests. The workflow now resolves its
  instance nodes through the installed provider.

- P40: add `workflows/freshforge/tsa47_ws4_smoke.yaml` and
  `scripts/run_provider_smoke.py`. The bounded graph validates the matrix, gates provenance,
  builds a baseline schedule, and simulates one year from an existing matrix.

- P41: add a tiny provider-smoke fixture, `requirements-freshforge.txt` pinned to the FEMIC/ws4
  commits, and a CI job that runs the build → validate → provenance → schedule → simulate graph
  and uploads the evidence JSON.

- P47: record the accepted model boundary in `notes/adr/0001-model-boundary.md` and add a
  `docs/limitations.rst` page linked from the index, model-build guide, and decisions page.
  Correct the provenance sidecar to name the TSR-consistent BatchTIPSY managed curves and
  point at the instance limitations URL. Normal quality gates remain green.

- P48: reconcile the ground-plot sample, add `docs/ground-plot-validation.rst` and the
  stratified summary script/tables, and record ADR 0002. Production TSR curves are retained;
  TSA 47 does not justify a curve or AAC change. The sidecar and limitations page name the
  sample limit.

- P49: inventory 47 FAIB/CMI/PSP candidates, add
  `docs/ground-plot-preregistration.rst`, and record ADR 0003. The public data have no
  management-origin field; the four-strata managed/young test is data-limited (zero eligible
  sites), so production curves and the AAC remain unchanged.
