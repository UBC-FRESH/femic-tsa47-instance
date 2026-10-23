Web UI
======

The ws4 web UI serves the compiled TSA 47 dataset and its runs. It is
read-only except for the optional run and agent controls. It binds loopback by
default and has no authentication.

Launch
------

The calibrated model is served by:

.. code-block:: bash

   ./serve_tsa47_calibrated.sh

The script expands to:

.. code-block:: bash

   python -m ws4.cli serve \
     --dataset runtime/tsa47_full/matrix \
     --runs runtime/tsa47_full/runs \
     --geometry runtime/tsa47_full/fragments.geojson \
     --land-base runtime/tsa47_full/land_base.geojson \
     --targets config/targets.tsa47_full.yaml \
     --crs EPSG:3005 \
     --allow-runs \
     --allow-agent \
     --port 8018

``PORT=...`` overrides the default. The geometry is EPSG:3005; pass
``--crs EPSG:3005`` so MapLibre can project it to WGS84. The land base is the
AOI polygon drawn under the blocks, so non-forest gaps read as land rather than
as missing map data.

The block layer still renders if the OpenStreetMap basemap tiles are
unavailable. If MapLibre cannot create a WebGL context, switch **Map engine** to
**SVG (fallback)**.

Geometry scale
--------------

The served ``fragments.geojson`` is a 100 m simplification of the block layer.
The unsimplified layer is retained as ``fragments_full.geojson``. The overview
keeps the initial map payload manageable; the full layer is the source for
viewport-detail work. The 100 m tolerance is invisible at the TSA overview
scale and preserves every block polygon.

Checks
------

- ``/health`` returns ``{"status":"ok"}``.
- The map shows the full TSA 47 AOI.
- The run list contains ``baseline`` and any benchmark runs.
- The target table shows ten decade targets and their realized values.

Do not use ``--allow-remote`` on an untrusted network. Put the service behind a
trusted proxy if it must be reachable from another host.
