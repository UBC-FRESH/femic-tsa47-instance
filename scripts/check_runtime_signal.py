#!/usr/bin/env python3
"""Check that every compiled AU/species pair has a runtime signal.

The check reads the FEMIC model-input bundle and the ws4 matrix. For each
``(stratum_code, si_level)`` pair in the AU table it requires the matching
``feature.Area.og1`` and ``feature.Area.og2`` labels. It also requires every
track with area to carry at least one feature or product label, and every
feature/product curve id to resolve in ``curves.parquet``. When a run is given,
it requires a positive initial area for each pair.

This is a hard gate: a missing label, an orphan track, or a missing curve is a
compiled-signal defect, not a scheduling choice. The harvest-coverage check is
the separate scheduling gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

DEFAULT_BUNDLE: Path = Path("data/model_input_bundle")
PAIR_COLUMNS: tuple[str, str] = ("stratum_code", "si_level")


def check_runtime_signal(
    *,
    dataset: Path,
    bundle: Path = DEFAULT_BUNDLE,
    run: Path | None = None,
) -> dict[str, object]:
    """Check the AU labels, track signals, and initial area accounts.

    Parameters
    ----------
    dataset : Path
        Compiled ws4 dataset directory.
    bundle : Path, optional
        FEMIC model-input bundle that contains ``au_table.csv``.
    run : Path or None, optional
        A ws4 run directory with ``account_values.csv``. When given, each
        species/SI pair must have a positive initial area.

    Returns
    -------
    dict of str to object
        A JSON-ready summary with ``status``, the missing labels, the orphan
        tracks, the missing curve ids, and the zero-area labels.

    Raises
    ------
    FileNotFoundError
        When the bundle, dataset, or run input is missing.
    ValueError
        When the AU table lacks a required column.
    """
    au = pd.read_csv(bundle / "au_table.csv")
    for column in PAIR_COLUMNS:
        if column not in au.columns:
            raise ValueError(f"au_table.csv is missing {column!r}")
    features = pd.read_parquet(dataset / "features.parquet")
    products = pd.read_parquet(dataset / "products.parquet")
    curves = pd.read_parquet(dataset / "curves.parquet")
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    tracks = pd.read_parquet(dataset / "tracks.parquet")

    labels = {str(value) for value in features["label"].tolist()}
    curve_ids = {int(value) for value in curves["curve_id"].tolist()}

    missing_labels: list[str] = []
    pairs = au.loc[:, list(PAIR_COLUMNS)].drop_duplicates()
    for _, row in pairs.iterrows():
        for origin in ("og1", "og2"):
            label = f"feature.Area.{origin}.{row['stratum_code']}_{row['si_level']}"
            if label not in labels:
                missing_labels.append(label)

    area_by_track = fragments.groupby("track_id")["area_ha"].sum()
    tracks_with_area = {
        int(str(value)) for value, area in area_by_track.items() if float(area) > 0.0
    }
    signalled_tracks = {int(value) for value in features["track_id"].tolist()}
    signalled_tracks.update(int(value) for value in products["track_id"].tolist())
    orphan_tracks = sorted(tracks_with_area.difference(signalled_tracks))
    track_names = dict(
        zip(tracks["track_id"].astype(int), tracks["name"].astype(str), strict=False)
    )

    missing_curves: list[int] = []
    for frame in (features, products):
        for value in frame["curve_id"].dropna().tolist():
            curve_id = int(str(value))
            if curve_id not in curve_ids:
                missing_curves.append(curve_id)

    zero_area: list[str] = []
    if run is not None:
        account_values = pd.read_csv(run / "account_values.csv")
        initial = account_values.loc[account_values["offset"] == -1]
        for _, row in pairs.iterrows():
            label = f"feature.Area.og1.{row['stratum_code']}_{row['si_level']}"
            match = initial.loc[initial["account"] == label]
            if match.empty or float(match["value"].iloc[0]) <= 0.0:
                zero_area.append(label)

    errors = len(missing_labels) + len(orphan_tracks) + len(missing_curves) + len(zero_area)
    return {
        "status": "ok" if errors == 0 else "error",
        "dataset": str(dataset),
        "bundle": str(bundle),
        "run": str(run) if run is not None else None,
        "pair_count": len(pairs),
        "track_count": len(tracks_with_area),
        "missing_labels": sorted(set(missing_labels)),
        "orphan_tracks": [
            {"track_id": track_id, "name": track_names.get(track_id, "")}
            for track_id in orphan_tracks
        ],
        "missing_curves": sorted(set(missing_curves)),
        "zero_area": sorted(set(zero_area)),
        "error_count": errors,
    }


def main() -> None:
    """Run the runtime-signal check and exit non-zero on an error."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--run", type=Path, default=None)
    args = parser.parse_args()
    summary = check_runtime_signal(
        dataset=args.dataset,
        bundle=args.bundle,
        run=args.run,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
