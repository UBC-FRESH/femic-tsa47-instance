# Sliver and small-fragment analysis: TSA 47

Date: 2026-10-24
Dataset: `runtime/tsa47_full/matrix`
Source geometry: `output/patchworks_tsa47_full/fragments/fragments.shp`

## Headline

- **Block-level small polygons are a modest problem.** 3,462 blocks
  are below 1 ha (4.7% of blocks, 2,046.1 ha,
  0.30% of area).
- **Fragment-level small fragments are a larger problem.** 13,827
  fragments are below 1 ha (14.1% of fragments,
  6,720.9 ha, 0.97% of area).
- **Most of the extra small fragments are not VRI slivers.** 10,682
  small fragments sit in multi-fragment blocks, and **100% of them carry
  RETENTION > 0**. They are the unmanaged/retention remainder of the IFM
  proportional split. Merging them would erase the retention signal.
- A blanket <1 ha merge would change the AU/species of 63.6% of
  the moved area and the IFM state of 27.4%. That is not a safe
  cleanup.

## Block-level size distribution

| Bin (ha) | Blocks | Share of blocks | Area (ha) | Share of area |
| --- | ---: | ---: | ---: | ---: |
| 0-0.1 | 126 | 0.2% | 7.2 | 0.00% |
| 0.1-0.25 | 389 | 0.5% | 68.9 | 0.01% |
| 0.25-0.5 | 762 | 1.0% | 288.6 | 0.04% |
| 0.5-0.75 | 969 | 1.3% | 610.8 | 0.09% |
| 0.75-1 | 1,216 | 1.6% | 1,070.5 | 0.15% |
| 1-1.25 | 2,438 | 3.3% | 2,739.3 | 0.40% |
| 1.25-1.5 | 2,444 | 3.3% | 3,358.3 | 0.48% |
| 1.5-2 | 4,702 | 6.3% | 8,234.6 | 1.19% |
| 2-5 | 21,777 | 29.4% | 73,032.5 | 10.54% |
| 5-10 | 18,170 | 24.5% | 130,223.0 | 18.80% |
| 10-20 | 13,313 | 17.9% | 186,325.5 | 26.89% |
| 20-50 | 6,743 | 9.1% | 196,974.1 | 28.43% |
| 50-1e+07 | 1,121 | 1.5% | 89,878.5 | 12.97% |

The block-level mode is **0.88-0.90 ha (116 blocks)**, not a low-end spike. The
distribution rises toward 1 ha and then jumps across the VRI minimum-mapping
edge.

## Fragment-level size distribution

The low-end fragment mode is **0.04-0.06 ha (487 fragments)**. The exact edge at 1 ha is
sharp: **0.98-1.0 ha: 337; 1.0-1.02 ha: 383**. That is a genuine cutoff flip point: 1.0 ha is the VRI
minimum-mapping-unit edge, and the population just above it is larger than the
population just below it.

| Bin (ha) | Fragments | Share of fragments | Area (ha) | Share of area |
| --- | ---: | ---: | ---: | ---: |
| 0-0.1 | 1,869 | 1.9% | 110.8 | 0.02% |
| 0.1-0.25 | 2,623 | 2.7% | 440.8 | 0.06% |
| 0.25-0.5 | 2,619 | 2.7% | 968.5 | 0.14% |
| 0.5-0.75 | 2,855 | 2.9% | 1,795.9 | 0.26% |
| 0.75-1 | 3,861 | 3.9% | 3,404.9 | 0.49% |
| 1-1.25 | 4,362 | 4.4% | 4,892.6 | 0.71% |
| 1.25-1.5 | 3,963 | 4.0% | 5,444.0 | 0.79% |
| 1.5-2 | 7,268 | 7.4% | 12,696.2 | 1.83% |
| 2-5 | 28,354 | 28.9% | 93,757.7 | 13.53% |
| 5-10 | 20,241 | 20.6% | 144,037.9 | 20.79% |
| 10-20 | 13,238 | 13.5% | 183,341.9 | 26.46% |
| 20-50 | 5,891 | 6.0% | 170,241.0 | 24.57% |
| 50-1e+07 | 896 | 0.9% | 71,679.5 | 10.35% |

## Threshold table

| Cutoff | Blocks below | Block area (ha) | Fragments below | Fragment area (ha) |
| --- | ---: | ---: | ---: | ---: |
| <0.1 ha | 126 | 7.2 | 1,869 | 110.8 |
| <0.25 ha | 515 | 76.2 | 4,492 | 551.6 |
| <0.5 ha | 1,277 | 364.8 | 7,111 | 1,520.1 |
| <0.75 ha | 2,246 | 975.6 | 9,966 | 3,316.0 |
| <1 ha | 3,462 | 2,046.1 | 13,827 | 6,720.9 |

## What is in the small fragments?

| Attribute | Finding |
| --- | --- |
| RETENTION > 0 | **100%** of small fragments in multi-fragment blocks; 72.9% of all small-fragment area |
| Managed (THLB) | 222.9 ha (10.9%) |
| Old growth (>250 years) | 49.7% of small-block area |
| Species unique to small fragments | None; every species also occurs above 1 ha |
| AU/species unique in block | Blocks are AU-specific, so a small block is the block's AU by construction |
| No touching neighbour | 710 blocks, 462.1 ha |

The retention result is the important one. These are not stray VRI polygons.
They are the unmanaged remainder created when the IFM proportional split assigns
a share of a stand to retention. They carry model semantics.

## Merge simulation

For each small block, the analysis found touching neighbours and selected the
neighbour with the longest shared boundary. The "safe" merge requires the same
AU, same IFM, same origin, age difference at most 20 years, and a neighbour with
RETENTION = 0.

| Measure | Value |
| --- | ---: |
| Small blocks | 3,462 |
| With a touching neighbour | 2,752 (77.4% of area) |
| Same AU + IFM | 870 (466.9 ha, 29.5% of merged area) |
| Different AU | 1,008.0 ha (63.6%) |
| Different IFM | 434.3 ha (27.4%) |
| Same age | 29.6% of merged area |
| Mean age difference | 90.5 years |
| No touching neighbour | 710 blocks (462.1 ha) |

Safe merge candidates:

| Cutoff | Safe blocks | Safe area (ha) | Block reduction | Fragment reduction |
| --- | ---: | ---: | ---: | ---: |
| <0.25 ha | 131 | 17.9 | 0.18% | 0.13% |
| <0.5 ha | 283 | 73.3 | 0.38% | 0.29% |
| <1.0 ha | 564 | 279.0 | 0.76% | 0.58% |

An aggressive merge of every small block with a touching neighbour would remove
2,752 blocks (3.7% of blocks)
and 2,752 fragments
(2.8% of fragments), but it would relabel
63.6% of the moved area to a different AU/species and
27.4% to a different IFM state. That is not recommended.

## Recommendation

1. **Do not use a blanket <1 ha merge.** The 1.0 ha edge is real, but it is the
   VRI minimum-mapping edge, not a sliver-only edge. A blanket cutoff would
   remove legitimate small stands and retention fragments.
2. **Use a two-threshold policy.**
   - **0.25 ha**: mandatory geometric sliver cleanup. Merge only into a
     touching neighbour with the same AU, IFM, origin, and similar age. This
     removes 325/131 blocks and 43.4/17.9 ha.
   - **0.5 ha**: upper bound for the same safe merge. This removes 740/283
     blocks and 197.9/73.3 ha.
   - **1.0 ha**: do not merge by default; only merge if the full safe rule holds.
     That removes 2,486/564 blocks and 1,488.5/279.0 ha.
3. **Never merge the retention/IFM split fragments.** They are
   10,682 fragments (10.9% of all fragments)
   and 100% RETENTION > 0. If the goal is model size, change how retention is
   represented (block-level area share/account) rather than deleting the
   fragments.
4. **Keep isolated small blocks.** 710 blocks (462.1 ha)
   have no touching neighbour. Do not delete them; they are real area.
5. **Do not tune the 0-1 ha opening weights to hide this.** The 0-1 ha openings
   may be dominated by retention fragments. Fix the geometry where it is safe,
   and represent retention explicitly.

## Expected gain

The safe geometric cleanup at 1.0 ha removes 564 blocks
(0.76%) and roughly 0.58% of fragments. The
larger opportunity is the retention representation: 10,682
fragments (10.9%) are retention/IFM splits, not slivers.

## MKRF cross-check

The MKRF PoC shapefile has 1,763 fragments; 35.6% are <1 ha and 5.8% of the area. It is PoC-scale, not the production inventory.

## Reproduction

The analysis uses the compiled `fragments.parquet` and `blocks.parquet`, joins
the track names for `IFM`/`ORIGIN`/`RETENTION`, and uses the fragment shapefile
for adjacency.

```bash
python - <<'PY'
import pandas as pd
f = pd.read_parquet("runtime/tsa47_full/matrix/fragments.parquet")
print((f.area_ha < 1.0).mean())
print(f.area_ha[f.area_ha < 1.0].sum())
PY
```

The spatial merge analysis reads
`output/patchworks_tsa47_full/fragments/fragments.shp`, builds the block
attributes, and queries touching neighbours with the GeoPandas spatial index.

## Applied

On 2026-10-24 the safe merge was adopted at the 1.0 ha cutoff with the strict
same-AU/IFM/origin, age-within-20-years, and neighbour-retention-zero rule.

- Blocks merged: 511; area merged: 255.78 ha; net area change: 0.0 ha.
- Blocks after merge: 73,659; compiled fragments: 97,529.
- Strict AAC benchmark: 3,872 blocks, all ten decades met.
- Coverage run: 3,951 blocks, all ten decades met; the remaining unselected
  AUs are allowlisted and covered by the coverage run.
- Retention/IFM split fragments were not merged.
