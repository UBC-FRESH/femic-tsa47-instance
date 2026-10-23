Model Build
===========

The full TSA 47 model is built by ``scripts/build_full_tsa47_model.sh``. The
script records each command and artifact path; the Patchworks XML/fragments
pair is an interchange input to ``ws4 build``, not the runtime lane.

Chain
-----

.. code-block:: text

   femic run
     -> femic export patchworks
     -> ws4 build
     -> ws4 validate
     -> build_baseline_schedule
     -> ws4 simulate + report
     -> prepare_ws4_ui (exact block geometry)
     -> prepare_land_base (non-forest underlay)

FEMIC compiles the public inventory and yield curves and writes the model-input
bundle. The export reads the calibrated checkpoint when ``CALIBRATE_THLB=1`` so
each stand carries the proportional THLB signal. ws4 compiles the full matrix
and runs the baseline.

Commands
--------

.. code-block:: bash

   MODEL_DIR=runtime/tsa47_full \
   PATCHWORKS_OUT=output/patchworks_tsa47_full \
   CALIBRATE_THLB=1 \
   THLB_TARGET_HA=<published THLB> \
   scripts/build_full_tsa47_model.sh

Set ``FEMIC_EXTERNAL_DATA_ROOT`` to the public BC data root. The generated
matrix, runs, evidence, and UI geometry are written under
``runtime/tsa47_full/`` and are ignored by Git.

Runtime boundary
----------------

VDYP7 is a Windows executable. On Linux it runs under Wine, including the
32-bit loader. The first lane sets ``vdyp_sampling_mode: auto`` because the
larger ``all`` batches exceeded the short VDYP console timeout in the TSA 48
run. Auto sampling fits from fewer stands, so it is a provisional workaround;
raise the timeout and rerun in ``all`` mode before release.

The first lane also sets ``managed_curve_mode: vdyp_transform`` and therefore
does not need BatchTIPSY. That transform is a provisional managed curve lane,
not accepted TIPSY yield curves. Replace it before release.

The THLB calibration is a proportional rescale, not a reviewed GBR netdown. The
benchmark assumes the calibrated managed area.

AAC benchmark
-------------

The ten-decade benchmark is a separate search from the baseline:

.. code-block:: bash

   scripts/run_aac_benchmark.sh

It writes ``runtime/tsa47_full/runs/aac_benchmark/``. The target band is
``8,305,000-8,306,000`` m3 per decade at ``830,500`` m3/yr. The recorded run scheduled
3,872 blocks and met all ten decades with objective 0.0. Set
``ITERATIONS``, ``PATIENCE``, ``THREADS``, or ``TIME_LIMIT`` to change the
search. ``scripts/watch_aac_benchmark.sh`` shows the search live without
persisting a run.

Signal and coverage gates
-------------------------

Two gates keep the compiled signal and the benchmark coverage separate:

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
The strict AAC benchmark and the ``aac_benchmark_coverage`` diagnostic are
recorded separately.
