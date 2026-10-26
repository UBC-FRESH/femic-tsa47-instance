TSA 47 AOI
==========

The model AOI is the full Great Bear Rainforest South Timber Supply Area, TSA 47. The
tracked boundary is ``data/source/aoi/tsa47_full.gpkg`` (EPSG:3005,
layer ``tsa47_full``).

Boundary
--------

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - Source
     - ``FEMIC_EXTERNAL_DATA_ROOT/bc/tsa/FADM_TSA.gdb``
   * - Source layer
     - ``WHSE_ADMIN_BOUNDARIES_FADM_TSA``
   * - Selection
     - ``TSA_NUMBER = 47``, ``TSB_NUMBER`` null, ``RETIREMENT_DATE`` null
   * - Output
     - ``data/source/aoi/tsa47_full.gpkg``, layer ``tsa47_full``
   * - CRS
     - EPSG:3005
   * - Gross area
     - 1,991.8 thousand ha
   * - Bounds
     - 740945.10, 585354.72, 1069115.12, 769795.65

The layer also carries supply-block rows and retired historical versions. The
selection above keeps the single current dissolved TSA feature. Supply blocks
are components, not the build boundary.

TSA 47 contains 60.1% of the Kingcome boundary and 20.2% of the Strathcona boundary; the THLB target apportions the predecessor THLBs by those gross overlap fractions.

Legal framework
---------------

The Great Bear Rainforest (Forest Management) Act and B.C. Reg. 328/2016 came
into effect on January 1, 2017. They replaced the former North Coast, Mid
Coast, Kingcome, and Strathcona TSAs with the GBR North, GBR South, and North
Island TSAs.

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - Current AAC
     - 830,500 m3/yr
   * - Legal source
     - B.C. Reg. 328/2016, section 10
   * - Effective date
     - 2017-01-01

Why the full TSA
----------------

The published AAC is a TSA-wide legal determination. The full dissolved TSA is
therefore the only defensible benchmark boundary. District, tenure, or
supply-block clips are overlays or planning sub-units, not the AAC boundary.

Decision record
---------------

The review record is ``notes/reference/aoi.md``. The numeric check is
``data/source/aoi/tsa47_full.summary.json``. A change to
``selection.boundary_path`` or ``boundary_code`` needs a new recorded decision.
