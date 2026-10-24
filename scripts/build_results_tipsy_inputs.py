#!/usr/bin/env python3
"""Derive candidate AU-wise TIPSY inputs for TSA 47 from public RESULTS layers.

The workflow repeats the TSA 48 RESULTS analysis on the TSA 47 AOI: acquire the
BCGW RESULTS opening, forest-cover, and planting layers, assign each opening to
the TSA 47 model AU by BEC and leading species, and aggregate species
composition, density, site index, genetic worth, and regeneration timing.

The output is a candidate table, not accepted policy. Genetic worth uses the
Kingcome TSR 3 future-regime values (Cw/Fd 3%, others 0%) because RESULTS
carries genetic class rather than a directly reported genetic-worth percentage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.feather as feather

GENETIC_WORTH = {
    "Cw": 3.0,
    "Yc": 0.0,
    "Fd": 3.0,
    "Hw": 0.0,
    "Hm": 0.0,
    "Ba": 0.0,
}
SPECIES_MAP = {
    "CW": "Cw",
    "YC": "Yc",
    "FD": "Fd",
    "FDC": "Fd",
    "FDI": "Fd",
    "HW": "Hw",
    "HM": "Hm",
    "BA": "Ba",
}
LEADING_STRATUM = {
    "Hw": "CWH_HW",
    "Cw": "CWH_CW",
    "Yc": "CWH_YC",
    "Fd": "CWH_FD",
    "Hm": "MH_HM",
    "Ba": "CWH_BA",
}
# TSA 47 fallback medians from the calibrated VRI checkpoint. ``main``
# recomputes these from the checkpoint supplied on the command line.
SI_MEDIANS = {
    ("CWH_HW", "L"): 11.9,
    ("CWH_HW", "M"): 17.0,
    ("CWH_HW", "H"): 26.3,
    ("CWH_CW", "L"): 11.4,
    ("CWH_CW", "M"): 15.0,
    ("CWH_CW", "H"): 18.9,
    ("CWH_YC", "L"): 8.2,
    ("CWH_YC", "M"): 11.1,
    ("CWH_YC", "H"): 14.3,
    ("CWH_FD", "L"): 17.0,
    ("CWH_FD", "M"): 23.2,
    ("CWH_FD", "H"): 29.1,
    ("MH_HM", "L"): 6.0,
    ("MH_HM", "M"): 8.7,
    ("MH_HM", "H"): 12.8,
    ("CWH_BA", "L"): 9.6,
    ("CWH_BA", "M"): 14.7,
    ("CWH_BA", "H"): 21.4,
}


def stratum_by_leading_from_au_table(au_table: pd.DataFrame) -> dict[str, str]:
    """Build a leading-species-to-stratum map from the model AU table.

    Parameters
    ----------
    au_table : pandas.DataFrame
        Model AU table with a ``stratum_code`` column.

    Returns
    -------
    dict of str to str
        Leading TIPSY species code to model stratum code.
    """
    token_map = {
        "HW": "Hw",
        "CW": "Cw",
        "YC": "Yc",
        "FD": "Fd",
        "FDC": "Fd",
        "HM": "Hm",
        "BA": "Ba",
    }
    mapping: dict[str, str] = {}
    for value in au_table["stratum_code"].dropna().unique():
        stratum = str(value)
        species = token_map.get(stratum.split("_")[-1].strip().upper())
        if species is not None:
            mapping[species] = stratum
    return mapping


def load_si_medians(*, checkpoint: Path, au_table: Path) -> dict[tuple[str, str], float]:
    """Return median checkpoint site index for each AU and SI class.

    Parameters
    ----------
    checkpoint : Path
        Calibrated stand checkpoint with ``au``, ``SITE_INDEX``, and ``si_level``.
    au_table : Path
        Model AU table mapping ``au_id`` to ``stratum_code``.

    Returns
    -------
    dict of (str, str) to float
        Median site index keyed by ``(stratum_code, si_level)``.
    """
    table = feather.read_table(
        checkpoint,
        columns=["au", "SITE_INDEX", "si_level"],
    ).to_pandas()
    au_frame = pd.read_csv(au_table)
    id_to_stratum = {
        int(au_id): str(stratum)
        for au_id, stratum in zip(au_frame["au_id"], au_frame["stratum_code"], strict=False)
        if pd.notna(au_id) and pd.notna(stratum)
    }
    table["au"] = table["au"].astype(int)
    table["stratum"] = table["au"].map(id_to_stratum)
    grouped = (
        table.dropna(subset=["stratum", "si_level"])
        .groupby(["stratum", "si_level"])["SITE_INDEX"]
        .median()
    )
    return {
        (str(stratum), str(level)): float(value)
        for (stratum, level), value in grouped.items()
        if value == value
    }


def normalize_species(value: object) -> str | None:
    """Return a model species code for a RESULTS species code.

    Parameters
    ----------
    value : object
        RESULTS species code such as ``FDC`` or ``HW``.

    Returns
    -------
    str or None
        The model species code, or ``None`` when the value is missing or unknown.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    code = str(value).strip().upper()
    return SPECIES_MAP.get(code)


def _to_float(value: object) -> float | None:
    """Return a finite float, or ``None`` for missing or non-numeric values.

    Parameters
    ----------
    value : object
        A scalar from a RESULTS row or a pandas row attribute.

    Returns
    -------
    float or None
        The finite numeric value, or ``None`` when the input is missing,
        non-numeric, or not finite.
    """
    if value is None:
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _to_int(value: object) -> int | None:
    """Return an integer id, or ``None`` for missing or non-numeric values.

    Parameters
    ----------
    value : object
        A scalar identifier from a RESULTS or model AU row.

    Returns
    -------
    int or None
        The truncated integer value, or ``None`` when the input is not numeric.
    """
    result = _to_float(value)
    return int(result) if result is not None else None


def assign_au(
    *,
    bec_zone: object,
    species_pct: dict[str, float],
    site_index: float | None,
    stratum_by_leading: dict[str, str] | None = None,
    si_medians: dict[tuple[str, str], float] | None = None,
) -> tuple[str, str] | None:
    """Assign a model stratum and SI class from BEC, species mix, and SI.

    Parameters
    ----------
    bec_zone : object
        BEC zone code. It is accepted for provenance and future routing.
    species_pct : dict of str to float
        Species percentages for the opening.
    site_index : float or None
        Site index in metres.
    stratum_by_leading : dict of str to str or None
        Leading-species-to-stratum map. Defaults to the TSA 47 fallback.
    si_medians : dict of (str, str) to float or None
        Median SI by ``(stratum, level)``. Defaults to the TSA 47 fallback.

    Returns
    -------
    tuple of (str, str) or None
        The model stratum and SI class, or ``None`` when the opening cannot be
        assigned.
    """
    if not species_pct:
        return None
    leading = max(species_pct.items(), key=lambda item: item[1])[0]
    stratum = (stratum_by_leading or LEADING_STRATUM).get(leading)
    if stratum is None:
        return None
    if site_index is None or np.isnan(site_index):
        return None
    medians = si_medians or SI_MEDIANS
    candidates = {
        level: medians[(stratum, level)] for level in ("L", "M", "H") if (stratum, level) in medians
    }
    if not candidates:
        return None
    level = min(candidates, key=lambda key: abs(candidates[key] - site_index))
    return stratum, level


def _best_cover_row(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return one forest-cover row per opening, preferring the most complete/latest."""
    rows: list[dict[str, Any]] = []
    for _opening_id, group in frame.groupby("OPENING_ID"):
        group = group.copy()
        group["_species_count"] = (
            group[[f"I_SPECIES_CODE_{i}" for i in range(1, 6)]].notna().sum(axis=1)
        )
        group["_reference_year"] = pd.to_numeric(group["REFERENCE_YEAR"], errors="coerce").fillna(0)
        best = group.sort_values(
            ["_reference_year", "_species_count", "FOREST_COVER_ID"],
            ascending=False,
        ).iloc[0]
        rows.append(best.to_dict())
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=frame.crs)


def aggregate(
    *,
    openings: gpd.GeoDataFrame,
    cover: gpd.GeoDataFrame,
    planting: gpd.GeoDataFrame,
    aoi: gpd.GeoDataFrame,
    stratum_by_leading: dict[str, str] | None = None,
    si_medians: dict[tuple[str, str], float] | None = None,
) -> pd.DataFrame:
    """Aggregate RESULTS attributes to model AU candidate rows.

    Parameters
    ----------
    openings : geopandas.GeoDataFrame
        RESULTS opening polygons with ``OPENING_ID`` and BEC fields.
    cover : geopandas.GeoDataFrame
        RESULTS forest-cover inventory rows with species and site-index fields.
    planting : geopandas.GeoDataFrame
        RESULTS planting rows with species, number planted, and treatment area.
    aoi : geopandas.GeoDataFrame
        Model AOI polygons used to filter openings.
    stratum_by_leading : dict of str to str or None
        Leading-species-to-stratum map. Defaults to the TSA 47 fallback.
    si_medians : dict of (str, str) to float or None
        Median SI by ``(stratum, level)``. Defaults to the TSA 47 fallback.

    Returns
    -------
    pandas.DataFrame
        One row per model AU with species mix, density, SI, OAF, and genetic
        worth.
    """
    aoi_union = aoi.geometry.union_all()
    openings = openings[openings.geometry.representative_point().within(aoi_union)]
    if openings.empty:
        raise ValueError("no RESULTS openings could be assigned to a model AU")
    cover = _best_cover_row(cover[cover["OPENING_ID"].isin(openings["OPENING_ID"])])
    planting = planting[planting["OPENING_ID"].isin(openings["OPENING_ID"])]
    merged = openings.merge(cover, on="OPENING_ID", how="inner", suffixes=("", "_fc"))

    # Planting-derived density and species mix, where reported.
    planting = planting.copy()
    planting["density"] = pd.to_numeric(
        planting["NUMBER_PLANTED"], errors="coerce"
    ) / pd.to_numeric(planting["ACTUAL_TREATMENT_AREA"], errors="coerce").replace(0, np.nan)
    plant_mix: dict[int, dict[str, float]] = {}
    plant_density: dict[int, float] = {}
    for opening_id, group in planting.groupby("OPENING_ID"):
        total = group["density"].sum()
        if total > 0:
            plant_density[int(opening_id)] = float(total)
            mix: dict[str, float] = {}
            for plant_row in group.itertuples():
                plant_species = normalize_species(plant_row.SILV_TREE_SPECIES_CODE)
                if plant_species is not None:
                    mix[plant_species] = float(plant_row.density)
            plant_mix[int(opening_id)] = mix

    records: list[dict[str, Any]] = []
    for row in merged.itertuples():
        species: dict[str, float] = {}
        for i in range(1, 6):
            code = normalize_species(getattr(row, f"I_SPECIES_CODE_{i}", None))
            pct = _to_float(getattr(row, f"I_SPECIES_PERCENT_{i}", None))
            if code is not None and pct is not None and pct > 0:
                species[code] = species.get(code, 0.0) + pct
        if not species:
            species = plant_mix.get(int(row.OPENING_ID), {})
        total = sum(species.values())
        if total <= 0:
            continue
        species = {code: value / total * 100.0 for code, value in species.items()}
        si = _to_float(getattr(row, "SITE_INDEX", None))
        assigned = assign_au(
            bec_zone=getattr(row, "BGC_ZONE_CODE", None),
            species_pct=species,
            site_index=si,
            stratum_by_leading=stratum_by_leading,
            si_medians=si_medians,
        )
        if assigned is None:
            continue
        stratum, level = assigned
        total_stems = _to_float(getattr(row, "I_TOTAL_STEMS_PER_HA", None))
        planting_density = plant_density.get(int(row.OPENING_ID))
        records.append(
            {
                "opening_id": int(row.OPENING_ID),
                "stratum_code": stratum,
                "si_level": level,
                "site_index": si,
                "bec_zone": getattr(row, "BGC_ZONE_CODE", None),
                "species_mix": json.dumps(
                    {k: round(v, 2) for k, v in sorted(species.items())},
                    sort_keys=True,
                ),
                "total_stems_sph": total_stems,
                "planting_density_sph": planting_density,
            }
        )
    if not records:
        raise ValueError("no RESULTS openings could be assigned to a model AU")
    frame = pd.DataFrame(records)
    grouped = (
        frame.groupby(["stratum_code", "si_level"], as_index=False)
        .agg(
            opening_count=("opening_id", "nunique"),
            median_si=("site_index", "median"),
            median_total_stems=("total_stems_sph", "median"),
            median_planting_density=("planting_density_sph", "median"),
            planting_opening_count=("planting_density_sph", lambda values: values.notna().sum()),
        )
        .sort_values(["stratum_code", "si_level"])
    )
    # Overstory total stems are not regeneration density. Only use a density
    # when the opening has at least one planting record; otherwise leave the
    # candidate density blank and let the base TIPSY input supply the fallback.
    grouped["median_density"] = grouped["median_planting_density"].where(
        grouped["planting_opening_count"] >= 1
    )
    grouped["density_source"] = np.select(
        [
            grouped["planting_opening_count"] >= 3,
            grouped["planting_opening_count"] >= 1,
        ],
        ["planting", "planting_single"],
        default="missing",
    )
    for column in (
        "median_si",
        "median_total_stems",
        "median_planting_density",
        "median_density",
    ):
        grouped[column] = grouped[column].round(1)
    grouped["species_mix"] = grouped.apply(
        lambda row: _weighted_species(
            frame,
            stratum=row.stratum_code,
            level=row.si_level,
        ),
        axis=1,
    )
    grouped["genetic_worth"] = grouped["species_mix"].apply(_genetic_worth)
    grouped["oaf1"] = 0.85
    grouped["oaf2"] = 0.95
    return grouped


def _weighted_species(frame: pd.DataFrame, *, stratum: str, level: str) -> str:
    """Return an opening-weighted species mix for one AU."""
    subset = frame[(frame["stratum_code"] == stratum) & (frame["si_level"] == level)]
    totals: dict[str, float] = {}
    for value in subset["species_mix"]:
        for species, pct in json.loads(value).items():
            totals[species] = totals.get(species, 0.0) + float(pct)
    grand = sum(totals.values())
    if grand <= 0:
        return "{}"
    return json.dumps(
        {species: round(pct / grand * 100.0, 2) for species, pct in sorted(totals.items())},
        sort_keys=True,
    )


def _genetic_worth(value: str) -> str:
    """Return a JSON genetic-worth map for a species-mix JSON string."""
    mix = json.loads(value)
    return json.dumps(
        {species: GENETIC_WORTH.get(species, 0.0) for species in mix},
        sort_keys=True,
    )


def apply_candidates_to_input(
    *,
    candidates: pd.DataFrame,
    base_input: pd.DataFrame,
    au_table: pd.DataFrame,
    fallback_density: float | None = None,
    density_override: float | None = None,
    si_by_key: dict[tuple[str, str], float] | None = None,
) -> pd.DataFrame:
    """Replace the managed species, density, SI, and OAF fields in a TIPSY input.

    Parameters
    ----------
    candidates : pandas.DataFrame
        Output of :func:`aggregate`, keyed by ``stratum_code`` and ``si_level``.
    base_input : pandas.DataFrame
        TIPSY transposed-input template with ``feature_id`` equal to the managed
        local AU id.
    au_table : pandas.DataFrame
        Model AU table with ``source_managed_local_au_id``, ``stratum_code``, and
        ``si_level``.
    fallback_density : float or None
        Density used when a RESULTS candidate has no planting-derived density.
        The base input density is retained when this is ``None``.
    density_override : float or None
        Fixed density applied to every matched candidate.
    si_by_key : dict of (str, str) to float or None
        Optional checkpoint SI by ``(stratum, level)``. When supplied, it
        overrides the RESULTS cover SI to avoid harvested-area selection bias.

    Returns
    -------
    pandas.DataFrame
        A copy of ``base_input`` with RESULTS-derived species, density, site
        index, genetic worth, and OAF values.
    """
    frame = base_input.copy()
    for position in range(1, 6):
        column = f"planted_species{position}"
        if column in frame:
            # An all-NaN species column arrives as float64; keep it textual.
            frame[column] = frame[column].astype(object)
    au_keys: dict[int, tuple[str, str]] = {}
    for au_row in au_table.itertuples():
        au_id = _to_int(au_row.source_managed_local_au_id)
        if au_id is not None:
            au_keys[au_id] = (str(au_row.stratum_code), str(au_row.si_level))
    candidate_by_key = {
        (str(row.stratum_code), str(row.si_level)): row for row in candidates.itertuples()
    }
    species_si_columns = {
        "Ba": "ba_si",
        "Cw": "cw_si",
        "Fd": "fd_si",
        "Hw": "hw_si",
        "Hm": "hm_si",
        "Ss": "ss_si",
        "Yc": "yc_si",
    }
    for index, frame_row in frame.iterrows():
        feature_id = _to_int(frame_row["feature_id"])
        if feature_id is None:
            continue
        key = au_keys.get(feature_id)
        if key is None:
            continue
        candidate = candidate_by_key.get(key)
        if candidate is None:
            continue
        raw_mix = json.loads(str(candidate.species_mix))
        mix: dict[str, float] = {}
        for species, percentage in raw_mix.items():
            normalized = normalize_species(species)
            if normalized is None:
                continue
            mix[normalized] = mix.get(normalized, 0.0) + float(percentage)
        total = sum(mix.values())
        if total <= 0:
            continue
        density = density_override
        if density is None:
            density = _to_float(candidate.median_density)
        if density is None:
            density = fallback_density
        site_index = None
        if si_by_key is not None:
            site_index = si_by_key.get((str(candidate.stratum_code), str(candidate.si_level)))
        if site_index is None:
            site_index = _to_float(candidate.median_si)
        if density is None or site_index is None:
            continue
        for position in range(1, 6):
            frame.at[index, f"planted_species{position}"] = ""
            frame.at[index, f"planted_density{position}"] = 0.0
            frame.at[index, f"genetic_worth{position}"] = 0.0
        for position, (species, percentage) in enumerate(
            sorted(mix.items(), key=lambda item: (-item[1], item[0]))[:5],
            start=1,
        ):
            frame.at[index, f"planted_species{position}"] = species
            frame.at[index, f"planted_density{position}"] = round(density * percentage / total)
            frame.at[index, f"genetic_worth{position}"] = GENETIC_WORTH.get(species, 0.0)
            si_column = species_si_columns.get(species)
            if si_column is not None:
                frame.at[index, si_column] = site_index
        oaf1 = _to_float(candidate.oaf1)
        oaf2 = _to_float(candidate.oaf2)
        if oaf1 is not None:
            frame.at[index, "oaf1"] = oaf1
        if oaf2 is not None:
            frame.at[index, "oaf2"] = oaf2
    for position in range(1, 6):
        column = f"planted_density{position}"
        if column in frame:
            # BTC parses these as Integer; "417.0" raises a conversion dialog.
            frame[column] = frame[column].fillna(0).astype(int)
    return frame


def main() -> None:
    """Read the RESULTS GPKGs and write the candidate AU table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download-root",
        type=Path,
        default=Path("data/downloads/bcdc"),
    )
    parser.add_argument(
        "--aoi",
        type=Path,
        default=Path("data/source/aoi/tsa47_full.gpkg"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("config/tsr/tipsy_au_results_candidates.tsa47.csv"),
    )
    parser.add_argument(
        "--tipsy-input",
        type=Path,
        help="Optional template TIPSY input to update with the RESULTS candidates.",
    )
    parser.add_argument(
        "--base-input",
        type=Path,
        default=Path("data/03_input-tsa47.csv"),
        help="Template TIPSY input used when --tipsy-input is set.",
    )
    parser.add_argument(
        "--au-table",
        type=Path,
        default=Path("data/model_input_bundle/au_table.csv"),
        help="Model AU table used for the RESULTS-to-AU mapping.",
    )
    parser.add_argument(
        "--fallback-density",
        type=float,
        default=1000.0,
        help="Density used when no planting record exists; base input is kept if omitted.",
    )
    parser.add_argument(
        "--density-override",
        type=float,
        help="Fixed density for every matched candidate; use to isolate species/SI.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("runtime/tsa47_full/thlb_calibrated_checkpoint.feather"),
        help="Checkpoint used to derive median SI by AU and SI class.",
    )
    args = parser.parse_args()
    if not args.checkpoint.is_file():
        fallback = Path("runtime/tsa47_full_vdyp_20261023/thlb_calibrated_checkpoint.feather")
        if fallback.is_file():
            args.checkpoint = fallback
    au_table = pd.read_csv(args.au_table)
    stratum_by_leading = stratum_by_leading_from_au_table(au_table)
    si_medians = load_si_medians(checkpoint=args.checkpoint, au_table=args.au_table)
    openings = gpd.read_file(
        args.download_root
        / "WHSE_FOREST_VEGETATION_RSLT_OPENING_SVW"
        / "WHSE_FOREST_VEGETATION_RSLT_OPENING_SVW.gpkg"
    )
    cover = gpd.read_file(
        args.download_root
        / "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW"
        / "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW.gpkg"
    )
    planting = gpd.read_file(
        args.download_root
        / "WHSE_FOREST_VEGETATION_RSLT_PLANTING_SVW"
        / "WHSE_FOREST_VEGETATION_RSLT_PLANTING_SVW.gpkg"
    )
    aoi = gpd.read_file(args.aoi)
    result = aggregate(
        openings=openings,
        cover=cover,
        planting=planting,
        aoi=aoi,
        stratum_by_leading=stratum_by_leading,
        si_medians=si_medians,
    )
    result["checkpoint_si"] = [
        si_medians.get((str(stratum), str(level)))
        for stratum, level in zip(result["stratum_code"], result["si_level"], strict=False)
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(result.to_string(index=False))
    if args.tipsy_input is not None:
        updated = apply_candidates_to_input(
            candidates=result,
            base_input=pd.read_csv(args.base_input),
            au_table=au_table,
            fallback_density=args.fallback_density,
            density_override=args.density_override,
            si_by_key=si_medians,
        )
        args.tipsy_input.parent.mkdir(parents=True, exist_ok=True)
        updated.to_csv(args.tipsy_input, index=False)
        print(f"wrote {args.tipsy_input}")


if __name__ == "__main__":
    main()
