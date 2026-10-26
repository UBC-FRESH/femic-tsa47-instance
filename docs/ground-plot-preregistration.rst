Ground-plot validation pre-registration
=======================================

Purpose
-------

An earlier ground-plot check found that the existing ground plots under-predict
volume, DBH, and stems,
but the sample cannot separate species, age, site index, density, and management
origin. This check asks a narrower question: do the public FAIB data contain an
independent remeasured managed/young sample large enough for a confirmatory test?

This page fixes the test before any correction is fitted. The accepted decision
is ADR 0003: the public data are **data-limited**, so no confirmatory test was run
and production remains on the TSR-consistent BatchTIPSY lane.

Candidate inventory
-------------------

The inventory counts sites, visits, remeasured sites (two or more visits), and
young sites (any visit age 5-80). It does not call a plot managed unless a
management-origin field says so.

TSA 47
~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 12 12 10 10 14 10 14

   * - Source
     - Sample type
     - Sites
     - Visits
     - Remeasured
     - Young
     - Age known
   * - PSP
     - PSP_G
     - 3
     - 7
     - 1
     - 0
     - 6
   * - PSP
     - PSP_R
     - 27
     - 237
     - 27
     - 21
     - 204
   * - NONPSP
     - CMI
     - 16
     - 16
     - 0
     - 5
     - 15
   * - NONPSP
     - NFI
     - 8
     - 15
     - 7
     - 5
     - 15
   * - NONPSP
     - VRI
     - 281
     - 281
     - 0
     - 114
     - 275
   * - NONPSP
     - YSM
     - 16
     - 16
     - 0
     - 16
     - 16
   * - **Total**
     - **All**
     - **351**
     - **572**
     - **35**
     - **161**
     - **531**

The total includes 30 PSP sites and 321 non-PSP sites. The
young column counts sites with at least one visit aged 5-80; it does not imply
that the stand is managed.

Species coverage
~~~~~~~~~~~~~~~~

The earlier matched sample contains Ba (25 rows), Cw (100), Fd (42), Hm (2), and Hw
(337). These are exploratory matched rows, not candidate counts; they show that
Cw and Hw are present, but the absent origin field prevents selecting a managed
subset.

Field audit
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 14 56

   * - Field
     - Available
     - Use and limitation
   * - ``SAMPLE_ESTABLISHMENT_TYPE``
     - Header
     - Plot program (PSP_G, PSP_R, CMI, NFI, VRI, YSM). Not a management-origin flag.
   * - ``OWNER``, ``OWN_SCHED_DESCRIP``, ``MGMT_UNIT``
     - Header
     - Ownership and tenure. Not a silviculture or clearcut-origin flag.
   * - ``SAMPLE_SITE_PURPOSE_TYPE_CODE``
     - Visits
     - Purpose code. ``M`` appears for CMI, but the public schema does not define it as management origin.
   * - ``FIRST_MSMT``, ``LAST_MSMT``, ``PERIOD``, ``TOTAL_PERIOD``
     - Visits and header
     - Remeasurement history. Usable for the sample frame.
   * - ``PROJ_AGE_ADJ``, ``PROJ_AGE_1``
     - Visits
     - Projected age. Usable, but age alignment with TIPSY remains an assumption.
   * - Planting, clearcut, or treatment origin
     - **Absent**
     - The blocking gap. No header, visit, or tree field records management origin.

The public compilation therefore cannot tell a managed/young stand from a natural
or experimental plot without an assumption. Treating ``SAMPLE_SITE_PURPOSE_TYPE_CODE = M``
as managed would be an undocumented assumption, not a measurement.

Pre-registered test
-------------------

The protocol below is fixed before the confirmatory run. Those rows are
exploratory and cannot be reused as the confirmatory sample.

**Target population.** Remeasured, managed-origin, single-leading-species Cw or
Hw stands in TSA 47, aged 16-80 at measurement, with a model AU match, volume
and stems at the 12.5 cm utilization limit, and DBH from the compiled plot
summary.

**Strata.** Four cells: Cw 16-50, Cw 51-80, Hw 16-50, Hw 51-80.

**Minimum sample.** At least 30 independent remeasured sites per stratum (120
sites total). Every site must have a documented management origin and at least
two measurements. Natural PSP_G, experimental PSP_R, VRI audits, single-visit
plots, mixed stands, and unknown-origin plots are excluded.

**Metrics.** Volume, DBH, height, and stems; signed bias, MAE, RMSE, and relative
bias; 95% bootstrap confidence intervals; sample size for every cell.

**Decision rule.** A curve change requires all of the following:

1. The minimum sample is met in all four strata.
2. The volume-bias direction is consistent across Cw and Hw.
3. The 95% confidence interval excludes zero in both species.
4. A pre-specified correction improves held-out MAE for both volume and DBH.
5. A new ADR accepts the change.

**Stopping rule.** Do not pool VRI, PSP_G, PSP_R, or single-visit plots to reach
the minimum. Do not reuse those rows as confirmation. Do not tune to the AAC.

Decision
--------

The inventory finds **zero eligible sites**: none of the candidate sites has a
documented management origin, and the remeasured candidates are natural
(PSP_G), experimental (PSP_R), or origin-unknown (NFI). The four-strata minimum
is therefore not met.

No confirmatory test was run. ADR 0003 records the data limit and retains the
production TSR-consistent BatchTIPSY curves. No volume, DBH, height, stems, or
AAC change follows.

The next step is data acquisition: remeasured managed/young Cw and Hw plots with
management-origin metadata. A desk reclassification of existing plot programs is
not a substitute.

Reproduce
---------

The inventory table is ``config/tsr/ground_plot_candidates.tsa47.csv`` and is
regenerated from the public FAIB header and visit tables:

.. code-block:: bash

   python scripts/inventory_ground_plot_candidates.py \
     --tsa 47 \
     --psp-header data/downloads/psp/faib_header.csv \
     --psp-visits data/downloads/psp/faib_sample_byvisit.csv \
     --nonpsp-header data/downloads/non_psp_gbr_south_tsa_hps/faib_header.csv \
     --nonpsp-visits data/downloads/non_psp_gbr_south_tsa_hps/faib_sample_byvisit.csv \
     --out config/tsr/ground_plot_candidates.tsa47.csv

The raw FAIB downloads are public BC data and are not committed.
