#!/usr/bin/env python3
"""Build a managed-land SI TIPSY input from a training split of RESULTS cover.

The experiment holds species and density at the current TSR input and changes
only the site index. For each AU/SI cell with enough training observations, the
median observed managed-stand SI replaces the checkpoint AU median. The
holdout openings are excluded from the SI estimate, so the resulting curves can
be tested on held-out heights without leakage.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

from build_results_tipsy_inputs import (
    assign_au,
    load_si_medians,
    normalize_species,
    stratum_by_leading_from_au_table,
)

COVER_SPECIES_COLUMNS = tuple(f"I_SPECIES_CODE_{index}" for index in range(1, 6))
COVER_PERCENT_COLUMNS = tuple(f"I_SPECIES_PERCENT_{index}" for index in range(1, 6))


def _finite(value: object) -> float | None:
    """Return a finite float, or ``None`` when the value is missing."""
    if value is None or value is pd.NA:
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _species_mix(row: dict[Any, Any]) -> dict[str, float]:
    """Return normalized model species percentages for one cover row."""
    mix: dict[str, float] = {}
    for code_column, percent_column in zip(
        COVER_SPECIES_COLUMNS, COVER_PERCENT_COLUMNS, strict=True
    ):
        species = normalize_species(row.get(code_column))
        percent = _finite(row.get(percent_column))
        if species is not None and percent is not None and percent > 0:
            mix[species] = mix.get(species, 0.0) + percent
    total = sum(mix.values())
    if total <= 0:
        return {}
    return {species: percent / total * 100.0 for species, percent in mix.items()}


def observed_management_rows(
    *,
    cover: pd.DataFrame,
    au_table: pd.DataFrame,
    stratum_by_leading: dict[str, str],
    si_medians: dict[tuple[str, str], float],
    min_age: int = 5,
    max_age: int = 80,
    min_height: float = 1.3,
    min_leading_percent: float = 80.0,
) -> pd.DataFrame:
    """Return observed managed-stand rows with model AU and site index.

    Parameters
    ----------
    cover : pandas.DataFrame
        RESULTS forest-cover attributes.
    au_table : pandas.DataFrame
        Model AU table.
    stratum_by_leading : dict of str to str
        Leading-species-to-stratum map.
    si_medians : dict of (str, str) to float
        Checkpoint SI by model AU and SI class.
    min_age, max_age : int
        Inclusive age window.
    min_height : float
        Minimum observed height in metres.
    min_leading_percent : float
        Minimum leading-species share.

    Returns
    -------
    pandas.DataFrame
        One row per observation with ``opening_id``, ``stratum_code``,
        ``si_level``, ``observed_si``, ``observed_height_m``, and
        ``observed_age``.
    """
    records: list[dict[str, Any]] = []
    for row in cover.to_dict(orient="records"):
        age = _finite(row.get("I_SPECIES_AGE_1"))
        height = _finite(row.get("I_SPECIES_HEIGHT_1"))
        leading_percent = _finite(row.get("I_SPECIES_PERCENT_1"))
        opening_id = _finite(row.get("OPENING_ID"))
        observed_si = _finite(row.get("SITE_INDEX"))
        if (
            age is None
            or height is None
            or leading_percent is None
            or opening_id is None
            or observed_si is None
        ):
            continue
        if not (min_age <= age <= max_age) or height < min_height:
            continue
        if leading_percent < min_leading_percent:
            continue
        mix = _species_mix(row)
        if not mix:
            continue
        assigned = assign_au(
            bec_zone=row.get("BGC_ZONE_CODE"),
            species_pct=mix,
            site_index=observed_si,
            stratum_by_leading=stratum_by_leading,
            si_medians=si_medians,
        )
        if assigned is None:
            continue
        stratum, level = assigned
        records.append(
            {
                "opening_id": int(opening_id),
                "stratum_code": stratum,
                "si_level": level,
                "observed_si": observed_si,
                "observed_height_m": height,
                "observed_age": age,
            }
        )
    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError("no observed cover rows matched a managed AU")
    return frame


def managed_si_by_cell(
    *,
    observations: pd.DataFrame,
    holdout_mod: int,
    holdout_seed: int,
    min_train_n: int,
) -> pd.DataFrame:
    """Return training-split median managed SI for each AU/SI cell.

    Parameters
    ----------
    observations : pandas.DataFrame
        Output of :func:`observed_management_rows`.
    holdout_mod : int
        Opening-id modulus used to define the holdout.
    holdout_seed : int
        Opening-id remainder that identifies the holdout.
    min_train_n : int
        Minimum training observations required to estimate a cell.

    Returns
    -------
    pandas.DataFrame
        One row per cell with training/holdout counts, checkpoint SI, managed
        SI, and whether the managed SI is used.
    """
    frame = observations.copy()
    frame["is_holdout"] = frame["opening_id"] % holdout_mod == holdout_seed
    train = frame[~frame["is_holdout"]]
    holdout = frame[frame["is_holdout"]]
    grouped = (
        train.groupby(["stratum_code", "si_level"], as_index=False)
        .agg(n_train=("observed_si", "size"), managed_si=("observed_si", "median"))
        .merge(
            holdout.groupby(["stratum_code", "si_level"], as_index=False).agg(
                n_holdout=("observed_si", "size")
            ),
            on=["stratum_code", "si_level"],
            how="outer",
        )
    )
    grouped["n_train"] = grouped["n_train"].fillna(0).astype(int)
    grouped["n_holdout"] = grouped["n_holdout"].fillna(0).astype(int)
    grouped["used"] = grouped["n_train"] >= min_train_n
    grouped["managed_si"] = [
        round(float(value), 1) if used and value == value else None
        for value, used in zip(grouped["managed_si"], grouped["used"], strict=False)
    ]
    return grouped.sort_values(["stratum_code", "si_level"]).reset_index(drop=True)


def apply_managed_si(
    *,
    base_input: pd.DataFrame,
    au_table: pd.DataFrame,
    managed_si: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the TIPSY input with cell SI replaced where training data exists.

    Parameters
    ----------
    base_input : pandas.DataFrame
        Current TIPSY input with ``feature_id`` equal to the managed local AU id.
    au_table : pandas.DataFrame
        Model AU table.
    managed_si : pandas.DataFrame
        Output of :func:`managed_si_by_cell`.

    Returns
    -------
    tuple of (pandas.DataFrame, pandas.DataFrame)
        The updated input and the audit table of applied cells.
    """
    cell_to_si: dict[tuple[str, str], float] = {}
    for row in managed_si.itertuples():
        value = _finite(row.managed_si)
        if row.used and value is not None:
            cell_to_si[(str(row.stratum_code), str(row.si_level))] = value
    au_to_cell: dict[int, tuple[str, str]] = {}
    for row in au_table.itertuples():
        au_id = _finite(row.source_managed_local_au_id)
        if au_id is not None:
            au_to_cell[int(au_id)] = (str(row.stratum_code), str(row.si_level))
    frame = base_input.copy()
    si_columns = [column for column in frame.columns if column.endswith("_si")]
    applied: list[dict[str, Any]] = []
    for index, frame_row in frame.iterrows():
        feature_id = _finite(frame_row.get("feature_id"))
        if feature_id is None:
            continue
        cell = au_to_cell.get(int(feature_id))
        if cell is None or cell not in cell_to_si:
            continue
        managed_value = cell_to_si[cell]
        for column in si_columns:
            frame.at[index, column] = managed_value
        applied.append(
            {
                "feature_id": int(feature_id),
                "stratum_code": cell[0],
                "si_level": cell[1],
                "managed_si": managed_value,
            }
        )
    return frame, pd.DataFrame(applied)


def main() -> None:
    """Write the managed-SI TIPSY input and audit table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--cover", type=Path)
    parser.add_argument("--base-input", type=Path)
    parser.add_argument(
        "--au-table", type=Path, default=Path("data/model_input_bundle/au_table.csv")
    )
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--holdout-mod", type=int, default=5)
    parser.add_argument("--holdout-seed", type=int, default=0)
    parser.add_argument("--min-train-n", type=int, default=10)
    parser.add_argument("--out-input", type=Path)
    parser.add_argument("--out-summary", type=Path)
    args = parser.parse_args()

    cover_path = args.cover or Path(
        "data/downloads/bcdc/"
        "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW/"
        "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW.gpkg"
    )
    base_input = args.base_input or Path(f"data/03_input-tsa{args.tsa}.csv")
    checkpoint = args.checkpoint or Path(
        f"runtime/tsa{args.tsa}_full_vdyp_20261023/thlb_calibrated_checkpoint.feather"
    )
    out_input = args.out_input or Path(f"tipsy_io/runs/03_input-tsa{args.tsa}_managed_si.csv")
    out_summary = args.out_summary or Path(f"config/tsr/managed_si_by_au.tsa{args.tsa}.csv")
    cover = gpd.read_file(
        cover_path,
        columns=[
            "OPENING_ID",
            "BGC_ZONE_CODE",
            "SITE_INDEX",
            "I_SPECIES_CODE_1",
            "I_SPECIES_PERCENT_1",
            "I_SPECIES_CODE_2",
            "I_SPECIES_PERCENT_2",
            "I_SPECIES_CODE_3",
            "I_SPECIES_PERCENT_3",
            "I_SPECIES_CODE_4",
            "I_SPECIES_PERCENT_4",
            "I_SPECIES_CODE_5",
            "I_SPECIES_PERCENT_5",
            "I_SPECIES_AGE_1",
            "I_SPECIES_HEIGHT_1",
        ],
        ignore_geometry=True,
    )
    au_table = pd.read_csv(args.au_table)
    si_medians = load_si_medians(checkpoint=checkpoint, au_table=args.au_table)
    observations = observed_management_rows(
        cover=cover,
        au_table=au_table,
        stratum_by_leading=stratum_by_leading_from_au_table(au_table),
        si_medians=si_medians,
    )
    managed = managed_si_by_cell(
        observations=observations,
        holdout_mod=args.holdout_mod,
        holdout_seed=args.holdout_seed,
        min_train_n=args.min_train_n,
    )
    updated, applied = apply_managed_si(
        base_input=pd.read_csv(base_input),
        au_table=au_table,
        managed_si=managed,
    )
    out_input.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    updated.to_csv(out_input, index=False)
    audit = managed.merge(
        applied,
        on=["stratum_code", "si_level"],
        how="left",
        suffixes=("", "_applied"),
    )
    audit.to_csv(out_summary, index=False)
    print(f"wrote {out_input} and {out_summary}; {len(applied)} AU rows changed")


if __name__ == "__main__":
    main()
