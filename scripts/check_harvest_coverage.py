#!/usr/bin/env python3
"""Check that managed AUs above a threshold appear in a harvest schedule.

The compiled model can carry a nonzero managed area for an AU that a particular
volume-only benchmark never selects. That is a scheduling choice, not a
compiled-signal defect. This gate makes the choice explicit: every AU with at
least ``--min-managed-ha`` of managed area must have a harvest event in the
schedule, or an allowlist entry with a reason.

The allowlist is JSON::

    {"aus": [{"au": "4601004", "reason": "not selected by the strict benchmark"}]}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

DEFAULT_MIN_MANAGED_HA: float = 100.0
AU_PATTERN: str = r"AU\((\d+)\)"
IFM_PATTERN: str = r"IFM\((\w+)\)"


def load_allowlist(path: Path | None) -> dict[str, str]:
    """Read an AU allowlist and return a mapping of AU to reason.

    Parameters
    ----------
    path : Path or None
        JSON allowlist with an ``aus`` list. ``None`` returns an empty map.

    Returns
    -------
    dict of str to str
        Each allowed AU mapped to its reason.

    Raises
    ------
    ValueError
        When the document does not contain an ``aus`` list.
    """
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    entries = document.get("aus")
    if not isinstance(entries, list):
        raise ValueError(f"{path} must contain an 'aus' list")
    allowed: dict[str, str] = {}
    for entry in entries:
        au = str(entry["au"])
        allowed[au] = str(entry.get("reason", ""))
    return allowed


def _managed_area_by_au(dataset: Path) -> pd.Series:
    """Return the managed area in hectares for each AU.

    Parameters
    ----------
    dataset : Path
        Compiled ws4 dataset directory.

    Returns
    -------
    pandas.Series
        Managed area indexed by AU code.
    """
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    tracks = pd.read_parquet(dataset / "tracks.parquet")
    tracks = tracks.copy()
    tracks["au"] = tracks["name"].astype(str).str.extract(AU_PATTERN)[0]
    tracks["ifm"] = tracks["name"].astype(str).str.extract(IFM_PATTERN)[0]
    joined = fragments.merge(tracks.loc[:, ["track_id", "au", "ifm"]], on="track_id", how="left")
    managed = joined.loc[joined["ifm"] == "managed"]
    return managed.groupby("au")["area_ha"].sum().sort_index()


def _harvested_area_by_au(dataset: Path, schedule: Path) -> pd.Series:
    """Return the harvested area in hectares for each AU.

    Parameters
    ----------
    dataset : Path
        Compiled ws4 dataset directory.
    schedule : Path
        Schedule CSV with a ``block_id`` column.

    Returns
    -------
    pandas.Series
        Harvested area indexed by AU code. Blocks without an AU are dropped.
    """
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    tracks = pd.read_parquet(dataset / "tracks.parquet")
    tracks = tracks.copy()
    tracks["au"] = tracks["name"].astype(str).str.extract(AU_PATTERN)[0]
    joined = fragments.merge(tracks.loc[:, ["track_id", "au"]], on="track_id", how="left")
    block = joined.groupby("block_id", as_index=False).agg(
        area_ha=("area_ha", "sum"), au=("au", "first")
    )
    scheduled = pd.read_csv(schedule)
    selected = block.loc[block["block_id"].isin(scheduled["block_id"].unique())]
    return selected.groupby("au")["area_ha"].sum().sort_index()


def check_harvest_coverage(
    *,
    dataset: Path,
    schedule: Path,
    min_managed_ha: float = DEFAULT_MIN_MANAGED_HA,
    allowlist: Path | None = None,
) -> dict[str, object]:
    """Check the schedule's AU coverage against the managed area.

    Parameters
    ----------
    dataset : Path
        Compiled ws4 dataset directory.
    schedule : Path
        Schedule CSV to check.
    min_managed_ha : float, optional
        Smallest managed area that must be covered.
    allowlist : Path or None, optional
        JSON allowlist of intentional exclusions.

    Returns
    -------
    dict of str to object
        A JSON-ready summary with ``status``, the uncovered AUs, and the
        allowed exclusions.

    Raises
    ------
    ValueError
        When the allowlist is malformed.
    """
    managed = _managed_area_by_au(dataset)
    harvested = _harvested_area_by_au(dataset, schedule)
    allowed = load_allowlist(allowlist)
    uncovered: list[dict[str, object]] = []
    for au, area in managed.items():
        if float(area) < min_managed_ha:
            continue
        if float(harvested.get(au, 0.0)) > 0.0:
            continue
        uncovered.append(
            {
                "au": str(au),
                "managed_area_ha": round(float(area), 4),
                "allowed": str(au) in allowed,
                "reason": allowed.get(str(au), ""),
            }
        )
    unexpected = [item for item in uncovered if not item["allowed"]]
    return {
        "status": "ok" if not unexpected else "error",
        "dataset": str(dataset),
        "schedule": str(schedule),
        "min_managed_ha": min_managed_ha,
        "au_count": len(managed),
        "uncovered": uncovered,
        "unexpected_count": len(unexpected),
        "allowlist": str(allowlist) if allowlist is not None else None,
    }


def main() -> None:
    """Run the coverage check and exit non-zero on an unexpected gap."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--min-managed-ha", type=float, default=DEFAULT_MIN_MANAGED_HA)
    parser.add_argument("--allowlist", type=Path, default=None)
    args = parser.parse_args()
    summary = check_harvest_coverage(
        dataset=args.dataset,
        schedule=args.schedule,
        min_managed_ha=args.min_managed_ha,
        allowlist=args.allowlist,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
