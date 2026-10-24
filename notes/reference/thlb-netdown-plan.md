# THLB netdown plan: TSA 47

Status: queued. The current THLB target is a predecessor-value derivation; this
task replaces it with a documented **GLB > AFLB > LHLB > THLB** netdown.

Date: 2026-10-24
Current target: 145,256 ha
Published AAC: 830,500 m3/yr

## Why this task exists

The current model calibrates a proportional per-stand THLB signal to the
predecessor TSR current THLB values. That is transparent and reproducible, but
it is not a reviewed GBR land-base netdown. It does not reproduce the staged
reductions from gross land base to analysis forest land base, legally
harvestable land base, and timber harvesting land base, and it does not apply the
GBR land-use order exclusions that postdate the predecessor TSRs.

The user wants the same documented netdown discipline used in the TSA 29 and
TSA 23 FEMIC instances.

## Source audit

The GBR North and South TSAs have **no dedicated provincial TSR cycle**. Their
current AAC comes from B.C. Reg. 328/2016. The predecessor TSR packages are the
available netdown evidence:

| Predecessor | Code | TSR cycle | Documents |
| --- | --- | --- | --- |
| Kingcome | 33 | TSR 2010 | Data Package (128 pp) and AAC Rationale (61 pp) |
| Strathcona | 37 | TSR 2012 | Data Package (35 pp) and AAC Rationale (43 pp) |

A PDF text audit found THLB references in every predecessor data package and
rationale. The exact acronyms ``AFLB`` and ``LHLB`` are not used in the
predecessor documents; those documents present staged land-base tables using
"Total Area", "Productive Area", "Current THLB", "Future THLB", and the
reduction steps. The GLB/AFLB/LHLB/THLB ladder is the FEMIC organizing grammar,
not a verbatim TSR label.

Examples of the source structure:

- North Coast TSR 2007, Data Package, section 2.1 and Table 2.1: THLB definition
  and staged reductions.
- Mid Coast TSR 2011, Data Package: current and long-term THLB tables; AAC
  rationale records the current effective THLB.
- Kingcome TSR 2010, Data Package, section 5.0 and page 27: current THLB,
  future THLB, and EBM/pre-EBM splits.
- Strathcona TSR 2012, Data Package, section 5.0: staged THLB definition and
  reductions.

These are cached under ``~/.femic/tsr/`` after ``femic tsr fetch``. They are not
committed.

## Boundary apportionment

TSA 47 contains 60.08% of the Kingcome boundary and 20.23% of the Strathcona boundary.

The reviewed netdown must clip the predecessor stand-level netdown checkpoints
to the current TSA 47 boundary and carry area by overlap. The result is a
GBR-specific THLB, not a simple sum of predecessor THLBs.

## Staged method

1. **GLB**: gross land base from the current dissolved TSA boundary, with the
   ocean/foreshore separation recorded explicitly.
2. **GLB -> AFLB**: remove land not administered for TSA timber supply, private
   land, parks and protected areas, tree farm licences, woodlots, community
   forests, Indian Reserves, and other non-TSA tenure. This is where the GBR
   land-use order and the current legal designations enter.
3. **AFLB -> LHLB**: apply legal exclusions: riparian reserve, wildlife habitat
   areas, old-growth management areas, unstable terrain, cultural heritage,
   visual preservation, and other legally reserved areas.
4. **LHLB -> THLB**: apply operational and economic deductions: inoperable
   terrain, low site, non-merchantable types, alder, future roads/trails/
   landings, wildlife tree retention, and EBM constraints.
5. **Reconcile**: compare the resulting THLB with the published AAC partition
   and the predecessor benchmark. Record every step as applied,
   applied_noop, unsupported, or blocked_missing_source.

## Tasks

- P1.4.1 Fetch and extract the predecessor TSR netdown documents (19, 21, 33, 37).
- P1.4.2 Build and review the predecessor THLB netdown recipes with
  ``femic tsr thlb-netdown-build``.
- P1.4.3 Run the stand-level netdown checkpoints for each predecessor.
- P1.4.4 Clip/apportion the predecessor checkpoints to the current TSA 47
  boundary and apply the GBR land-use order exclusions.
- P1.4.5 Reconcile GLB >= AFLB >= LHLB >= THLB and compare to the current
  145,256 ha target and the AAC.
- P1.4.6 Replace the proportional calibration with the reviewed THLB target and
  re-run the AAC benchmark.

## Acceptance criteria

- The netdown ladder reconciles at every stage, with no negative residual.
- Each step has a page-level provenance and an explicit status.
- The final THLB is recorded in ``config/tsr/overlay.yaml`` and
  ``config/tsr/thlb_netdown.recipe.yaml``.
- A validator fails when a stage total is inconsistent or a residual is negative.
- The calibrated model uses the reviewed THLB, not the predecessor sum.
- The AAC benchmark is re-run and all ten decades are met, or each miss is
  recorded with its cause.

## Commands

```bash
python -m femic tsr fetch --tsa 19 --tsa 21 --tsa 33 --tsa 37
python -m femic tsr extract --tsa 19 --tsa 21 --tsa 33 --tsa 37
python -m femic tsr thlb-netdown-build --instance-root .
python -m femic tsr thlb-netdown-run --instance-root .
python -m femic tsr thlb-netdown-workbench-build --instance-root .
```

## Risks and gaps

- The predecessor TSRs predate the 2016 GBR order. A strict reconstruction of
  the current legal THLB may require a GBR-specific overlay that does not exist
  in the predecessor data packages.
- The predecessor documents use different table layouts. The FEMIC parser may
  classify some rows as context rather than a stage; those must stay explicit.
- The current AAC is a legal determination with partitions, not a simple
  residual of the predecessor AACs. Reconcile the land base to the AAC, not the
  reverse.
- The model is volume-only; the THLB netdown does not add adjacency or opening
  constraints.

## Status

Queued. No recipe or checkpoint has been built yet.

## External model lead (2026-10-24)

The GBR timber-supply and land-use analyses appear to use the **SELES Spatial
Timber Supply Model (STSM)**. The public SELES publication list
(`http://gowlland.ca/publications.html`) records:

- Fall, A. 2022. *Great Bear Rainforest Land-Use Order: 2021 Analysis Update
  Memo 1: Timber supply and carbon offset potential based on updated spatial
  information.* Report to the GBR Government-to-Government working group.
- Fall, A. 2022. *GBR Land-Use Order: 2021 Analysis Update Memo 7: Timber supply
  assessment of potential LUO changes to grizzly habitat, Kermode bear
  stewardship areas, red & blue-listed ecosystems and aquatic habitat.*
- Fall, A. 2023. *STSM v2022 (SELES Spatial Timber Supply Model): User
  documentation.* 202pp.
- Fall, A. 2015. *Central-North Coast and South-Central Coast (Great Bear
  Rainforest) Land-Use Order Review Analysis: comparing timber supply and carbon
  offset potential of current land-use orders with proposed JSP scenario.*

These are reports and model documentation, not the GBR TSR model archive. The
standard provincial TSR folder for TSA 46/47 is empty, so the model files are
not in the usual public location.

### Data request list

- The GBR North and GBR South TSR model archive, including the SELES/STSM
  scenario and parameter files.
- The land-base netdown tables and resultant outputs (GLB, AFLB, LHLB, THLB),
  with page-level provenance.
- Stand-level netdown or resultant checkpoints, if they exist.
- AAC partition assumptions and the current THLB by partition.
- SELES/STSM version, seral/adjacency parameters, operability rules, retention
  assumptions, and yield-curve source.
- Appendices to the 2021 LUO update memos that contain the spatial model detail.

### Interim lane

Until the model arrives, P1.4 proceeds on the **reconstructed lane**:
predecessor TSR netdowns clipped to the current GBR boundaries, plus the GBR
land-use order overlay. Label it **reconstructed**, not official. It is also the
comparison target for the official model when it arrives.
