Decisions and limitations
=========================

This page records the model decisions that matter to a reviewer. The concise
operational summary is :doc:`limitations`; the accepted boundary is
``notes/adr/0001-model-boundary.md``. The detailed records are in
``notes/reference/`` and ``notes/reports/``.

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

5. Accuracy is not AAC fit
---------------------------

The AAC band is a policy constraint, not a validation statistic. A curve set
that needs fewer hectares is not thereby more accurate. The independent height
check compares TIPSY height at age with observed RESULTS cover heights. The
current TSR curves are slightly more accurate than the RESULTS species mix
(TSR bias -0.55 m, MAE 1.38 m, RMSE 2.53 m; RESULTS bias
-0.34 m, MAE 1.36 m). The height bias is largely a site-index issue: the checkpoint AU median SI
understates the managed/harvested stand SI (TSA 46 CWH_HW H: 23.0 m observed
versus 16.3 m checkpoint). A holdout test found that a managed-land SI does not improve TSA 47 height
accuracy (MAE 1.52 m to 1.60 m), although it improves TSA 46 (1.86 m to
1.46 m). Volume, DBH, and mortality remain unvalidated.
Record: ``notes/reference/tipsy-validation.md``.

6. UI geometry scale
--------------------

The served map uses a 100 m overview. The full layer is retained. This is an
interim payload fix; production serving needs viewport and tiled detail. Record:
``notes/reference/ws4-build.md``.

7. Independent sibling instance
-------------------------------

This repository and `Great Bear Rainforest North TSA 46 <https://github.com/UBC-FRESH/femic-tsa46-instance>`_
are related but independent. Neither imports the other. Record:
``notes/reference/related-instances.md``.

8. Accepted model boundary
--------------------------

ADR 0001 records the accepted boundary: full TSA, predecessor-derived THLB,
TSR-consistent BatchTIPSY managed curves, and the AAC as a policy ceiling. It
also records what the model does not answer. See
``notes/adr/0001-model-boundary.md`` and :doc:`limitations`.

9. Ground-plot validation
-------------------------

The P48 check matches 506 rows from 130 sites. The VRI audit (n=480) and the
managed/young subset (n=26) both under-predict volume, DBH, and stems, but the
sample cannot separate species, age, site index, establishment density, and
management origin. Production remains on the TSR-consistent BatchTIPSY lane.
See ``notes/adr/0002-ground-plot-validation.md`` and
:doc:`ground-plot-validation`.

10. Managed/young validation pre-registration
---------------------------------------------

The public FAIB data have no management-origin field. The remeasured candidates
are natural PSP_G, experimental PSP_R, or origin-unknown NFI, and the P48 rows
are exploratory. The pre-registered four-strata test is therefore data-limited:
zero eligible sites. Production remains on the TSR-consistent BatchTIPSY lane.
See ``notes/adr/0003-ground-plot-preregistration.md`` and
:doc:`ground-plot-preregistration`.
