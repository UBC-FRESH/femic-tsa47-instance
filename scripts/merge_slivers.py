#!/usr/bin/env python3
"""Merge safe geometric slivers into touching neighbour blocks.

The tool works on the FEMIC fragments shapefile, before ``ws4 build``. It only
merges a small block when the merge preserves the model semantics:

- the block is below the cutoff and has ``RETENTION == 0``;
- a touching neighbour block exists;
- the neighbour has the same AU, IFM, and ORIGIN;
- the area-weighted age differs by at most the age tolerance;
- the neighbour has ``RETENTION == 0``.

Retention/IFM split fragments are never merged. Isolated small blocks are kept.
The output shapefile has the same columns, with merged area and area-weighted
age on the host fragment. Net area is preserved by summing ``AREA_HA``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.validation import make_valid

REQUIRED_COLUMNS: tuple[str, ...] = (
    "FRAGMENT_I",
    "BLOCK",
    "AREA_HA",
    "F_AGE",
    "AU",
    "IFM",
    "ORIGIN",
    "SILV_STATE",
    "RETENTION",
    "TSA",
    "geometry",
)


def _valid(geometry: BaseGeometry) -> BaseGeometry:
    """Return a valid geometry, repairing invalid input."""
    if not geometry.is_valid:
        return make_valid(geometry)
    return geometry


def _block_table(fragments: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return one row per block with area, area-weighted age, and attributes."""
    frame = fragments.copy()
    frame["_age_area"] = frame["F_AGE"] * frame["AREA_HA"]
    frame["_ret_area"] = frame["RETENTION"] * frame["AREA_HA"]
    grouped = frame.groupby("BLOCK", as_index=False).agg(
        area=("AREA_HA", "sum"),
        age_area=("_age_area", "sum"),
        ret_area=("_ret_area", "sum"),
        AU=("AU", "first"),
        IFM=("IFM", "first"),
        ORIGIN=("ORIGIN", "first"),
        SILV_STATE=("SILV_STATE", "first"),
        nfrag=("FRAGMENT_I", "size"),
    )
    grouped["age"] = grouped["age_area"] / grouped["area"]
    grouped["retention"] = grouped["ret_area"] / grouped["area"]
    geometry = frame.dissolve(by="BLOCK", as_index=False).loc[:, ["BLOCK", "geometry"]]
    blocks = grouped.merge(geometry, on="BLOCK", how="left")
    return gpd.GeoDataFrame(blocks, geometry="geometry", crs=fragments.crs)


def _candidate_host(
    candidate: pd.Series,
    blocks: gpd.GeoDataFrame,
    *,
    age_tolerance: float,
) -> tuple[int | None, str]:
    """Return the host block id and a skip reason, or ``(None, reason)``."""
    geometry = candidate.geometry
    index = blocks.sindex
    candidates = list(index.query(geometry, predicate="intersects"))
    best_id: int | None = None
    best_length = 0.0
    for position in candidates:
        other = blocks.iloc[position]
        if int(other["BLOCK"]) == int(candidate["BLOCK"]):
            continue
        try:
            shared = geometry.intersection(other.geometry).length
        except Exception:
            continue
        if shared > best_length:
            best_length = shared
            best_id = int(other["BLOCK"])
    if best_id is None:
        return None, "no_touching_neighbour"
    host = blocks.loc[blocks["BLOCK"] == best_id].iloc[0]
    if str(host["AU"]) != str(candidate["AU"]):
        return None, "different_au"
    if str(host["IFM"]) != str(candidate["IFM"]):
        return None, "different_ifm"
    if str(host["ORIGIN"]) != str(candidate["ORIGIN"]):
        return None, "different_origin"
    if abs(float(host["age"]) - float(candidate["age"])) > age_tolerance:
        return None, "age_difference"
    if float(host["retention"]) > 0.0 or float(candidate["retention"]) > 0.0:
        return None, "retention"
    return best_id, ""


def merge_slivers(
    *,
    fragments_path: Path,
    out_path: Path,
    cutoff_ha: float = 1.0,
    age_tolerance: float = 20.0,
) -> dict[str, object]:
    """Merge safe slivers and write the cleaned fragments.

    Parameters
    ----------
    fragments_path : Path
        FEMIC fragments shapefile.
    out_path : Path
        Destination shapefile.
    cutoff_ha : float, optional
        Block area below which a merge is considered.
    age_tolerance : float, optional
        Largest allowed area-weighted age difference, in years.

    Returns
    -------
    dict of str to object
        Counts, merged area, skipped reasons, and the net-area check.

    Raises
    ------
    ValueError
        When a required column is missing or the output would lose area.
    """
    fragments = gpd.read_file(fragments_path)
    missing = [column for column in REQUIRED_COLUMNS if column not in fragments.columns]
    if missing:
        raise ValueError(f"fragments shapefile is missing {missing}")
    fragments["BLOCK"] = fragments["BLOCK"].astype(int)
    fragments["FRAGMENT_I"] = fragments["FRAGMENT_I"].astype(int)
    fragments["AREA_HA"] = fragments["AREA_HA"].astype(float)
    fragments["F_AGE"] = fragments["F_AGE"].astype(float)
    fragments["RETENTION"] = fragments["RETENTION"].astype(float)
    fragments["geometry"] = fragments["geometry"].apply(_valid)
    blocks = _block_table(fragments)
    candidates = blocks.loc[blocks["area"] < cutoff_ha].sort_values("area")
    candidate_ids = set(candidates["BLOCK"].astype(int).tolist())
    host_by_block: dict[int, int] = {}
    skipped: dict[str, int] = {}
    merged_area = 0.0
    for _, candidate in candidates.iterrows():
        host_id, reason = _candidate_host(candidate, blocks, age_tolerance=age_tolerance)
        if host_id is None:
            skipped[reason] = skipped.get(reason, 0) + 1
            continue
        if int(host_id) in candidate_ids:
            skipped["host_is_candidate"] = skipped.get("host_is_candidate", 0) + 1
            continue
        host_by_block[int(candidate["BLOCK"])] = host_id
        merged_area += float(candidate["area"])

    if not host_by_block:
        fragments.to_file(out_path)
        return {
            "input_fragments": len(fragments),
            "input_blocks": int(fragments["BLOCK"].nunique()),
            "cutoff_ha": cutoff_ha,
            "candidates": len(candidates),
            "merged_blocks": 0,
            "merged_area_ha": 0.0,
            "skipped": skipped,
            "output_fragments": len(fragments),
            "output_blocks": int(fragments["BLOCK"].nunique()),
            "area_before_ha": round(float(fragments["AREA_HA"].sum()), 6),
            "area_after_ha": round(float(fragments["AREA_HA"].sum()), 6),
        }

    # Host fragment is the largest fragment in the host block.
    host_rows: dict[int, int] = {}
    for host_id, group in fragments.loc[
        fragments["BLOCK"].isin(set(host_by_block.values()))
    ].groupby("BLOCK"):
        host_rows[int(host_id)] = int(group.sort_values("AREA_HA", ascending=False).index[0])

    area_before = float(fragments["AREA_HA"].sum())
    drop_rows: list[int] = []
    for candidate_id, host_id in host_by_block.items():
        host_row = host_rows[host_id]
        candidate_rows = fragments.index[fragments["BLOCK"] == candidate_id].tolist()
        host = fragments.loc[host_row]
        host_area = float(host["AREA_HA"])
        host_age_area = host_area * float(host["F_AGE"])
        host_geometry = host.geometry
        for row in candidate_rows:
            current = fragments.loc[row]
            area = float(current["AREA_HA"])
            host_area += area
            host_age_area += area * float(current["F_AGE"])
            host_geometry = unary_union([host_geometry, current.geometry])
            drop_rows.append(row)
        fragments.at[host_row, "AREA_HA"] = host_area
        fragments.at[host_row, "F_AGE"] = host_age_area / host_area
        fragments.at[host_row, "geometry"] = host_geometry

    cleaned = fragments.drop(index=drop_rows).copy()
    area_after = float(cleaned["AREA_HA"].sum())
    if abs(area_before - area_after) > 1e-6:
        raise ValueError(f"net area changed from {area_before} to {area_after}; refusing to write")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_file(out_path)
    return {
        "input_fragments": len(fragments),
        "input_blocks": int(fragments["BLOCK"].nunique()),
        "cutoff_ha": cutoff_ha,
        "candidates": len(candidates),
        "merged_blocks": len(host_by_block),
        "merged_area_ha": round(merged_area, 6),
        "skipped": skipped,
        "output_fragments": len(cleaned),
        "output_blocks": int(cleaned["BLOCK"].nunique()),
        "area_before_ha": round(area_before, 6),
        "area_after_ha": round(area_after, 6),
    }


def main() -> None:
    """Run the merge and print its summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cutoff-ha", type=float, default=1.0)
    parser.add_argument("--age-tolerance", type=float, default=20.0)
    args = parser.parse_args()
    summary = merge_slivers(
        fragments_path=args.fragments,
        out_path=args.out,
        cutoff_ha=args.cutoff_ha,
        age_tolerance=args.age_tolerance,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
