# TSR-consistent BatchTIPSY curves: TSA 47

Date: 2026-10-24
Status: production managed-curve lane; VDYP-transform run retained as a dated
backup at `runtime/tsa47_full_vdyp_20261023`.

## Why this lane exists

The first lane used `managed_curve_mode: vdyp_transform`. That transform scaled
the natural VDYP curves and was not an accepted TIPSY yield. It also carried
the VRI volume-adjustment factor into the BatchTIPSY `OAF1` field. The
predecessor TSRs use OAF1 = 0.85, and that correction alone changes managed
volume by about one third.

## TSR assumptions

- Source TSRs: Kingcome TSA TSR 3 Data Package (2010, Tables 47-48) and Strathcona TSA TSR 3 Data Package (2005, Table 21).
- Future stands regenerate to the existing analysis-unit species composition.
  The mix is area-weighted from the calibrated VRI checkpoint and restricted to
  conifers. Up to three species are carried.
- Stem density: 1,000 stems/ha. This is the TIPSY cap for North Coast
  natural regeneration (TSA 46) and the Kingcome planted density (TSA 47).
- OAF1 = 0.85 and OAF2 = 0.95.
- Regeneration delay: 1 year.
- The AU-level inventory site index is applied to every planted species, because
  the AU table has one site-index value per AU rather than species-specific
  values.

These are **predecessor-TSR assumptions**, not a reviewed GBR yield table. TSA
47 has no dedicated provincial TSR cycle.

## Lane

1. `scripts/build_tsr_tipsy_input.py` derives the species mix and writes the
   BatchTIPSY input.
2. `scripts/run_tsr_tipsy.py` runs BatchTIPSY 4.7 under the Wine/Xvfb lane and
   parses the transposed output. The 18 AUs produce 648 long
   curve rows (ages 0-350 in ten-year steps).
3. `scripts/build_tsr_bundle.py` interpolates the curves to annual ages 1-300
   and replaces only the treated curves in a bundle copy.
4. `scripts/build_full_tsa47_model.sh` exports Patchworks, merges safe
   slivers, compiles the ws4 matrix, and writes the UI geometry.
5. The opening-first schedule is built with the touching-block topology and
   simulated with the patch account.

Command:

```bash
export FEMIC_BTC_WINEPREFIX=/path/to/wineprefix-mono
export FEMIC_BTC_DISPLAY=:99
TSA=47 bash scripts/build_tsr_lane.sh
```

The BatchTIPSY install and Wine prefix are not committed. See
`runbooks/tipsy-btc-linux-wine.md` in the North Island instance for the
one-time setup.

## Result

- Managed AUs: 18
- Topology edges: 104,350
- Openings: 8,636
- Scheduled blocks: 17,365
- Scheduled area: 103,413.3 ha
- Opening range: 5.0-40.0 ha
- Patch area: 218,872.3 ha
- Patch classes: 100% in the 5-40 ha class at every year
- Ten-decade AAC: 8,305,578.9-8,305,999.0 m3, all ten inside 8,305,000-8,306,000 m3
- Calibrated managed area: 145,256 ha
- Harvest coverage: all 18 managed AUs covered

## Caveats

- The species mix is a VRI-derived regeneration assumption, not an operational
  prescription.
- The uniform site index across species is a simplification.
- Genetic gain is not applied.
- The opening-first schedule is a deterministic seed, not an optimized plan.
- The BatchTIPSY output is only as good as the AU definitions and TSR
  assumptions above.

## Related

- `notes/reference/opening-policy.md`
- `notes/reference/tsr.md`
- `notes/reference/ws4-build.md`
- `config/tipsy/tsa47.yaml`
