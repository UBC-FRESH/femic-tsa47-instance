Decisions and limitations
=========================

This page records the model decisions that matter to a reviewer. The detailed
records are in ``notes/reference/`` and ``notes/reports/``.

1. Full TSA boundary
--------------------

The benchmark uses the full current dissolved TSA 47 boundary. The AAC is
a TSA-wide legal determination, so a district or tenure clip would not answer
the AAC question. Record: ``notes/reference/aoi.md``.

2. Predecessor-derived THLB
---------------------------

The GBR order replaced the predecessor TSAs. TSA 47 has no dedicated TSR
cycle, so the THLB target is derived from the mainland portions of the former Kingcome TSA (186,914 ha current EBM THLB) and Strathcona TSA (162,873 ha current THLB).

This is a **predecessor-value derivation**, not a reviewed GBR netdown. Record:
``config/tsr/overlay.yaml`` and ``notes/reference/tsr.md``.

3. VDYP transform, not accepted TIPSY
-------------------------------------

The managed curve lane uses ``managed_curve_mode: vdyp_transform``. It is a
provisional transform of the natural curves, not accepted TIPSY yield curves.
Replace it with a BatchTIPSY handoff before calling the model production-ready.

4. Zero-harvest AUs
-------------------

Three small managed AUs are unselected by the strict volume-only benchmark:

.. list-table::
   :header-rows: 1
   :widths: 16 20 18

   * - AU
     - Managed area (ha)
     - Total area (ha)
   * - 4701002
     - 139.2
     - 20,768.9
   * - 4702004
     - 40.7
     - 18,424.0
   * - 4701005
     - 111.4
     - 8,246.2

Total: **291.2 ha (0.20% of the managed area)**. The
coverage run selects the AUs above the 100 ha threshold and re-optimizes. The
strict benchmark remains the benchmark of record. Record:
``notes/reference/model-sanity.md`` and
``config/harvest_coverage.allowlist.json``.

5. UI geometry scale
--------------------

The served map uses a 100 m overview. The full layer is retained. This is an
interim payload fix; production serving needs viewport and tiled detail. Record:
``notes/reference/ws4-build.md``.

6. Independent sibling instance
-------------------------------

This repository and `Great Bear Rainforest North TSA 46 <https://github.com/UBC-FRESH/femic-tsa46-instance>`_
are related but independent. Neither imports the other. Record:
``notes/reference/related-instances.md``.
