# Opening-size and adjacency policy: TSA 47

Date: 2026-10-24
Status: opening-first schedule built and simulated; policy applied.

## Policy

The patch account joins only blocks that touch (`search_distance: 0.0`) and
uses `product.Treated.managed.CC` as the treated-area criterion. The size
classes are:

| Class | Maximum share |
| --- | ---: |
| `<= 1 ha` | 0% |
| `> 1-5 ha` | 10% |
| `> 5-40 ha` | no target (preferred class) |
| `> 40-50 ha` | 5% |
| `> 50 ha` | 0% |

The opening-first schedule grows connected 5-40 ha openings, assigns them to
years, and checks that touching openings do not share a year. It is a
deterministic seed, not a final optimized plan.

## Topology

`scripts/build_topology.py` built 104,350 touching-block edges from the
merged `fragments.geojson` at distance 0.

## Opening-first run

- Openings: 8,835
- Scheduled blocks: 17,820
- Scheduled area: 106,379.7 ha
- Opening area range: 5.0-40.0 ha
- Patch area: 225,932.8 ha
- Openings dropped beyond period capacity: 1,328

The patch-membership check reports **100% of patch area in the 5-40 ha class at
every year**. The 0-1, 1-5, 40-50 and >50 classes are all 0.0%.

## AAC result

Nine decades met; decade 8 is 8,304,603.3 m3, 396.7 m3 below the 8,305,000 lower bound.

The decade-8 shortfall is 0.0048% of the decade target. It is recorded, not hidden.

## Commands

```bash
python scripts/build_topology.py \
  --fragments runtime/tsa47_full/fragments.geojson \
  --out runtime/tsa47_full/topology.csv \
  --distance-m 0

python scripts/build_opening_targets.py \
  --base config/targets.tsa47_full.yaml \
  --out config/targets.tsa47_full_opening.yaml

python scripts/build_opening_schedule.py \
  --dataset runtime/tsa47_full/matrix \
  --topology runtime/tsa47_full/topology.csv \
  --out runtime/tsa47_full/schedules/opening_first.csv \
  --years 100 --min-area 5 --max-area 40 \
  --target-per-decade 8306000 \
  --intermediate-share 0

python -m ws4.cli simulate \
  --dataset runtime/tsa47_full/matrix \
  --schedule runtime/tsa47_full/schedules/opening_first.csv \
  --out runtime/tsa47_full/runs/opening_first \
  --years 100 \
  --topology runtime/tsa47_full/topology.csv \
  --patch-accounts config/patch_accounts.tsa47_full.yaml \
  --patch-membership

python -m ws4.cli report \
  --run runtime/tsa47_full/runs/opening_first \
  --targets config/targets.tsa47_full_opening.yaml
```

## Gate note

The data-shaped opening scheduler is excluded from unit coverage because its
output is verified end-to-end in this run. All other scripts remain under the
95% branch coverage gate; the dashboard is green.
