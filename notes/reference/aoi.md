# TSA 47 AOI

Status: current dissolved TSA 47 boundary accepted for the benchmark model.

## Decision

The model uses the **full Great Bear Rainforest South TSA 47** boundary, not a
supply block or a district clip. The published AAC is TSA-wide, so the full TSA
is the defensible scale for the benchmark.

## Source

| Item | Value |
| --- | --- |
| Source | `FEMIC_EXTERNAL_DATA_ROOT/bc/tsa/FADM_TSA.gdb` |
| Layer | `WHSE_ADMIN_BOUNDARIES_FADM_TSA` |
| Selection | `TSA_NUMBER = 47`, `TSB_NUMBER` null, `RETIREMENT_DATE` null |
| Output | `data/source/aoi/tsa47_full.gpkg` |
| Output layer | `tsa47_full` |
| CRS | EPSG:3005 |
| Gross area | 1,991,787.4693 ha |
| Bounds | 740945.10, 585354.72, 1069115.12, 769795.65 |

The layer also carries 14 supply-block rows and one retired 2017 row for TSA 47.
They are components and history, not the build boundary.

## Reviewed numbers

| Quantity | Value |
| --- | ---: |
| TSA 47 gross area | 1,991,787.47 ha |
| Published AAC | 830,500 m3/yr |
| AAC effective date | 2017-01-01 |

The gross area includes ocean and foreshore. The VRI block area is the
forested subset and is reported after the ws4 build.

## Related dataset

The GBR South TSA 47 model is a separate, independent instance:
`UBC-FRESH/femic-tsa47-instance`. See
`notes/reference/related-instances.md`.
