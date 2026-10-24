Reproduce the model
===================

This guide rebuilds the TSA 47 instance from a clean checkout. The runtime
outputs are large and ignored by Git; a fresh checkout has the code, boundary,
configs, and docs but not the model tree.

Prerequisites
-------------

- Linux with Python 3.11 or 3.12.
- ``femic`` and ``ws4`` installed in the active environment.
- Wine with both 64-bit and 32-bit support for VDYP7.
- BatchTIPSY 4.7 and a Wine Mono prefix for the managed-curve lane. The
  install and prefix are host-local and are not committed.
- A userspace Xvfb for BatchTIPSY. See the North Island
  ``runbooks/tipsy-btc-linux-wine.md`` for the one-time setup.
- ``FEMIC_EXTERNAL_DATA_ROOT`` pointing at a materialized
  ``femic-public-data/data`` tree.
- The ``plots/`` directory in the instance root.

1. Materialize the public data
------------------------------

.. code-block:: bash

   export FEMIC_EXTERNAL_DATA_ROOT=/path/to/femic-public-data/data
   python scripts/check_public_data.py --out data/source/public_data_manifest.json

The four required geodatabases and the two pre-stacked rasters must resolve to
real files, not annex pointer symlinks.

2. Build the AOI
----------------

.. code-block:: bash

   python scripts/build_aoi.py \
     --source "$FEMIC_EXTERNAL_DATA_ROOT/bc/tsa/FADM_TSA.gdb" \
     --tsa-number 47 \
     --out data/source/aoi/tsa47_full.gpkg

Expected: one feature, EPSG:3005, 1,991,787.47 ha gross.

3. Run the FEMIC data-prep lane
-------------------------------

.. code-block:: bash

   python -m femic run \
     --run-config config/run_profile.tsa47_full.yaml \
     --run-id tsa47_full_20261023 \
     --log-dir runtime/logs \
     --skip-checks

The profile keeps ``managed_curve_mode: vdyp_transform``. This run
materializes the VDYP caches, the calibrated-stand checkpoint, and
``data/03_input-tsa47.csv``. The production managed curves are built in the
next step; the transform curves are not the benchmark of record.

The run takes tens of minutes. It writes the model-input bundle and
``data/vri_vclr1p_checkpoint8.feather``.

4. Build the TSR-consistent model
---------------------------------

.. code-block:: bash

   export FEMIC_BTC_WINEPREFIX=/path/to/wineprefix-mono
   export FEMIC_BTC_DISPLAY=:99
   TSA=47 bash scripts/build_tsr_lane.sh

The lane derives the area-weighted VRI conifer mix, writes the BatchTIPSY
input, runs BTC, interpolates the treated curves, exports Patchworks, merges
safe slivers, compiles the matrix, and runs the opening-first benchmark. The
lane writes ``runtime/tsa47_tsr``. After validation, the served instance
uses that tree as ``runtime/tsa47_full``; the earlier VDYP run is kept at
``runtime/tsa47_full_vdyp_20261023``.

5. Verify
---------

.. code-block:: bash

   python -m ws4.cli validate --dataset runtime/tsa47_full/matrix
   python scripts/check_runtime_signal.py \
     --dataset runtime/tsa47_full/matrix \
     --bundle data/model_input_bundle \
     --run runtime/tsa47_full/runs/opening_first
   python scripts/check_harvest_coverage.py \
     --dataset runtime/tsa47_full/matrix \
     --schedule runtime/tsa47_full/schedules/opening_first.csv
   python scripts/dashboard.py

The dashboard runs lint, format, strict types, tests, the workflow validator,
and the docs build.

6. Serve
--------

.. code-block:: bash

   ./serve_tsa47_calibrated.sh

Then check ``http://127.0.0.1:8018/health``. Set ``MODEL_DIR`` to serve the
dated VDYP backup instead.

Known rebuild boundaries
------------------------

- The first run failed when ``plots/`` was absent. Create it before the run.
- The BatchTIPSY install, Wine prefix, and Xvfb are host-local. The TSR lane
  cannot run on a machine without them.
- The checkpoint is ``data/vri_vclr1p_checkpoint8.feather``, not the TSA 48
  ``ria_`` name.
- The pre-stacked ``siteprod.tif`` and ``misc.thlb.tif`` rasters must be
  materialized.
- The model applies opening size and adjacency through the opening-first
  schedule, but green-up, seral-stage, and visual constraints are still out of
  scope.
- The AU-level site index is applied to every species in the TIPSY input; the
  VRI AU table does not carry species-specific site indices.
