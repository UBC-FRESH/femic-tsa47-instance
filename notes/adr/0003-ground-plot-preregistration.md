# ADR 0003: Managed/young ground-plot validation is data-limited

Status: accepted
Date: 2026-10-25
Issues: UBC-FRESH/ws4#335

## Context

P48 retained the production TSR-consistent BatchTIPSY curves because the
existing ground plots could not separate species, age, site index, density, and
management origin. P49 asked whether a confirmatory test is possible from the
public FAIB data.

The inventory covers 351 sites and 572 visits in TSA 47:

- 30 PSP sites (3 PSP_G natural, 27 PSP_R experimental).
- 321 non-PSP sites (16 CMI, 8 NFI, 281 VRI, 16 YSM).
- 35 remeasured sites and 161 sites with a visit age 5-80.
- The only remeasured non-PSP program is NFI (7 sites, 5 young).

The public schema has no management-origin field. `SAMPLE_ESTABLISHMENT_TYPE`
names the plot program; `OWNER`, `OWN_SCHED_DESCRIP`, and `MGMT_UNIT` describe
ownership and tenure; `SAMPLE_SITE_PURPOSE_TYPE_CODE` is not documented as a
management-origin flag. No header, visit, or tree field records planting,
clearcut, or treatment origin.

The pre-registered test requires 30 independent remeasured sites in each of four
Cw/Hw 16-50 and 51-80 strata (120 sites total), all with documented management
origin and at least two measurements. TSA 47 has zero eligible sites.

## Decision

Do not run the confirmatory managed/young test. Retain the production
TSR-consistent BatchTIPSY curves and do not change the AAC.

The inventory is data-limited, not result-limited: the missing field is
management origin, and the remeasured candidates are natural (PSP_G),
experimental (PSP_R), or origin-unknown (NFI). Reclassifying a plot program as
managed would be an undocumented assumption. Reusing the P48 rows would make the
test exploratory, not confirmatory.

The pre-registered protocol is recorded in
`docs/ground-plot-preregistration.rst`. It fixes the target population,
exclusions, four strata, minimum sample, metrics, decision rule, and stopping
rule before any correction is fitted. A future phase must acquire remeasured
managed/young Cw and Hw plots with origin metadata, or record a permanent
data-limit decision.

## Consequences

- Production remains reproducible on the accepted curve lane.
- The data gap is explicit: no public management-origin field and no eligible
  remeasured managed/young sample.
- The next step is data acquisition, not curve fitting or AAC tuning.
- A desk reclassification of PSP_G, PSP_R, VRI, CMI, NFI, or YSM is not accepted
  as a substitute.
- No optimality or AAC-sustainability claim follows from this decision.

## Alternatives considered

- **Treat CMI purpose code M as managed.** Rejected: the public schema does not
  define M as management origin, and CMI sites are single-visit in this extract.
- **Use PSP_G natural plots.** Rejected: unmanaged old growth is not a
  managed-clearcut benchmark.
- **Use PSP_R experimental plots.** Rejected: treatments are not recorded well
  enough to define a common target population.
- **Use VRI audits.** Rejected: VRI is an inventory audit, not a remeasured
  managed plot.
- **Reuse the P48 rows.** Rejected: those rows are exploratory and cannot serve
  as confirmation.
- **Lower the minimum sample to force a result.** Rejected: it would manufacture
  precision the data do not have.
