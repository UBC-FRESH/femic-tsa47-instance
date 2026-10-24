Model build
===========

The model is built by ``scripts/build_full_tsa47_model.sh``. The script
records every command and artifact path. The Patchworks XML/fragments pair is an
interchange input to ``ws4 build``, not the runtime lane.

Chain
-----

.. code-block:: text

   femic run
     -> femic export patchworks
     -> ws4 build
     -> ws4 validate
     -> build_baseline_schedule
     -> ws4 simulate + report
     -> ws4 optimize (AAC benchmark)
     -> prepare_ws4_ui
     -> prepare_land_base

Upstream run
------------

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - Run ID
     - ``tsa47_full_20261023``
   * - Status
     - ok, exit 0
   * - Duration
     - 2,078.901 s
   * - Started / finished
     - 2026-10-23T20:06:12Z / 2026-10-23T20:40:51Z
   * - AUs / curves
     - 18 / 73
   * - Exported fragments
     - 74,170
   * - Manifest
     - ``runtime/logs/run_manifest-tsa47_full_20261023.json``

The run uses the full TSA boundary in ``config/run_profile.tsa47_full.yaml``
and the public data root. It writes the model-input bundle, VDYP caches, and the
checkpoint under ``data/`` (all ignored by Git).

Build and validation
--------------------

.. code-block:: bash

   MODEL_DIR=runtime/tsa47_full \
   PATCHWORKS_OUT=output/patchworks_tsa47_full \
   CALIBRATE_THLB=1 \
   THLB_TARGET_HA=145256 \
   scripts/build_full_tsa47_model.sh

The script runs ``femic export patchworks``, ``ws4 build``, ``ws4 validate``,
the baseline schedule and simulation, and the UI geometry preparation.

.. list-table::
   :header-rows: 1

   * - Dataset fact
     - Value
   * - Blocks
     - 73,659
   * - Fragments in the compiled dataset
     - 97,529
   * - Block area
     - 692,811.84 ha
   * - Tracks
     - 34,656
   * - Treatments
     - 22,000
   * - Feature rows
     - 207,936
   * - Product rows
     - 66,000
   * - Accounts
     - 45
   * - Curve rows
     - 3,333

Safe sliver cleanup
-------------------

The build runs ``scripts/merge_slivers.py`` before ``ws4 build``. It merges
only small blocks with the same AU, IFM, and origin, an area-weighted age
difference of at most 20 years, and a neighbour with ``RETENTION = 0``.
Retention/IFM split fragments are never merged and isolated small blocks are
kept. The merge removed 511 blocks (255.78 ha) and left
net area and managed area unchanged.

THLB calibration
----------------

The calibration scales each stand's ``thlb_raw / 100`` by one factor, capped at
1.0. The factor is solved so the capped proportional area hits the target.

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - Uncalibrated managed area
     - 146,347.89 ha
   * - Target
     - 145,256 ha
   * - Factor
     - 0.9925390944203576
   * - Saturated rows
     - 0
   * - Evidence
     - ``runtime/tsa47_full/evidence/thlb_calibration.json``

The calibration is a proportional rescale, not a reviewed GBR netdown.

Baseline
--------

The baseline schedule harvests every block once when it reaches age 60. It is a
reproducible reference, not the AAC benchmark: it dumps mature stands into the
first decade and then declines. The baseline run is
``runtime/tsa47_full/runs/baseline``.

AAC benchmark
-------------

The benchmark is a separate search from the baseline:

.. code-block:: bash

   scripts/run_aac_benchmark.sh

The target band is 8,305,000-8,306,000 m3 per decade at
830,500 m3/yr. The recorded run schedules 3,872 blocks with
5,327 events and meets all ten decades. See :doc:`benchmark` for
the decade table and the coverage run.

Signal and coverage gates
-------------------------

.. code-block:: bash

   python scripts/check_runtime_signal.py \
     --dataset runtime/tsa47_full/matrix \
     --bundle data/model_input_bundle \
     --run runtime/tsa47_full/runs/aac_benchmark

   python scripts/check_harvest_coverage.py \
     --dataset runtime/tsa47_full/matrix \
     --schedule runtime/tsa47_full/runs/aac_benchmark/schedule.csv \
     --allowlist config/harvest_coverage.allowlist.json

The runtime-signal gate fails on a missing species/SI label, an orphan track,
or a missing curve. The coverage gate fails when an AU with at least 100 ha of
managed area has no harvest event, unless the allowlist names it with a reason.

Runtime boundary
----------------

VDYP7 is a 32-bit Windows executable. On Linux it runs under Wine, including the
32-bit loader. The first lane sets ``vdyp_sampling_mode: auto`` because larger
``all`` batches exceeded the short VDYP console timeout in the TSA 48 reference
run. Auto sampling fits from fewer stands, so it is a provisional workaround.

The first lane also sets ``managed_curve_mode: vdyp_transform`` and therefore
does not require BatchTIPSY. That transform is a provisional managed curve lane,
not accepted TIPSY yield curves.

The legacy pipeline also needs ``plots/`` to exist, a
``config/tipsy/tsa47.yaml`` case file, and the materialized
``siteprod.tif`` and ``misc.thlb.tif`` rasters. ArcRasterRescue is only needed
when the pre-stacked SiteProd raster is absent.

Opening policy
--------------

The opening-first schedule is built from the touching-block topology:

.. code-block:: bash

   python scripts/build_topology.py \
     --fragments runtime/tsa47_full/fragments.geojson \
     --out runtime/tsa47_full/topology.csv \
     --distance-m 0

   python scripts/build_opening_schedule.py \
     --dataset runtime/tsa47_full/matrix \
     --topology runtime/tsa47_full/topology.csv \
     --out runtime/tsa47_full/schedules/opening_first.csv \
     --years 100 --min-area 5 --max-area 40 \
     --target-per-decade 8306000 \
     --intermediate-share 0

See :doc:`benchmark` for the result and :doc:`web-ui` for the run list.

