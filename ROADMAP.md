# FEMIC Great Bear Rainforest South TSA 47 Instance Roadmap

This roadmap is the plan of record for the GBR South TSA 47 model instance.
Keep it in step with `CHANGE_LOG.md`, `notes/`, and the GitHub issues.
`scripts/check_workflow.py` parses the phase headers, status lines, and
checkboxes below.

The build is one coherent deliverable: a public, reproducible FEMIC-to-ws4
instance with a served model. It is one phase with six tasks.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Build the instance | #1 | `feature/p0-build` | active |

## Phase 0: Build the instance

Parent issue: #1
Branch: `feature/p0-build`
Status: active

Goal: establish the public instance, rebuild the TSA 47 inputs with FEMIC,
compile and serve the ws4 model, and record the AAC benchmark.

- [ ] P0.1 Bootstrap the seed contract and FEMIC/ws4 scaffold (#2)
- [ ] P0.2 Build the AOI and record the public-data and TSR provenance (#3)
- [ ] P0.3 Run the FEMIC upstream pipeline (#4)
- [ ] P0.4 Export the Patchworks interchange package and build the ws4 matrix (#5)
- [ ] P0.5 Calibrate the THLB and run the ten-decade AAC benchmark (#6)
- [ ] P0.6 Serve the model, verify the UI, and close out (#7)

Acceptance criteria:

- `python scripts/dashboard.py` is green.
- The tracked AOI is `data/source/aoi/tsa47_full.gpkg`, EPSG:3005, 1,991,787.47 ha gross.
- The FEMIC run manifest records a successful TSA 47 run.
- `ws4 build` and `ws4 validate` pass on the full matrix.
- The calibrated managed area matches the derived 145,256 ha THLB target.
- The ten decade targets hold the published 830,500 m3/yr AAC, or each miss is recorded.
- `/health` returns `{"status":"ok"}` and the UI shows the TSA 47 AOI.
- No private data, credentials, or machine-specific paths are tracked.

## Detailed Next Steps Notes

1. Create the GitHub repository and the P0 parent issue. This needs maintainer approval.
2. Activate P0 by setting its parent issue number and its status to `active`, here and in the tracker map.
3. Build the AOI, manifest, and TSR provenance in P0.2 before the long FEMIC run.
4. Run the FEMIC upstream pipeline in P0.3; the run is the expensive step.
5. Export and build the ws4 matrix in P0.4.
6. Calibrate the THLB and run the AAC benchmark in P0.5.
7. Serve and verify the model in P0.6, then write the close-out report.
