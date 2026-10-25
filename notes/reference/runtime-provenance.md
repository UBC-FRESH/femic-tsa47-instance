# Runtime provenance refresh

Date: 2026-10-25
Phase: P50

The current TSA 47 production matrix was refreshed so its sidecar matches the
tracked provenance. The matrix tables were not rewritten.

| Item | Value |
| --- | --- |
| Matrix | `runtime/tsa47_full/matrix` |
| Sidecar | `runtime/tsa47_full/matrix/data_quality.yaml` |
| Pre-refresh sidecar | absent |
| Post-refresh sidecar SHA-256 | `a8900e98664e2413ce8522d9d15265b36c4069e5ab48e454fcf0bf52321b9c19` |
| Manifest SHA-256 | `d5d01ad02488f4c559223659e3be20ca4cb640e3564438d641dbb65e0ff298bc` |
| Quality report | `runtime/tsa47_full/quality/p50/quality.json` |
| Quality report SHA-256 | `1f1d70c10887e6c9ac381b1beee8bb15b11d70d0b5b49b414d1c17590160d493` |
| Status | ok |
| Tables | 12 |
| Warnings | none |

## Command

```bash
python -m ws4.cli quality \
  --dataset runtime/tsa47_full/matrix \
  --sidecar config/dataset_quality.yaml \
  --out runtime/tsa47_full/quality/p50 \
  --check
```

Exit status: 0.

## Checks

- metadata: ok
- tables: ok (12 tables have rows)
- provenance: ok (`data_quality.yaml` loaded)
- target_coverage: not-applicable (no targets supplied)

## Notes

- The runtime quality report is local and untracked.
- The dated VDYP-transform backup matrix was not refreshed.
- No curve, target, or AAC input changed.
