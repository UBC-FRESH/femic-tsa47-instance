# ADR 0002: Ground-plot validation retains the production curves

Status: accepted
Date: 2026-10-25
Issues: UBC-FRESH/ws4#324

## Context

P48 reconciles the independent FAIB/Nemora ground-plot compilation against the
production TSR-consistent BatchTIPSY curves. The purpose is to test whether the
public plots support a volume, DBH, height, or stems correction, not to tune the
curves to the AAC.

TSA 47 has a larger but mixed sample:

- 506 matched rows from 130 sites and 132 clusters.
- 480 VRI, 11 YSM, 8 NFI, and 7 CMI rows.
- Median age 70.5 years.
- VRI plots are inventory audits, not remeasured PSP/CMI plots. The managed and
  young subset is only 26 rows.

The overall matched sample has a volume bias of -49.6 m3/ha (-10.0%), a DBH bias
of -4.3 cm (-13.6%), a height bias of -1.2 m (-4.6%), and a stems bias of
-110.8 sph (-14.7%). The VRI subset has a smaller volume bias (-45.6 m3/ha,
-9.1%) than the managed/young subset (-122.6 m3/ha, -27.7%). The managed/young
subset also has a DBH bias of -3.0 cm (-11.3%), a height bias of -2.5 m
(-10.6%), and a stems bias of -253.2 sph (-30.1%).

The signal is real but not separable: species, age, site index, establishment
density, and management origin are confounded. Cw and Hw carry most of the
volume gap; Ba and Fd are close to neutral. Volume bias is worst at ages 51-80
(-27%) and near neutral at 81-200 (+1%), but DBH remains low at 81-200 (-16%).
The earlier managed-SI and density experiments improve some cells and
overcorrect others; they do not justify a production switch.

## Decision

Retain the production TSR-consistent BatchTIPSY curves. Do not apply a global,
species-level, or age-level correction from this sample, and do not change the
AAC.

The VRI audit and the small managed/young subset both underpin the direction of
the gap, but they answer different questions. A VRI audit is not a remeasured
managed plot, and the 26-row managed/young subset is too small to separate
origin, density, and site index. A correction fitted to the aggregate would
overcorrect the old-age VRI rows or the neutral Ba/Fd cells.

Treat the stratified table as a monitoring and triage signal. A future curve
change requires an independent remeasured managed/young sample large enough to
separate species, age, site index, and management origin, plus a new ADR.

## Consequences

- Production remains reproducible on the accepted curve lane.
- The model's volume and DBH uncertainty is documented rather than hidden.
- The managed/young underprediction is now recorded with sample sizes rather
  than as an unsupported aggregate.
- More remeasured managed/young Cw and Hw plots in the 16-80 age range are the
  priority for a future test.
- No optimality or AAC-sustainability claim follows from this decision.

## Alternatives considered

- **Apply a global volume multiplier.** Rejected: it would help the managed
  sample but overcorrect the VRI audit and the neutral Ba/Fd cells.
- **Apply a species-specific correction.** Rejected: Cw and Hw differ from Ba
  and Fd, but the sample is dominated by Hw and VRI, and the managed subset is
  too small to separate species from origin.
- **Switch to managed-site-index curves.** Rejected for production: the earlier
  comparison improves managed/young volume and DBH but overcorrects the VRI
  audit, and volume/DBH are still not independently validated.
- **Scale establishment density.** Rejected: the density diagnostic reduces the
  YSM stem gap but worsens DBH and overcorrects VRI stems.
- **Wait for a perfect sample.** Rejected: the limitation is recorded now, and
  the production lane remains the accepted benchmark until stronger evidence
  arrives.
