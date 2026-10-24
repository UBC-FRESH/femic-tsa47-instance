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

3. TSR-consistent BatchTIPSY curves
-----------------------------------

The production bundle uses BatchTIPSY 4.7 curves built by
``scripts/build_tsr_lane.sh``. The FEMIC data-prep profile stays
``managed_curve_mode: vdyp_transform`` because the lane replaces the treated
curves after the checkpoint and input table are materialized. The input follows the
predecessor TSRs: the future stand regenerates to the existing analysis-unit
species composition, with 1,000 stems/ha, OAF1 = 0.85, OAF2 = 0.95, and
a one-year regeneration delay. The sources are the Kingcome TSA TSR 3 Data Package (2010, Tables 47-48) and the Strathcona TSA TSR 3 Data Package (2005, Table 21). The full
method, caveats, and run results are in ``notes/reference/tipsy-curves.md``.

The earlier VDYP transform is retained as a dated backup at
``runtime/tsa47_full_vdyp_20261023``. It is not the benchmark of record.

4. Harvest coverage
-------------------

The opening-first schedule covers all 18 managed AUs, so
``scripts/check_harvest_coverage.py`` reports no gaps and the allowlist is
unused. The earlier strict volume-only schedule left small AUs unselected; that result is retained with the dated VDYP-transform runtime. The benchmark of record is the opening-first run, not the
volume-only seed.

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
