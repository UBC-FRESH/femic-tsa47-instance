Model structure
===============

The compiled ws4 dataset is a fragment-level columnar store. Blocks aggregate
fragments at runtime; the schedule, simulator, optimizer, and reports operate on
blocks.

Dataset tables
--------------

.. list-table::
   :header-rows: 1

   * - Table
     - Rows
     - Role
   * - ``fragments.parquet``
     - 98,040
     - Fragment geometry and age, keyed to a block and track
   * - ``blocks.parquet``
     - 98,040
     - Block/track/offset/area join used by simulation
   * - ``tracks.parquet``
     - 34,656
     - AU, IFM, origin, silviculture, retention, and treatment state
   * - ``treatments.parquet``
     - 22,000
     - Treatment timeline per track
   * - ``features.parquet``
     - 207,936
     - Feature labels and curve references
   * - ``products.parquet``
     - 66,000
     - Product labels and curve references
   * - ``accounts.parquet``
     - 45
     - Account definitions
   * - ``curves.parquet``
     - 3,333
     - Curve points
   * - ``strata.parquet``
     - 34,656
     - Track/offset age transitions

Blocks and area
---------------

.. list-table::
   :header-rows: 1

   * - Quantity
     - Value
   * - Unique blocks
     - 74,170
   * - Fragment rows
     - 98,040
   * - Block area
     - 692,811.84 ha
   * - Gross AOI area
     - 1,991,787.47 ha
   * - Managed area
     - 145,256 ha
   * - Managed share of block area
     - 21.0%

Tracks
------

A track name carries the model semantics explicitly:

.. code-block:: text

   AU(<code>)+IFM(managed|unmanaged)+ORIGIN(natural|treated)
     +SILV_STATE(<state>)+RETENTION(<share>)+treatment(<code>)

- ``AU`` is the analysis unit.
- ``IFM`` is treatment eligibility, not origin.
- ``ORIGIN`` is curve provenance.
- ``RETENTION`` moves area from managed to unmanaged without changing origin.

Species composition
-------------------

The initial ``feature.Area.og1.*`` accounts give the compiled species mix:

.. list-table::
   :header-rows: 1
   :widths: 18 22 12

   * - Species
     - Initial area (ha)
     - Share
   * - CWH_CW
     - 162,887.0
     - 37.3%
   * - CWH_HW
     - 132,610.9
     - 30.3%
   * - CWH_YC
     - 56,471.4
     - 12.9%
   * - MH_HM
     - 49,681.9
     - 11.4%
   * - CWH_BA
     - 18,239.8
     - 4.2%
   * - CWH_FD
     - 17,180.9
     - 3.9%

Every species above has a nonzero area account and a resolved curve. The
runtime-signal gate checks this on each build.

Accounts
--------

The model carries ``feature.Area``, ``feature.Yield``, ``product.Yield``,
``product.Treated``, and ``product.HarvestedVolume`` accounts. The AAC target
uses ``product.Yield.managed.Total``. The managed area account is
``feature.Area.managed``.

Geometry
--------

``fragments.geojson`` is the 100 m simplified UI layer.
``fragments_full.geojson`` is the unsimplified layer. The source fragments
shapefile is an interchange artifact under ``output/patchworks_tsa47_full/fragments/``.
