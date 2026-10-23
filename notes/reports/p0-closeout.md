# Phase close-out report: P0 Build the GBR South TSA 47 instance

Phase: P0, Build the instance
Parent issue: #1
Pull request: #8
Evidence head: `4543e41`. CI run 40026306802 is green in all three jobs on the code head.
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-23
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge the phase pull request, and delete the branch `feature/p0-build`.
2. Close parent issue #1 with a closeout comment that cites the merge commit.
3. Launch the next phase: accepted TIPSY curves, a reviewed GBR land-base netdown, and the opening-size policy.

Settings changes: none. This phase changes no repository setting, tag, release, or external account.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `python scripts/dashboard.py` is green. | Lint, format, types, tests, validator, and docs are green at `238b64f`. | Met |
| The tracked AOI is `data/source/aoi/tsa47_full.gpkg`, EPSG:3005, 1,991,787.47 ha gross. | `data/source/aoi/tsa47_full.summary.json`: one dissolved feature, EPSG:3005, 1,991,787.4693 ha. | Met |
| The FEMIC run manifest records a successful TSA 47 run. | `runtime/logs/run_manifest-tsa47_full_20261023.json`: status ok, exit 0, 2,078.901 s, tsa_list `["47"]`. | Met |
| `ws4 build` and `ws4 validate` pass on the full matrix. | 74,170 blocks, 692,811.84 ha block area; `ws4 validate` passes. | Met |
| The calibrated managed area matches the derived 145,256 ha THLB target. | `runtime/tsa47_full/evidence/thlb_calibration.json`: 145,256.000 ha, factor 0.9925390944203576, 0 saturated rows. | Met |
| The ten decade targets hold the published 830,500 m3/yr AAC. | `runs/aac_benchmark/report_targets.csv`: all ten decades `met`, 8,305,000-8,306,000 m3, objective 0.0, 3,872 blocks scheduled. | Met |
| `/health` returns `{"status":"ok"}` and the UI shows the TSA 47 AOI. | `curl http://127.0.0.1:8018/health` returns `{"status":"ok"}`; `/` returns 200; `/api/targets` returns 200. | Met |
| No private data, credentials, or machine-specific paths are tracked. | The workflow validator scans the committed files and reports 0 errors. | Met |

## 2. Workflow compliance

- Parent issue before the branch: #1 was created before `feature/p0-build`.
- Branch from `main`: `feature/p0-build` starts at the initial repository commit.
- Commit messages start with task IDs: `P0.1`, `P0.2-P0.6`.
- Gates for each commit: the dashboard is green at the evidence head.
- Roadmap and changelog in step: both record the completed tasks and the evidence.
- Child issues closed with closeout evidence: pending the closeout comments in the recommendation.
- Approval gates: repository creation was explicitly approved. No tag, release, settings change, or private data was touched.

## 3. Gate evidence

| Gate | Result at `238b64f` |
| --- | --- |
| lint | green |
| format | green |
| types | green |
| tests | green (167 tests, coverage gate 95 percent) |
| validator | green |
| docs | green |

CI run 40026306802: Quality gates, Green dashboard summary, and Pre-commit parity all pass on `4543e41`.

## 4. CI evidence

The pull request is not open yet. Its first CI run is posted on the pull request.

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| The first FEMIC run failed because `plots/` did not exist. | The ignore rules keep `plots/` out of git, so the directory was absent. | Created `plots/` and resumed the run. |
| The second FEMIC run failed because `config/tipsy/tsa47.yaml` was absent. | The seed ships only the TIPSY template. | Added a provisional coastal case file; the first lane uses VDYP-transform managed curves. |
| The public data root had unresolved `siteprod.tif` and `misc.thlb.tif` annex pointers. | The annex payload was not materialized. | Materialized both rasters from the sibling annex copy. |
| The checkpoint is `data/vri_vclr1p_checkpoint8.feather`, not the TSA 48 `ria_` name. | The legacy pipeline names the new checkpoint without the `ria_` prefix. | Updated the build script and FreshForge workflow. |
| CI failed on the first PR run because the model tests import numpy, pandas, pyarrow, geopandas, and shapely. | The seed requirements carry only the dev tools, and mypy had no pandas override. | Added the geospatial dependencies to `requirements-dev.txt` and a pandas override to `pyproject.toml`; CI run 40026306802 is green. |

## 6. Next phase

Goal: replace the provisional managed-curve lane and the predecessor-value THLB derivation with accepted evidence.

Tasks:

- P1.1 Accepted TIPSY curve handoff for TSA 47.
- P1.2 Reviewed GBR South land-base netdown and THLB target.
- P1.3 Opening-size and adjacency policy for the benchmark.

Recommended defaults:

- Keep the current VDYP-transform lane as the comparison baseline.
- Keep the derived 145,256 ha target until a reviewed netdown replaces it.
- Add the opening policy only after the TSA-level benchmark is accepted.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
