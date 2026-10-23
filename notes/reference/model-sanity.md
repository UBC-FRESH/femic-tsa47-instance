# Model sanity audit

Date: 2026-10-23
Dataset: `runtime/tsa47_full/matrix`
Benchmark: `runtime/tsa47_full/runs/aac_benchmark`

## Species composition

Initial `feature.Area.og1.*` area by species:

| Species | Area (ha) | Share |
| --- | ---: | ---: |
| CWH_CW | 162,887.0 | 37.3% |
| CWH_HW | 132,610.9 | 30.3% |
| CWH_YC | 56,471.4 | 12.9% |
| MH_HM | 49,681.9 | 11.4% |
| CWH_BA | 18,239.8 | 4.2% |
| CWH_FD | 17,180.9 | 3.9% |

The mix is coastal CWH/MH, consistent with the GBR South inventory. The
compiled species areas sum to the og1 area, and every species has a nonzero
area account.

## Managed area

- Block area: 692,811.84 ha.
- Managed area: 145,256.00 ha (21.0% of block area).
- Managed share of og1 area: 33.2%.

## Benchmark

- Unique blocks harvested: 3,872.
- Harvested area: 103,818.3 ha over 100 years (71% of the managed area).
- Events: 5,327 across offsets 0-99.
- All ten decade targets met at 8,305,000-8,306,000 m3.

## Finding: zero-harvest AUs

Three AUs have managed area but no benchmark harvest:

| AU | Managed area (ha) | Total area (ha) |
| --- | ---: | ---: |
| 4701002 | 139.2 | 20,768.9 |
| 4702004 | 40.7 | 18,424.0 |
| 4701005 | 111.4 | 8,246.2 |

Total managed area with no harvest: **291.2 ha (0.20% of the managed area)**.

The benchmark is volume-feasible without these AUs. The zero signal is recorded
as a known limitation, not a build failure. A follow-up should either schedule
a minimum share of these AUs or document why they are economically or
operationally excluded.

## Coverage run

`runtime/tsa47_full/runs/aac_benchmark_coverage/` is a coverage diagnostic, not
the benchmark of record. It starts from the strict benchmark and adds one
harvest event for each of the two AUs above the 100 ha threshold, then
re-optimizes.

- Both AUs are covered: 4701002 (9.1 ha) and 4701005 (0.9 ha).
- All ten decades meet the strict band; objective is approximately 0.
- 3,974 blocks are scheduled.
- 4702004 is 40.7 ha, below the 100 ha threshold, and remains unharvested.

## Status

Pass. The compiled runtime signal is complete, and the coverage run selects both
AUs above the threshold while meeting all ten AAC decades.
