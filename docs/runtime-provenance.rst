Runtime provenance refresh
==========================

The current production matrix was refreshed on 2026-10-25 so its
`data_quality.yaml` sidecar matches the provenance published in the current
provenance records. The quality gate passes. This page records the matrix path, hashes, and gate
result.

Scope
-----

This is a provenance refresh, not a rebuild. The matrix tables were not
rewritten, and no curve, target, or AAC input changed. The dated VDYP-transform
backup matrices were not refreshed.

Current matrix
--------------

TSA 47
~~~~~~

- Matrix: ``runtime/tsa47_full/matrix``
- Sidecar: ``runtime/tsa47_full/matrix/data_quality.yaml``
- Sidecar SHA-256: ``a8900e98664e2413ce8522d9d15265b36c4069e5ab48e454fcf0bf52321b9c19``
- Manifest SHA-256: ``d5d01ad02488f4c559223659e3be20ca4cb640e3564438d641dbb65e0ff298bc``
- Quality report: under ``runtime/tsa47_full/quality/``
- Quality report SHA-256: ``1f1d70c10887e6c9ac381b1beee8bb15b11d70d0b5b49b414d1c17590160d493``
- Status: **ok**; provenance supplied; 12 tables; no warnings.

Quality checks
--------------

.. list-table::
   :header-rows: 1
   :widths: 24 22 54

   * - Check
     - Status
     - Detail
   * - metadata
     - ok
     - Sidecar supplies the provenance metadata.
   * - tables
     - ok
     - 12 tables have rows.
   * - provenance
     - ok
     - Sidecar loaded: ``data_quality.yaml``.
   * - target_coverage
     - not-applicable
     - No active targets were supplied. This is not a target-coverage pass.

The report carries the current limitations, including:

- natural VDYP curves and TSR-consistent BatchTIPSY managed curves;
- predecessor-derived THLB;
- the data-limited managed/young validation in ADR 0003;
- the sparse ground-plot validation in ADR 0002;
- the deterministic opening-first seed and the AAC-as-ceiling caveat.

Refresh command
---------------

The command copies the tracked sidecar beside the matrix and runs the gate:

.. code-block:: bash

   python -m ws4.cli quality \
     --dataset runtime/tsa47_full/matrix \
     --sidecar config/dataset_quality.yaml \
     --out runtime/tsa47_full/quality/p50 \
     --check

The pre-refresh matrix had no ``data_quality.yaml``. The post-refresh sidecar
hash equals the tracked ``config/dataset_quality.yaml`` hash. The runtime
quality report is local and untracked; this page and
``notes/reference/runtime-provenance.md`` are the tracked evidence.

Limits
------

- The runtime artifacts are local and not committed; the hashes are a snapshot.
- No target file was supplied, so target coverage is not asserted.
- The dated VDYP-transform backups are separate comparison artifacts.
- This is not a release tag or a new model version.
