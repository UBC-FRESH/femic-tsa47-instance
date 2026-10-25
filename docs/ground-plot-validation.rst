Ground-plot validation
======================

Purpose
-------

This page reports the independent FAIB/Nemora ground-plot check for TSA 47. It
tests whether the public plots support a correction to the production
TSR-consistent BatchTIPSY curves. It does not tune the curves to the AAC.

The accepted decision is ADR 0002: the signal is real but the sample cannot
separate species, age, site index, establishment density, and management
origin, so production remains on the TSR-consistent lane.

Sample frame
------------

The validation lane is ``scripts/validate_tipsy_ground_plots.py``. It keeps one
leading species per visit (at least 50% of basal area), requires a single-species
stand, uses the 12.5 cm utilization limit, and matches the plot to a model AU
by BEC zone, leading species, and checkpoint site-index class.

.. list-table::
   :header-rows: 1
   :widths: 18 10 10 16 46

   * - Sample type
     - Rows
     - Sites
     - Median age (yr)
     - Role
   * - CMI
     - 7
     - 7
     - 68.0
     - Continuously measured inventory plots.
   * - NFI
     - 8
     - 6
     - 86.3
     - National forest inventory plots.
   * - VRI
     - 480
     - 106
     - 70.5
     - Inventory audit plots, not remeasured PSP/CMI.
   * - YSM
     - 11
     - 11
     - 26.8
     - Young-stand survey plots.
   * - **Total**
     - **506**
     - **130**
     - **70.5**
     - **132 clusters; 26 managed/young rows.**

The matched sample is not a random audit. Of the 1,284 candidate plots and
8,255 live trees, 130 sites contributed 506 matched rows; the remaining 1,154
candidate plots did not contribute a matched row. The lane does not persist a
reason code for non-matches. The separate PSP/CMI set (30 sites, 244 visits;
3 natural and 27 experimental sites) was excluded as a managed-clearcut
benchmark. VRI dominates the count, while the managed/young subset is only 26
rows. The VRI and managed/young results are reported separately.

Results
-------

The signed bias is predicted minus observed. A negative volume bias means the
model underpredicted the plot.

.. list-table::
   :header-rows: 1
   :widths: 18 8 14 14 12 12 12

   * - Metric
     - n
     - Observed
     - Predicted
     - Bias
     - MAE
     - Relative
   * - Volume (m3/ha)
     - 506
     - 497.8
     - 448.2
     - -49.6
     - 151.0
     - -10.0%
   * - DBH (cm)
     - 506
     - 31.6
     - 27.3
     - -4.3
     - 7.0
     - -13.6%
   * - Height (m)
     - 506
     - 26.4
     - 25.2
     - -1.2
     - 3.8
     - -4.6%
   * - Stems (sph)
     - 506
     - 755.4
     - 644.6
     - -110.8
     - 356.6
     - -14.7%

By sample type
~~~~~~~~~~~~~~

The ``n`` column is volume/DBH.

.. list-table::
   :header-rows: 1
   :widths: 12 10 14 14 14 14 14 14

   * - Sample
     - n
     - Volume bias
     - Volume MAE
     - Volume rel.
     - DBH bias
     - Height bias
     - Stems bias
   * - CMI
     - 7/7
     - -111.8
     - 135.0
     - -27.3%
     - -0.1
     - -3.7
     - -327.1
   * - NFI
     - 8/8
     - -239.4
     - 239.4
     - -27.7%
     - -4.0
     - -2.1
     - -156.0
   * - VRI
     - 480/480
     - -45.6
     - 151.7
     - -9.1%
     - -4.4
     - -1.1
     - -103.1
   * - YSM
     - 11/11
     - -44.5
     - 70.5
     - -28.2%
     - -4.0
     - -2.1
     - -276.8

The managed/young subset (CMI, NFI, and YSM; n=26) has a volume bias of
-122.6 m3/ha (-27.7%), a DBH bias of -3.0 cm (-11.3%), a height bias of
-2.5 m (-10.6%), and a stems bias of -253.2 sph (-30.1%). The VRI audit is
less negative on volume but still underpredicted on DBH.

By species
~~~~~~~~~~

The ``n`` column is volume/DBH/height/stems.

.. list-table::
   :header-rows: 1
   :widths: 10 16 16 12 12 12

   * - Species
     - n
     - Volume bias (rel.)
     - DBH bias
     - Height bias
     - Stems bias
   * - Ba
     - 25/25/25/25
     - -12.5 (-2%)
     - -6.4
     - +1.0
     - +116.4
   * - Cw
     - 100/100/100/100
     - -106.3 (-19%)
     - -9.5
     - -1.7
     - -33.6
   * - Fd
     - 42/42/42/42
     - -8.8 (-2%)
     - -0.2
     - -1.2
     - -15.5
   * - Hm
     - 2/2/2/2
     - -220.3 (-51%)
     - -8.1
     - -6.1
     - -12.7
   * - Hw
     - 337/337/337/337
     - -39.6 (-8%)
     - -3.1
     - -1.2
     - -163.0

By age class
~~~~~~~~~~~~

The ``n`` column is volume/DBH/height/stems. The 5-15 cell has only five rows
and a near-zero observed volume; its relative bias is not a useful accuracy
measure.

.. list-table::
   :header-rows: 1
   :widths: 12 16 16 12 12 12

   * - Age class
     - n
     - Volume bias (rel.)
     - DBH bias
     - Height bias
     - Stems bias
   * - 5-15
     - 5/5/5/5
     - +0.5 (+123%)
     - -8.7
     - -2.8
     - +4.4
   * - 16-30
     - 71/71/71/71
     - -18.3 (-27%)
     - -4.7
     - -0.7
     - -6.2
   * - 31-50
     - 72/72/72/72
     - -62.4 (-24%)
     - -2.4
     - -2.1
     - -128.4
   * - 51-80
     - 140/140/140/140
     - -147.6 (-27%)
     - -1.7
     - -2.6
     - -249.2
   * - 81-200
     - 218/218/218/218
     - +6.2 (+1%)
     - -6.3
     - -0.2
     - -52.8

Species by age (n >= 10)
~~~~~~~~~~~~~~~~~~~~~~~~

Only cells with at least ten observations are shown. Volume and DBH are the
two metrics with enough cells to stratify; height and stems are in the CSV.

.. list-table::
   :header-rows: 1
   :widths: 10 12 8 14 12 12 12

   * - Species
     - Age
     - n
     - Volume bias
     - Volume rel.
     - DBH bias
     - DBH rel.
   * - Ba
     - 81-200
     - 20
     - -17.1
     - -2%
     - -7.0
     - -15%
   * - Cw
     - 51-80
     - 35
     - -191.8
     - -38%
     - -1.1
     - -4%
   * - Cw
     - 81-200
     - 57
     - -62.2
     - -9%
     - -15.0
     - -31%
   * - Fd
     - 16-30
     - 11
     - +35.4
     - +69%
     - -0.2
     - -1%
   * - Fd
     - 31-50
     - 16
     - +88.4
     - +101%
     - +1.2
     - +6%
   * - Fd
     - 81-200
     - 15
     - -144.9
     - -17%
     - -1.8
     - -5%
   * - Hw
     - 16-30
     - 53
     - -31.7
     - -41%
     - -5.7
     - -30%
   * - Hw
     - 31-50
     - 50
     - -111.5
     - -33%
     - -3.0
     - -11%
   * - Hw
     - 51-80
     - 105
     - -132.9
     - -23%
     - -1.9
     - -6%
   * - Hw
     - 81-200
     - 124
     - +63.4
     - +10%
     - -2.8
     - -8%

Interpretation
--------------

- Volume, DBH, height, and stems are underpredicted in the aggregate. The
  managed/young subset is more negative on volume and stems than the VRI audit.
- The signal is not a uniform scale error. Ba and Fd are close to neutral; Cw
  and Hw carry most of the volume gap. Volume is worst at 51-80 years and near
  neutral at 81-200, while DBH remains low at 81-200.
- VRI is an inventory audit, not a remeasured managed plot. The managed/young
  subset is only 26 rows, so origin, density, site index, and species remain
  confounded.
- The earlier managed-SI and density experiments improve some cells and
  overcorrect others. No global correction is defensible from this sample.

Decision
--------

ADR 0002 retains the production TSR-consistent BatchTIPSY curves. No volume,
DBH, height, stems, or AAC change follows from this sample. The next test needs
an independent remeasured managed/young sample, especially Cw and Hw in the
16-80 age range, with enough rows to separate species from origin and density.

Reproduce
---------

The observations are ``config/tsr/tipsy_ground_plot_validation.tsa47.csv``.
The stratified table is regenerated from them:

.. code-block:: bash

   python scripts/summarize_ground_plot_validation.py \
     --tsa 47 \
     --observations config/tsr/tipsy_ground_plot_validation.tsa47.csv \
     --out config/tsr/tipsy_ground_plot_validation_stratified.tsa47.csv

The full matching lane and its raw inputs are documented in
``notes/reference/tipsy-validation.md``.
