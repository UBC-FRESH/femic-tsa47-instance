Model limitations
=================

This page is the short, citable boundary for the Great Bear Rainforest South
TSA 47 benchmark. It summarizes the accepted decision record in
``notes/adr/0001-model-boundary.md`` and the detailed history in
:doc:`decisions`. The upstream software boundary is documented in
`Limitations and boundaries <https://ubc-fresh.github.io/ws4/guides/limitations-and-boundaries.html>`__.

The model is a strategic benchmark built from public data. It is not an
operational plan, a legal determination, or an investment case.

Boundary and land base
----------------------

- The model uses the full current dissolved TSA 47 boundary (1,991.8 thousand ha
  gross), not a district, tenure, or watershed clip.
- The managed land base is calibrated to 145,256 ha from the mainland
  portions of the former Kingcome TSA (186.9 thousand ha current EBM THLB at 60.1%)
  and Strathcona TSA (162.9 thousand ha current THLB at 20.2%). That is a
  **predecessor-value derivation**, not a reviewed GBR netdown.
- The calibration forces the managed area to the target. It does not discover a
  new operability, retention, or conservation land base.

Inventory
---------

- Inventory is the 2025 BC VRI vintage. The source manifest does not record an
  imputation share or coverage percentage, so those values remain unknown.
- Age, species composition, site index, and volume carry VRI error. No field
  audit of the compiled blocks is included.
- The model does not resolve private land, Indian reserves, or tenure-specific
  operability beyond the public inventory and the calibrated land base.

Yield curves
------------

- Natural curves are VDYP. Managed curves are BatchTIPSY 4.7 output from the
  TSR-consistent lane, using the Kingcome TSA TSR 3 Data Package (2010,
  Tables 47-48) and the Strathcona TSA TSR 3 Data Package (2005, Table 21).
- The managed lane is a **predecessor-TSR assumption set**, not a reviewed GBR
  yield table. It assumes regeneration to the existing AU species mix,
  1,000 stems/ha, OAF1 = 0.85, OAF2 = 0.95, a regeneration delay of one year,
  and a uniform AU-level site index across species. Genetic gain is not applied.
- The `managed_curve_mode: vdyp_transform` profile flag describes the FEMIC
  data-preparation lane. Production treated curves come from the TSR-consistent
  BatchTIPSY lane; the earlier VDYP-transform run is a dated backup.
- Ground-plot validation is reported in :doc:`ground-plot-validation`. The VRI
  audit and the 26-row managed/young subset both show underprediction, but the
  sample cannot separate origin, density, and site index; production remains on
  the TSR-consistent lane (ADR 0002).
- No public management-origin field or independent remeasured managed/young
  sample is available; the four-strata validation is data-limited (ADR 0003).
- Independent height checks against RESULTS cover heights are encouraging, but
  volume, DBH, and mortality are not fully validated. RESULTS basal area is
  largely a placeholder, and the public PSP layer is not a remeasured audit in
  all cases.

AAC and scheduling
------------------

- The published AAC (830,500 m3/yr) is treated as a policy ceiling. The
  benchmark reports ten-decade volumes in the 8,305,000-8,306,000 m3 band; that is a
  feasibility test, not proof that the AAC is ecologically or economically
  sustainable.
- The opening-first schedule is a deterministic seed, not an optimized plan. No
  optimality claim is made for it, for bounded searches, or for heuristic
  schedules.
- The opening and patch rules are model constraints. They do not establish
  operational feasibility, road access, slope stability, or silviculture
  capacity.

What the model does not answer
------------------------------

- It does not set or defend a new AAC.
- It does not provide a reviewed GBR land-base netdown.
- It does not provide a validated volume, DBH, or mortality model.
- It does not model markets, delivered log costs, milling, wildfire, insects,
  climate change, visual quality, community values, or Indigenous land-use
  objectives.
- It does not replace professional review, legal advice, or field assessment.

Using the results
-----------------

Use the model for strategic sensitivity analysis, provenance review, and method
development. Do not present its output as an operational harvest plan, a
certification result, or a guarantee of sustainable harvest. When a reviewed
netdown, a dedicated TSR cycle, or a stronger validation becomes available,
record the change in a new ADR rather than silently changing the profile.

Related records: :doc:`decisions`, :doc:`model-build`,
``notes/reference/tipsy-curves.md``, ``notes/reference/tipsy-validation.md``,
and ``config/dataset_quality.yaml``.

The current runtime matrices, sidecar hashes, and quality status are recorded in
:doc:`runtime-provenance`.
