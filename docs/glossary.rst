Glossary
========

AAC
    Allowable annual cut, the legal volume of timber that may be harvested each
    year in a management unit.

AU
    Analysis unit. A stand group with the same species, site index, and
    management assumptions.

Block
    A runtime aggregation of fragments. Simulation, optimization, and reports
    operate on blocks.

Fragment
    The compiled spatial decision unit. A block can contain several fragments.

FEMIC
    Forest Estate Modelling Integration Core. The upstream compiler that builds
    inventory and yield inputs from public BC data.

GBR
    Great Bear Rainforest.

IFM
    Integrated forest management state in Patchworks. It controls treatment
    eligibility, not curve origin.

THLB
    Timber harvesting land base. The area considered available for timber
    harvesting after exclusions.

Track
    A model state combining AU, IFM, origin, silviculture state, retention, and
    treatment. The track name is the readable contract.

TSA
    Timber supply area. The primary management unit for an AAC determination.

VDYP
    Variable Density Yield Prediction. The BC natural-stand yield model. On
    Linux it runs through Wine.

ws4
    The spatially explicit wood supply simulator, optimizer, and web UI used as
    the runtime for this instance.

VRI
    Vegetation Resources Inventory. The provincial forest inventory used for
    stand attributes and polygon support.

TSR
    Timber Supply Review. The BC process and data packages used to derive the
    predecessor yield assumptions.

BatchTIPSY
    The batch driver for TIPSY. It is used here to build the managed-curve lane.

TIPSY
    Table Interpolation Program for Stand Yields. The BC stand-yield model
    behind the managed curves.

SI
    Site index. A site-productivity measure, expressed in metres in this
    project.

DBH
    Diameter at breast height. A tree-diameter measure used in the ground-plot
    validation.

MAE
    Mean absolute error. A validation error statistic.

RMSE
    Root mean square error. A validation error statistic that penalizes larger
    errors more heavily.

PSP
    Permanent sample plot. A remeasured forest inventory plot.

NFI
    National Forest Inventory. A public plot source used in validation.

CMI, YSM
    Public ground-plot source codes used in the validation tables. See the
    ground-plot validation page for their sample definitions.

EBM
    Ecosystem-based management. The GBR management framework referenced in the
    predecessor TSA documents.

GLB, AFLB, LHLB
    Gross land base, available forest land base, and long-term harvest land
    base. The successive area screens in a TSR-style netdown.

FADM
    The provincial Forest Analysis and Data Management TSA boundary layer used
    to select the current dissolved TSA feature.
