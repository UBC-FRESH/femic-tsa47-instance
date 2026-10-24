AAC benchmark
=============

The benchmark asks whether the model can hold the published AAC across ten
decades. The target account is ``product.Yield.managed.Total`` with a
``period_width`` of 10. Each decade target is ten times the annual AAC.

Targets
-------

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - AAC
     - 830,500 m3/yr
   * - Decade target band
     - 8,305,000-8,306,000 m3
   * - Horizon
     - 100 years
   * - Target file
     - ``config/targets.tsa47_full.yaml``
   * - Run
     - ``runtime/tsa47_full/runs/opening_first``

TSR-consistent curves
---------------------

The managed lane uses BatchTIPSY 4.7 curves, not the earlier VDYP transform.
The input follows the predecessor TSRs: the future stand regenerates to the
existing analysis-unit species composition, with 1,000 stems/ha, OAF1 = 0.85,
OAF2 = 0.95, and a one-year regeneration delay. The species mix is area-weighted
from the calibrated VRI checkpoint. The source TSRs are the Kingcome TSA TSR 3
Data Package (2010, Tables 47-48) and the Strathcona TSA TSR 3 Data Package
(2005, Table 21). The full method is in ``notes/reference/tipsy-curves.md``.

Result
------

.. list-table::
   :header-rows: 1
   :widths: 10 25 14

   * - Decade
     - Realized volume (m3)
     - Band status
   * - 1
     - 8,305,966.0
     - met
   * - 2
     - 8,305,867.1
     - met
   * - 3
     - 8,305,898.7
     - met
   * - 4
     - 8,305,808.5
     - met
   * - 5
     - 8,305,976.7
     - met
   * - 6
     - 8,305,579.0
     - met
   * - 7
     - 8,305,999.0
     - met
   * - 8
     - 8,305,791.8
     - met
   * - 9
     - 8,305,981.9
     - met
   * - 10
     - 8,305,965.6
     - met

All ten decades are inside the band. The opening-first schedule schedules
8,636 openings on 17,365 blocks, covering 103,413.3 ha.

Opening-first policy
--------------------

The opening-size and adjacency policy is applied with a touching-block
topology and a patch account. The account joins only blocks that touch and
uses ``product.Treated.managed.CC`` as the treated-area criterion.

- Topology edges: 104,350
- Opening range: 5.0-40.0 ha
- Patch area: 218,872.3 ha
- Patch classes: **100% in the 5-40 ha class at every year**

The 0-1, 1-5, 40-50 and >50 ha classes are all 0.0%. The opening-first
schedule is a deterministic seed, not a final optimized plan. The full record
is ``notes/reference/opening-policy.md``.

Harvest coverage
----------------

The opening-first schedule covers all 18 managed AUs.
``scripts/check_harvest_coverage.py`` reports no gaps, so the allowlist is
unused. The earlier strict volume-only schedule left small AUs unselected; that
result is retained with the dated VDYP-transform runtime.

RESULTS sensitivity
-------------------

The TSA 48 RESULTS-derived TIPSY workflow was repeated for TSA 47. The raw
candidate table has 16 AU/SI rows, but only six have at least three planting
records. Using the raw table would let sparse cover data drive the result; the
screened scenario applies RESULTS only to those six groups and keeps the
current TSR input for the rest.

.. list-table::
   :header-rows: 1
   :widths: 34 14 14 18

   * - Scenario
     - Openings
     - Blocks
     - Scheduled area
   * - Current TSR
     - 8,636
     - 17,365
     - 103,413.3 ha
   * - RESULTS screened
     - 7,806
     - 15,449
     - 92,902.7 ha
   * - RESULTS raw
     - 7,320
     - 14,585
     - 88,651.3 ha

All three scenarios meet the ten-decade band and hold 100% of patch area in the
5-40 ha class. The screened scenario reduces scheduled area by about 10%
relative to the current TSR lane. It is a sensitivity result, not the benchmark
of record; the raw scenario is an upper bound driven by sparse cover data.

See ``notes/reference/results-tipsy.md`` for the data coverage, AU changes, and
caveats.

Independent height validation
-----------------------------

Area is a consequence of the yield assumptions, not a score. Accuracy is
checked separately by comparing TIPSY height at age with observed RESULTS
forest-cover height for immature single-species stands. The AAC target is not
used in this check.

For TSA 47, 3,472 observations matched a TIPSY AU curve:

.. list-table::
   :header-rows: 1
   :widths: 30 18 18 18

   * - Curve set
     - Bias
     - MAE
     - RMSE
   * - Current TSR
     - -0.55 m
     - 1.38 m
     - 2.53 m
   * - RESULTS screened
     - -0.34 m
     - 1.36 m
     - 2.48 m

The dominant CWH_HW H young stands are close: 2,125 observations, bias -0.33 m
(-8%) at ages 5-15, and -1.76 m (-5.5%) at ages 51-80. CWH_HW M at ages 5-15 is
the weakest well-sampled cell at -1.02 m (-28%). The RESULTS curves are only
marginally closer, and their species inputs are not independent of the observed
cover.

Site-index attribution
~~~~~~~~~~~~~~~~~~~~~~

The CWH_HW H gap is small: observed managed-stand SI is **28.0 m**, while the
checkpoint AU median is **26.3 m**. CWH_HW M is 19.0 m observed versus 17.0 m
checkpoint. The pattern is the same as TSA 46 but much smaller. The next test
is an SI-stratified managed-land curve, validated on held-out stands.

This is a height-only check. Volume, DBH, and mortality still need independent
validation. See ``notes/reference/tipsy-validation.md``.

Baseline versus benchmark
-------------------------

The baseline schedule is a deterministic clearcut-at-age-60 reference. It
harvests every block once and dumps mature stands into the first decade, so it
is not an AAC benchmark. Use it to verify that the dataset and simulator run,
not to judge the AAC.

Rerun
-----

The supported lane is:

.. code-block:: bash

   export FEMIC_BTC_WINEPREFIX=/path/to/wineprefix-mono
   export FEMIC_BTC_DISPLAY=:99
   TSA=47 bash scripts/build_tsr_lane.sh

The BatchTIPSY install and Wine prefix are not committed. See
``notes/reference/tipsy-curves.md`` for the one-time setup. To rerun only the
simulation and report:

.. code-block:: bash

   python -m ws4.cli simulate \
     --dataset runtime/tsa47_full/matrix \
     --schedule runtime/tsa47_full/schedules/opening_first.csv \
     --out runtime/tsa47_full/runs/opening_first \
     --years 100 \
     --topology runtime/tsa47_full/topology.csv \
     --patch-accounts config/patch_accounts.tsa47_full.yaml \
     --patch-membership

   python -m ws4.cli report \
     --run runtime/tsa47_full/runs/opening_first \
     --targets config/targets.tsa47_full_opening.yaml
