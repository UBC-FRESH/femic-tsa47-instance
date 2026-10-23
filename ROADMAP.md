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
| P0 Build the instance | #1 | `feature/p0-build` | complete |
| P1 Harden the model | #9 | `feature/p1-hardening` | active |

## Phase 0: Build the instance

Parent issue: #1
Branch: `feature/p0-build`
Status: complete

Goal: establish the public instance, rebuild the TSA 47 inputs with FEMIC,
compile and serve the ws4 model, and record the AAC benchmark.

- [x] P0.1 Bootstrap the seed contract and FEMIC/ws4 scaffold (#2)
- [x] P0.2 Build the AOI and record the public-data and TSR provenance (#3)
- [x] P0.3 Run the FEMIC upstream pipeline (#4)
- [x] P0.4 Export the Patchworks interchange package and build the ws4 matrix (#5)
- [x] P0.5 Calibrate the THLB and run the ten-decade AAC benchmark (#6)
- [x] P0.6 Serve the model, verify the UI, and close out (#7)

Acceptance criteria:

- `python scripts/dashboard.py` is green.
- The tracked AOI is `data/source/aoi/tsa47_full.gpkg`, EPSG:3005, 1,991,787.47 ha gross.
- The FEMIC run manifest records a successful TSA 47 run.
- `ws4 build` and `ws4 validate` pass on the full matrix.
- The calibrated managed area matches the derived 145,256 ha THLB target.
- The ten decade targets hold the published 830,500 m3/yr AAC, or each miss is recorded.
- `/health` returns `{"status":"ok"}` and the UI shows the TSA 47 AOI.
- No private data, credentials, or machine-specific paths are tracked.

## Phase 1: Harden the model

Parent issue: #9
Branch: `feature/p1-hardening`
Status: active

Goal: close the audit gaps before release.

- [x] P1.1 Add the runtime-signal and harvest-coverage gates (#10)
- [ ] P1.2 Add the opening-size and adjacency policy
- [ ] P1.3 Replace the VDYP transform with accepted TIPSY curves
- [ ] P1.4 Replace the derived THLB with a reviewed GBR netdown
- [ ] P1.5 Release v0.1.0 and verify a clean checkout
- [x] P1.6 Complete the Sphinx docs and publish Pages (#11)

Acceptance criteria:

- The runtime-signal gate passes on the compiled model and the benchmark.
- The harvest-coverage gate passes on the coverage run; remaining zero-harvest AUs are allowlisted with a reason.
- The opening policy is recorded and checked.
- The release passes the dashboard and CI from a clean checkout.

## Detailed Next Steps Notes

1. P1.1 adds the runtime-signal and harvest-coverage gates and records the coverage run.
2. P1.2 adds the opening-size and adjacency policy.
3. P1.3 replaces the VDYP transform with accepted TIPSY curves.
4. P1.4 replaces the derived THLB with a reviewed GBR netdown.
5. P1.5 releases v0.1.0 and verifies a clean checkout.
