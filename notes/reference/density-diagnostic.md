# Density and mortality diagnostic: TSA 47

Date: 2026-10-25
Status: scenario diagnostic complete; production unchanged.

## Purpose

Test whether the managed-stand stem gap is explained by initial density.

The density scenarios change only the initial planted density for the AUs in
the managed ground-plot sample (`23000`, `23001`, `23003`, `23005`). Species,
SI, and OAFs are unchanged. VRI audit plots are kept separate from the managed
YSM/CMI/NFI sample.

## Scenarios

- 1.0x: current TSR input, 1,000 stems/ha.
- 1.5x: 1,500 stems/ha.
- 2.0x: 2,000 stems/ha.

Each scenario was run through BTC with `stand-structure-basic` and validated
against the same 506-row ground-plot table.

## Results

### Managed YSM sample (n=11)

| Scenario | Volume bias | DBH bias | Height bias | Stems bias |
| --- | ---: | ---: | ---: | ---: |
| 1.0x | -44.5 m3/ha | -4.0 cm | -2.1 m | -276.8 sph |
| 1.5x | -33.8 m3/ha | -5.4 cm | -2.1 m | -153.5 sph |
| 2.0x | -30.0 m3/ha | -6.4 cm | -2.1 m | -99.3 sph |

### VRI audit sample (n=480)

| Scenario | Volume bias | DBH bias | Height bias | Stems bias |
| --- | ---: | ---: | ---: | ---: |
| 1.0x | -45.6 m3/ha | -4.4 cm | -1.2 m | -103.1 sph |
| 1.5x | -33.3 m3/ha | -6.4 cm | -1.2 m | +33.5 sph |
| 2.0x | -28.6 m3/ha | -7.4 cm | -1.2 m | +97.8 sph |

### CMI and NFI

- CMI: volume -111.8 / -100.1 / -95.6; stems -327.1 / -212.1 / -152.5.
- NFI: volume -239.4 / -224.0 / -219.1; stems -156.0 / +0.4 / +70.4.

## Interpretation

Higher density reduces the stem and volume gaps but makes DBH **worse** and
does not fix height. It is a partial lever, not a clean correction.

The YSM sample is heterogeneous: observed stems range from 50 to 1,751 sph. A
single density multiplier cannot represent that. The remaining explanation is
mortality/ingrowth and species/establishment composition, not density alone.

VRI audits overcorrect quickly under higher density and should remain a
separate management-origin class.

No production curve or AAC target was changed.

## Files

- `config/tsr/tipsy_ground_plot_validation_density_1.5.tsa47.csv`
- `config/tsr/tipsy_ground_plot_validation_density_2.0.tsa47.csv`
- Corresponding `*_summary.tsa47.csv`
- `notes/reference/tipsy-validation.md`
