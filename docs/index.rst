Great Bear Rainforest South TSA 47 Instance
===========================================

Standalone FEMIC and ws4 model instance for the Great Bear Rainforest South Timber Supply
Area, TSA 47. FEMIC rebuilds the public inventory and yield curves from
public BC data; ws4 compiles the model, runs the AAC benchmark, and serves the
web UI.

This site is the RTFM surface for the project. Read ``AGENTS.md`` and
``ROADMAP.md`` before changing the model, and use the reproduction guide when
you need to rebuild it. Read :doc:`limitations` before using the model output.

Status
------

The calibrated model is built. The runtime-signal and harvest-coverage gates,
the opening policy, and the TSR-consistent BatchTIPSY curves are in place, and
an independent height validation has been run. The remaining work is the
reviewed GBR land-base netdown, volume/DBH/mortality validation, and the release
verification.

Model at a glance
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 55

   * - Quantity
     - Value
   * - Boundary
     - TSA 47, current dissolved FADM feature
   * - Gross AOI area
     - 1,991.8 thousand ha
   * - Published AAC
     - 830,500 m3/yr
   * - Calibrated THLB
     - 145.3 thousand ha
   * - Blocks
     - 73,659
   * - Block area
     - 692.8 thousand ha
   * - AUs / curves
     - 18 / 73
   * - Managed curves
     - TSR-consistent BatchTIPSY
   * - AAC benchmark
     - 10/10 decades met
   * - Web UI
     - loopback port 8018

Runtime lane
------------

.. code-block:: text

   public BC data
     -> FEMIC run
     -> FEMIC Patchworks export (XML + fragments)
     -> ws4 build / validate
     -> ws4 simulate / optimize / report
     -> ws4 serve

ws4 is the runtime. The Patchworks XML and fragments are an interchange pair
for ``ws4 build``, not a second runtime lane.

Documentation map
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Guides

   aoi
   public-data
   model-build
   runtime-provenance
   model-structure
   benchmark
   ground-plot-validation
   ground-plot-preregistration
   web-ui
   reproduce
   decisions
   limitations
   glossary

.. toctree::
   :maxdepth: 2
   :caption: API reference

   api/index

Related instance
----------------

The sibling model is `Great Bear Rainforest North TSA 46 <https://github.com/UBC-FRESH/femic-tsa46-instance>`_.
The two are deliberately related but independent; neither repository imports the
other. See ``notes/reference/related-instances.md``.

Citation and license
--------------------

Cite the repository and the upstream FEMIC and ws4 software. The instance is
released under the MIT license; see ``CITATION.cff`` and ``LICENSE``.
