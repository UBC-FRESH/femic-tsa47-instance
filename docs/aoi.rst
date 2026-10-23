TSA 47 AOI
==========

The model AOI is the full Great Bear Rainforest South Timber Supply Area, TSA
46. The tracked boundary is ``data/source/aoi/tsa47_full.gpkg`` (EPSG:3005,
layer ``tsa47_full``, 1,991,787.4693 ha gross).

The full TSA is the benchmark boundary because the published AAC is TSA-wide.
The gross area includes ocean and foreshore; the VRI block area is the
forested subset.

Source
------

The boundary is the single current dissolved feature in the provincial
``FADM_TSA.gdb`` layer ``WHSE_ADMIN_BOUNDARIES_FADM_TSA``:

- ``TSA_NUMBER`` is ``47``;
- ``TSB_NUMBER`` is null (the dissolved TSA, not a supply block);
- ``RETIREMENT_DATE`` is null (the current feature).

The supply-block rows and the retired 2017 feature are historical context, not
build inputs.

Legal framework
---------------

The Great Bear Rainforest (Forest Management) Act and B.C. Reg. 328/2016
replaced the former Kingcome and Strathcona TSAs with the GBR South TSA,
effective January 1, 2017. The AAC for Crown land in the GBR South TSA is
**830,500 m3/yr**.

Source notes
------------

See ``notes/reference/aoi.md`` and ``notes/reference/tsr.md`` for the review
record and the public sources.
