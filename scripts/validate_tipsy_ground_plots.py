#!/usr/bin/env python3
"""Validate TIPSY volume, DBH, height, and stems against FAIB ground plots.

The plot inputs are the Nemora FAIB HPS manifest plus the FAIB compiled
summary tables. PSP and non-PSP tables use different column names; the schema
is detected from the compiled summary. Volume and stems use the 12.5 cm
utilization limit. DBH is approximate because TIPSY ``DBHg000`` is all-stem
QMD while the compiled plot tables report QMD at the utilization limit.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from build_results_tipsy_inputs import (
    assign_au,
    load_si_medians,
    normalize_species,
    stratum_by_leading_from_au_table,
)

AGE_BINS = (5, 15, 30, 50, 80, 200)
AGE_LABELS = ("5-15", "16-30", "31-50", "51-80", "81-200")
METRICS = ("volume", "dbh", "height", "stems")


def _finite(value: object) -> float | None:
    """Return a finite float, or ``None`` when the value is missing."""
    if value is None or value is pd.NA:
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _predict(curve: pd.DataFrame, age: float, column: str) -> float | None:
    """Interpolate a TIPSY curve at an observed age."""
    if column not in curve:
        return None
    return float(
        np.interp(
            age,
            curve["Age"].to_numpy(dtype=float),
            curve[column].to_numpy(dtype=float),
        )
    )


def _schema_columns(smries: pd.DataFrame) -> dict[str, str]:
    """Return the volume/DBH/stems column names for PSP or non-PSP data."""
    if "VHA_DWB_LIV" in smries.columns:
        return {
            "schema": "psp",
            "volume": "VHA_DWB_LIV",
            "dbh": "QMD_LIV",
            "stems": "STEMS_HA_LIV",
            "species_pct": "SP_PCT_BA_LI",
            "age": "AGE_TOT1",
            "height": "HTOP1",
            "si": "SI1",
        }
    if "VHA_NTWB_LS" in smries.columns:
        return {
            "schema": "non_psp",
            "volume": "VHA_NTWB_LS",
            "dbh": "QMD_LS",
            "stems": "STEMS_HA_LS",
            "species_pct": "SP_PCT_BA_LS",
            "age": "AGET_TLSO",
            "height": "HT_TLSO",
            "si": "SI_M_TLSO",
        }
    raise ValueError(
        "Unrecognized FAIB summary schema: expected PSP VHA_DWB_LIV or non-PSP VHA_NTWB_LS"
    )


def _leading_species(
    *,
    species: pd.DataFrame,
    species_pct_column: str,
    min_leading_percent: float,
) -> pd.DataFrame:
    """Return one leading species per cluster/visit above the share floor."""
    frame = species.copy()
    frame["species_model"] = frame["SPECIES"].map(normalize_species)
    frame = frame.dropna(subset=["species_model"])
    frame[species_pct_column] = pd.to_numeric(frame[species_pct_column], errors="coerce")
    frame = frame[frame[species_pct_column] >= min_leading_percent]
    selected = frame.sort_values(species_pct_column, ascending=False).drop_duplicates(
        ["CLSTR_ID", "VISIT_NUMBER"]
    )
    return selected


def build_validation_rows(
    *,
    header: pd.DataFrame,
    manifest: pd.DataFrame,
    smries: pd.DataFrame,
    species: pd.DataFrame,
    siteage: pd.DataFrame,
    curves: pd.DataFrame,
    au_table: pd.DataFrame,
    stratum_by_leading: dict[str, str],
    si_medians: dict[tuple[str, str], float],
    min_age: int = 5,
    max_age: int = 200,
    min_leading_percent: float = 50.0,
) -> pd.DataFrame:
    """Build observed/predicted ground-plot validation rows.

    Parameters
    ----------
    header : pandas.DataFrame
        FAIB site header with ``SITE_IDENTIFIER``, ``BEC_ZONE``, and
        ``SAMPLE_ESTABLISHMENT_TYPE``.
    manifest : pandas.DataFrame
        Nemora HPS manifest with ``cluster_id``, ``visit_number``, and
        ``site_identifier``.
    smries : pandas.DataFrame
        FAIB compiled plot summary filtered to one utilization limit.
    species : pandas.DataFrame
        FAIB compiled species summary filtered to the same utilization limit.
    siteage : pandas.DataFrame
        FAIB compiled species age/height/SI table.
    curves : pandas.DataFrame
        TIPSY curves with ``AU``, ``Age``, ``Yield``, ``Height``,
        ``DBHg000``, and ``StemCount125``.
    au_table : pandas.DataFrame
        Model AU table.
    stratum_by_leading : dict of str to str
        Leading-species-to-stratum map.
    si_medians : dict of (str, str) to float
        Checkpoint SI by AU/SI class.
    min_age, max_age : int
        Inclusive observed age window.
    min_leading_percent : float
        Minimum leading-species BA share.

    Returns
    -------
    pandas.DataFrame
        One row per matched observation with observed/predicted metrics.
    """
    columns = _schema_columns(smries)
    site_info = header.set_index("SITE_IDENTIFIER")[
        ["BEC_ZONE", "SAMPLE_ESTABLISHMENT_TYPE"]
    ].to_dict("index")
    sm = smries.drop_duplicates(["CLSTR_ID", "VISIT_NUMBER"])
    sm_records = {
        (str(row["CLSTR_ID"]), int(float(str(row["VISIT_NUMBER"])))): row
        for row in sm.to_dict(orient="records")
    }
    lead = _leading_species(
        species=species,
        species_pct_column=columns["species_pct"],
        min_leading_percent=min_leading_percent,
    )
    age_table = siteage.copy()
    age_table["species_model"] = age_table["SPECIES"].map(normalize_species)
    age_table = age_table.dropna(subset=["species_model"])
    age_records = {
        (
            str(row["CLSTR_ID"]),
            int(float(str(row["VISIT_NUMBER"]))),
            str(row["species_model"]),
        ): row
        for row in age_table.to_dict(orient="records")
    }
    curve_by_au = {
        int(au): frame.sort_values("Age") for au, frame in curves.groupby(curves["AU"].astype(int))
    }
    au_to_local = {
        (str(row.stratum_code), str(row.si_level)): int(float(str(row.source_managed_local_au_id)))
        for row in au_table.itertuples()
        if pd.notna(row.source_managed_local_au_id)
    }
    lead_records = {
        (str(row["CLSTR_ID"]), int(float(str(row["VISIT_NUMBER"])))): row
        for row in lead.to_dict(orient="records")
    }
    records: list[dict[str, Any]] = []
    for row in manifest.to_dict(orient="records"):
        site = site_info.get(row.get("site_identifier"))
        if site is None:
            continue
        visit = _finite(row.get("visit_number"))
        if visit is None:
            continue
        key = (str(row.get("cluster_id")), int(visit))
        if key not in sm_records or key not in lead_records:
            continue
        summary = sm_records[key]
        lead_row = lead_records[key]
        species_code = str(lead_row["species_model"])
        age_row = age_records.get((key[0], key[1], species_code))
        if age_row is None:
            continue
        age = _finite(age_row.get(columns["age"]))
        height = _finite(age_row.get(columns["height"]))
        site_index = _finite(age_row.get(columns["si"]))
        if age is None or not (min_age <= age <= max_age):
            continue
        assigned = assign_au(
            bec_zone=site.get("BEC_ZONE"),
            species_pct={species_code: 100.0},
            site_index=site_index,
            stratum_by_leading=stratum_by_leading,
            si_medians=si_medians,
        )
        if assigned is None:
            continue
        local_au = au_to_local.get(assigned)
        if local_au is None or local_au not in curve_by_au:
            continue
        curve = curve_by_au[local_au]

        records.append(
            {
                "sample_type": site.get("SAMPLE_ESTABLISHMENT_TYPE"),
                "site_identifier": row.get("site_identifier"),
                "cluster_id": row.get("cluster_id"),
                "visit_number": key[1],
                "stratum_code": assigned[0],
                "si_level": assigned[1],
                "local_au": local_au,
                "species": species_code,
                "age": age,
                "observed_si": site_index,
                "observed_volume": _finite(summary.get(columns["volume"])),
                "predicted_volume": _predict(curve, age, "Yield"),
                "observed_dbh": _finite(summary.get(columns["dbh"])),
                "predicted_dbh": _predict(curve, age, "DBHg000"),
                "observed_height": height,
                "predicted_height": _predict(curve, age, "Height"),
                "observed_stems": _finite(summary.get(columns["stems"])),
                "predicted_stems": _predict(curve, age, "StemCount125"),
            }
        )
    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError("no ground-plot rows matched a TIPSY AU curve")
    frame["age_class"] = pd.cut(
        frame["age"],
        bins=list(AGE_BINS),
        labels=list(AGE_LABELS),
        include_lowest=True,
    )
    return frame


def summarize_validation(frame: pd.DataFrame) -> pd.DataFrame:
    """Return bias and error metrics by sample type, AU, and age class.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of :func:`build_validation_rows`.

    Returns
    -------
    pandas.DataFrame
        Long-form metrics with ``metric``, ``n``, ``bias``, ``mae``,
        ``rmse``, and ``relative_bias``.
    """
    records: list[dict[str, Any]] = []
    for keys, group in frame.groupby(
        ["sample_type", "stratum_code", "si_level", "age_class"], observed=True
    ):
        for metric in METRICS:
            observed = group[f"observed_{metric}"]
            predicted = group[f"predicted_{metric}"]
            valid = pd.concat([observed, predicted], axis=1).dropna()
            valid = valid[(valid.iloc[:, 0] > 0) & (valid.iloc[:, 1] > 0)]
            if valid.empty:
                continue
            errors = valid.iloc[:, 1] - valid.iloc[:, 0]
            records.append(
                {
                    "sample_type": keys[0],
                    "stratum_code": keys[1],
                    "si_level": keys[2],
                    "age_class": keys[3],
                    "metric": metric,
                    "n": len(valid),
                    "mean_observed": round(float(valid.iloc[:, 0].mean()), 2),
                    "mean_predicted": round(float(valid.iloc[:, 1].mean()), 2),
                    "bias": round(float(errors.mean()), 2),
                    "mae": round(float(errors.abs().mean()), 2),
                    "rmse": round(float(np.sqrt(np.mean(np.square(errors)))), 2),
                    "relative_bias": round(float(errors.mean() / valid.iloc[:, 0].mean()), 3),
                }
            )
    return pd.DataFrame(records)


def main() -> None:
    """Run the ground-plot validation and write observations and metrics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--smries", type=Path, required=True)
    parser.add_argument("--species", type=Path, required=True)
    parser.add_argument("--siteage", type=Path, required=True)
    parser.add_argument("--curves", type=Path, required=True)
    parser.add_argument(
        "--au-table", type=Path, default=Path("data/model_input_bundle/au_table.csv")
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--min-age", type=int, default=5)
    parser.add_argument("--max-age", type=int, default=200)
    parser.add_argument("--min-leading-percent", type=float, default=50.0)
    args = parser.parse_args()

    header = pd.read_csv(args.header)
    manifest = pd.read_csv(args.manifest)
    smries = pd.read_csv(args.smries, low_memory=False)
    smries = smries[smries["UTIL"] == 12.5]
    species = pd.read_csv(args.species, low_memory=False)
    species = species[species["UTIL"] == 12.5]
    siteage = pd.read_csv(args.siteage, low_memory=False)
    curves = pd.read_csv(args.curves)
    au_table = pd.read_csv(args.au_table)
    frame = build_validation_rows(
        header=header,
        manifest=manifest,
        smries=smries,
        species=species,
        siteage=siteage,
        curves=curves,
        au_table=au_table,
        stratum_by_leading=stratum_by_leading_from_au_table(au_table),
        si_medians=load_si_medians(
            checkpoint=args.checkpoint,
            au_table=args.au_table,
        ),
        min_age=args.min_age,
        max_age=args.max_age,
        min_leading_percent=args.min_leading_percent,
    )
    summary = summarize_validation(frame)
    out = args.out or Path(f"config/tsr/tipsy_ground_plot_validation.tsa{args.tsa}.csv")
    summary_out = args.summary_out or Path(
        f"config/tsr/tipsy_ground_plot_validation_summary.tsa{args.tsa}.csv"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    summary.to_csv(summary_out, index=False)
    print(f"wrote {len(frame)} observations and {len(summary)} metric rows")


if __name__ == "__main__":
    main()
