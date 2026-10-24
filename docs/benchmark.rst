AAC benchmark
=============

The benchmark asks whether the model can hold the published AAC across ten
decades. The target account is ``product.Yield.managed.Total`` with a
``period_width`` of 10. Each decade target is ten times the annual AAC.

Targets
-------

.. list-table::
   :header-rows: 1

   * - Item
     - Value
   * - AAC
     - 830,500 m3/yr
   * - Decade target band
     - 8,305,000-8,306,000 m3
   * - Horizon
     - 100 years
   * - Target file
     - ``config/targets.tsa47_full.yaml``
   * - Run
     - ``runtime/tsa47_full/runs/aac_benchmark``

Strict benchmark result
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 10 25 14

   * - Decade
     - Realized volume (m3)
     - Band status
   * - 1
     - 8,305,998.831
     - met
   * - 2
     - 8,305,995.939
     - met
   * - 3
     - 8,305,992.017
     - met
   * - 4
     - 8,305,996.992
     - met
   * - 5
     - 8,305,998.787
     - met
   * - 6
     - 8,305,991.570
     - met
   * - 7
     - 8,305,999.826
     - met
   * - 8
     - 8,305,999.658
     - met
   * - 9
     - 8,305,998.183
     - met
   * - 10
     - 8,305,993.119
     - met

All ten decades are inside the band. The search starts from the target-driven
greedy seed, schedules 3,872 blocks, and records
5,327 events. The objective is 0.0.

Coverage run
------------

The strict volume-only search leaves small managed AUs unselected. A separate
coverage run starts from the strict schedule, adds one event for each AU above
the 100 ha threshold, and re-optimizes. It is a diagnostic, not the benchmark
of record.

- Coverage run: ``runtime/tsa47_full/runs/aac_benchmark_coverage``
- Blocks scheduled: 3,951
- Events: 5,409
- AUs covered: 4701002 and 4701005
- All ten decades meet the strict band with objective approximately 0.
- Per-decade report: ``runtime/tsa47_full/runs/aac_benchmark_coverage/report_targets.csv``

Baseline versus benchmark
-------------------------

The baseline schedule is a deterministic clearcut-at-age-60 reference. It
harvests every block once and dumps mature stands into the first decade, so it
is not an AAC benchmark. Use it to verify that the dataset and simulator run,
not to judge the AAC.

Rerun
-----

.. code-block:: bash

   scripts/run_aac_benchmark.sh
   # optional: change the search budget
   ITERATIONS=8000 PATIENCE=1000 THREADS=8 scripts/run_aac_benchmark.sh

The watcher is observational and does not persist a run:

.. code-block:: bash

   scripts/watch_aac_benchmark.sh
   PLAIN=1 scripts/watch_aac_benchmark.sh
