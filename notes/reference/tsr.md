# TSR and AAC provenance

Status: the GBR South TSA 47 has no dedicated TSR cycle in the provincial TSR
folder. The current AAC comes from the Great Bear Rainforest (Forest
Management) Act and B.C. Reg. 328/2016. The predecessor TSA TSR packages are
the available public netdown evidence.

## Current AAC

| Item | Value | Source |
| --- | ---: | --- |
| GBR North TSA AAC | 803,000 m3/yr | B.C. Reg. 328/2016, s. 5; effective 2017-01-01 |
| GBR South TSA AAC | 830,500 m3/yr | B.C. Reg. 328/2016, s. 10; effective 2017-01-01 |

The provincial TSR pages report the same current AAC values as of January 1,
2017:
`https://www2.gov.bc.ca/.../allowable-annual-cut-timber-supply-areas/great-bear-rainforest-north`
and `.../great-bear-rainforest-south`.

## TSR document materialization

The canonical FEMIC TSR index (`femic tsr index`) records 0 documents under
`TSA/Great_Bear_Rainforest_South_47/` and 0 under
`TSA/Great_Bear_Rainforest_South_47/`.

The built-in fetch and extract functions were run against the predecessor TSAs
that the GBR order replaced:

```bash
python -m femic tsr fetch --tsa 19 --tsa 21 --tsa 33 --tsa 37
python -m femic tsr extract --tsa 19 --tsa 21 --tsa 33 --tsa 37
```

The corpus is cached under `~/.femic/tsr/` and is not committed.

## TSR facts used

The THLB target is recorded in `config/tsr/overlay.yaml` after the
`femic tsr overlay-init` step and the reviewed fact extraction. Facts that
could not be tied to a page are not promoted.

## Predecessor mapping

| GBR TSA | Predecessor TSAs |
| --- | --- |
| GBR South TSA 47 | Kingcome (33), Strathcona (37) |
| GBR South TSA 47 | Kingcome (33), Strathcona (37) |
