#!/usr/bin/env python3
"""Replace treated curves in a FEMIC bundle with parsed BatchTIPSY curves.

The FEMIC bundle stores long-format curve points. This script maps each
``source_managed_local_au_id`` to its ``treated_curve_id``, interpolates the
BTC output to annual ages 1-300, and rewrites only the treated-curve rows.
Untreated curves, AU rows, and curve metadata are copied unchanged.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


def build_treated_curve_points(
    *,
    au_table: pd.DataFrame,
    curves: pd.DataFrame,
    min_age: int = 1,
    max_age: int = 300,
) -> pd.DataFrame:
    """Return annual treated-curve points for every managed AU.

    Parameters
    ----------
    au_table : pandas.DataFrame
        FEMIC AU table with ``source_managed_local_au_id`` and
        ``treated_curve_id``.
    curves : pandas.DataFrame
        Long-format BTC curves with ``AU``, ``Age``, and ``Yield``.
    min_age, max_age : int
        Inclusive annual age range to write.

    Returns
    -------
    pandas.DataFrame
        Columns ``curve_id``, ``x``, and ``y``.
    """
    required = {"AU", "Age", "Yield"}
    missing = required - set(curves.columns)
    if missing:
        raise ValueError(f"BTC curves are missing columns: {sorted(missing)}")
    curve_map = {
        int(local_au): int(curve_id)
        for local_au, curve_id in zip(
            au_table["source_managed_local_au_id"],
            au_table["treated_curve_id"],
            strict=False,
        )
        if pd.notna(local_au) and pd.notna(curve_id)
    }
    if not curve_map:
        raise ValueError("AU table has no managed AU-to-curve mappings")
    ages = np.arange(int(min_age), int(max_age) + 1)
    points: list[pd.DataFrame] = []
    for local_au, curve_id in curve_map.items():
        series = curves[curves["AU"].astype(int) == local_au].sort_values("Age")
        if series.empty:
            raise ValueError(f"BTC curves are missing managed AU {local_au}")
        values = np.interp(
            ages,
            series["Age"].to_numpy(dtype=float),
            series["Yield"].to_numpy(dtype=float),
            left=0.0,
            right=float(series["Yield"].iloc[-1]),
        )
        points.append(
            pd.DataFrame(
                {
                    "curve_id": curve_id,
                    "x": ages,
                    "y": np.round(values, 4),
                }
            )
        )
    return pd.concat(points, ignore_index=True)


def replace_treated_curves(
    *,
    bundle_dir: Path,
    curves_path: Path,
    output_dir: Path,
) -> Path:
    """Copy a bundle and replace its treated-curve points.

    Parameters
    ----------
    bundle_dir : Path
        Source bundle with ``au_table.csv``, ``curve_table.csv``, and
        ``curve_points_table.csv``.
    curves_path : Path
        Long-format BTC curve CSV.
    output_dir : Path
        Destination bundle directory. Existing content is replaced.

    Returns
    -------
    Path
        The destination bundle directory.
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(bundle_dir, output_dir)
    au_table = pd.read_csv(bundle_dir / "au_table.csv")
    curve_points = pd.read_csv(bundle_dir / "curve_points_table.csv")
    curves = pd.read_csv(curves_path)
    treated = build_treated_curve_points(au_table=au_table, curves=curves)
    curve_ids = set(treated["curve_id"].astype(int))
    kept = curve_points[~curve_points["curve_id"].astype(int).isin(curve_ids)]
    combined = (
        pd.concat([kept, treated], ignore_index=True)
        .sort_values(["curve_id", "x"])
        .reset_index(drop=True)
    )
    if combined.duplicated(["curve_id", "x"]).any():
        raise ValueError("Replacement created duplicate curve points")
    combined.to_csv(output_dir / "curve_points_table.csv", index=False)
    return output_dir


def main() -> None:
    """Replace treated curves in a bundle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--curves", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = replace_treated_curves(
        bundle_dir=args.bundle_dir,
        curves_path=args.curves,
        output_dir=args.out,
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
