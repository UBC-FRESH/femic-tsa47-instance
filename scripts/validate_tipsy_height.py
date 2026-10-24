#!/usr/bin/env python3
"""Validate TIPSY height-age predictions against observed RESULTS cover.

The comparison is deliberately independent of the AAC target. Observed
immature-stand heights and ages are read from the RESULTS forest-cover layer,
mapped to the model AU, and compared with the TIPSY height curve at the same
age. The output is a bias/error table by AU and age class, not a harvest-area
score.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
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

AGE_BINS = (5, 15, 30, 50, 80)
AGE_LABELS = ("5-15", "16-30", "31-50", "51-80")
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


def _species_mix(row: Mapping[object, object]) -> dict[str, float]:
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


def build_validation_rows(
    *,
    cover: pd.DataFrame,
    curves: pd.DataFrame,
    au_table: pd.DataFrame,
    stratum_by_leading: dict[str, str],
    si_medians: dict[tuple[str, str], float],
    min_age: int = 5,
    max_age: int = 80,
    min_height: float = 1.3,
    min_leading_percent: float = 80.0,
) -> pd.DataFrame:
    """Match observed cover height/age to the TIPSY curve for the model AU.

    Parameters
    ----------
    cover : pandas.DataFrame
        RESULTS forest-cover attributes, including ``I_SPECIES_*`` and
        ``I_SPECIES_HEIGHT_1`` / ``I_SPECIES_AGE_1``.
    curves : pandas.DataFrame
        Long-format TIPSY curves with ``AU``, ``Age``, and ``Height``.
    au_table : pandas.DataFrame
        Model AU table with ``source_managed_local_au_id``, ``stratum_code``,
        and ``si_level``.
    stratum_by_leading : dict of str to str
        Leading-species-to-stratum map.
    si_medians : dict of (str, str) to float
        Median SI by model AU and SI class.
    min_age, max_age : int
        Inclusive observed age window.
    min_height : float
        Minimum observed leading-species height in metres.
    min_leading_percent : float
        Minimum leading-species share for the single-species comparison.

    Returns
    -------
    pandas.DataFrame
        One row per matched observation with observed/predicted height and the
        model AU key.
    """
    curve_by_au = {
        int(au): group.sort_values("Age") for au, group in curves.groupby(curves["AU"].astype(int))
    }
    au_to_local = {
        (str(row.stratum_code), str(row.si_level)): int(float(str(row.source_managed_local_au_id)))
        for row in au_table.itertuples()
        if pd.notna(row.source_managed_local_au_id)
    }
    records: list[dict[str, Any]] = []
    for row in cover.to_dict(orient="records"):
        age = _finite(row.get("I_SPECIES_AGE_1"))
        height = _finite(row.get("I_SPECIES_HEIGHT_1"))
        leading_percent = _finite(row.get("I_SPECIES_PERCENT_1"))
        opening_id = _finite(row.get("OPENING_ID"))
        forest_cover_id = _finite(row.get("FOREST_COVER_ID"))
        if age is None or height is None or leading_percent is None:
            continue
        if opening_id is None or forest_cover_id is None:
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
            site_index=_finite(row.get("SITE_INDEX")),
            stratum_by_leading=stratum_by_leading,
            si_medians=si_medians,
        )
        if assigned is None:
            continue
        stratum, level = assigned
        local_au = au_to_local.get((stratum, level))
        if local_au is None or local_au not in curve_by_au:
            continue
        curve = curve_by_au[local_au]
        predicted = float(
            np.interp(
                age,
                curve["Age"].to_numpy(dtype=float),
                curve["Height"].to_numpy(dtype=float),
            )
        )
        records.append(
            {
                "opening_id": int(opening_id),
                "forest_cover_id": int(forest_cover_id),
                "stratum_code": stratum,
                "si_level": level,
                "local_au": local_au,
                "bec_zone": row.get("BGC_ZONE_CODE"),
                "leading_species": max(mix.items(), key=lambda item: item[1])[0],
                "leading_percent": round(leading_percent, 1),
                "observed_age": round(age, 1),
                "observed_height_m": round(height, 2),
                "predicted_height_m": round(predicted, 2),
                "error_m": round(predicted - height, 2),
            }
        )
    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError("no observed cover rows matched a TIPSY AU curve")
    frame["age_class"] = pd.cut(
        frame["observed_age"],
        bins=list(AGE_BINS),
        labels=list(AGE_LABELS),
        include_lowest=True,
    )
    return frame


def summarize_validation(frame: pd.DataFrame) -> pd.DataFrame:
    """Return bias and error metrics by stratum/SI and age class.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of :func:`build_validation_rows`.

    Returns
    -------
    pandas.DataFrame
        Metrics with ``n``, ``bias_m``, ``mae_m``, ``rmse_m``, and
        ``relative_bias``.
    """
    grouped = (
        frame.groupby(["stratum_code", "si_level", "age_class"], observed=True)
        .agg(
            n=("error_m", "size"),
            mean_observed_m=("observed_height_m", "mean"),
            mean_predicted_m=("predicted_height_m", "mean"),
            bias_m=("error_m", "mean"),
            mae_m=("error_m", lambda values: float(np.mean(np.abs(values)))),
            rmse_m=("error_m", lambda values: float(np.sqrt(np.mean(np.square(values))))),
        )
        .reset_index()
    )
    grouped["relative_bias"] = grouped["bias_m"] / grouped["mean_observed_m"]
    return grouped.round(3)


def main() -> None:
    """Run the TIPSY height validation and write observation/metric CSVs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--cover", type=Path)
    parser.add_argument("--curves", type=Path)
    parser.add_argument(
        "--au-table", type=Path, default=Path("data/model_input_bundle/au_table.csv")
    )
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--min-age", type=int, default=5)
    parser.add_argument("--max-age", type=int, default=80)
    parser.add_argument("--min-height", type=float, default=1.3)
    parser.add_argument("--min-leading-percent", type=float, default=80.0)
    args = parser.parse_args()

    cover_path = args.cover or Path(
        "data/downloads/bcdc/"
        "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW/"
        "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW.gpkg"
    )
    curves_path = args.curves or Path(f"tipsy_io/runs/curves_tsa{args.tsa}_tsr.csv")
    checkpoint = args.checkpoint or Path(
        f"runtime/tsa{args.tsa}_full_vdyp_20261023/thlb_calibrated_checkpoint.feather"
    )
    out = args.out or Path(f"config/tsr/tipsy_height_validation.tsa{args.tsa}.csv")
    summary_out = args.summary_out or Path(
        f"config/tsr/tipsy_height_validation_summary.tsa{args.tsa}.csv"
    )
    cover = gpd.read_file(
        cover_path,
        columns=[
            "OPENING_ID",
            "FOREST_COVER_ID",
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
    curves = pd.read_csv(curves_path)
    au_table = pd.read_csv(args.au_table)
    frame = build_validation_rows(
        cover=cover,
        curves=curves,
        au_table=au_table,
        stratum_by_leading=stratum_by_leading_from_au_table(au_table),
        si_medians=load_si_medians(checkpoint=checkpoint, au_table=args.au_table),
        min_age=args.min_age,
        max_age=args.max_age,
        min_height=args.min_height,
        min_leading_percent=args.min_leading_percent,
    )
    summary = summarize_validation(frame)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    summary.to_csv(summary_out, index=False)
    overall = frame["error_m"]
    print(
        f"n={len(frame)} bias={overall.mean():.2f} m "
        f"mae={overall.abs().mean():.2f} m "
        f"rmse={np.sqrt(np.mean(np.square(overall))):.2f} m"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
