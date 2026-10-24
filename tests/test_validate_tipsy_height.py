"""Tests for the independent TIPSY height validation table."""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.feather as feather
import pytest
from shapely.geometry import box

from validate_tipsy_height import (
    _finite,
    _species_mix,
    build_validation_rows,
    main,
    summarize_validation,
)


def _cover() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "OPENING_ID": 1,
                "FOREST_COVER_ID": 10,
                "BGC_ZONE_CODE": "CWH",
                "SITE_INDEX": 9.0,
                "I_SPECIES_CODE_1": "HW",
                "I_SPECIES_PERCENT_1": 100.0,
                "I_SPECIES_CODE_2": None,
                "I_SPECIES_PERCENT_2": None,
                "I_SPECIES_CODE_3": None,
                "I_SPECIES_PERCENT_3": None,
                "I_SPECIES_CODE_4": None,
                "I_SPECIES_PERCENT_4": None,
                "I_SPECIES_CODE_5": None,
                "I_SPECIES_PERCENT_5": None,
                "I_SPECIES_AGE_1": 10.0,
                "I_SPECIES_HEIGHT_1": 3.0,
            },
            {
                "OPENING_ID": 2,
                "FOREST_COVER_ID": 11,
                "BGC_ZONE_CODE": "CWH",
                "SITE_INDEX": 9.0,
                "I_SPECIES_CODE_1": "HW",
                "I_SPECIES_PERCENT_1": 100.0,
                "I_SPECIES_CODE_2": None,
                "I_SPECIES_PERCENT_2": None,
                "I_SPECIES_CODE_3": None,
                "I_SPECIES_PERCENT_3": None,
                "I_SPECIES_CODE_4": None,
                "I_SPECIES_PERCENT_4": None,
                "I_SPECIES_CODE_5": None,
                "I_SPECIES_PERCENT_5": None,
                "I_SPECIES_AGE_1": 2.0,
                "I_SPECIES_HEIGHT_1": 3.0,
            },
            {
                "OPENING_ID": 3,
                "FOREST_COVER_ID": 12,
                "BGC_ZONE_CODE": "CWH",
                "SITE_INDEX": 9.0,
                "I_SPECIES_CODE_1": "HW",
                "I_SPECIES_PERCENT_1": 50.0,
                "I_SPECIES_CODE_2": "CW",
                "I_SPECIES_PERCENT_2": 50.0,
                "I_SPECIES_CODE_3": None,
                "I_SPECIES_PERCENT_3": None,
                "I_SPECIES_CODE_4": None,
                "I_SPECIES_PERCENT_4": None,
                "I_SPECIES_CODE_5": None,
                "I_SPECIES_PERCENT_5": None,
                "I_SPECIES_AGE_1": 10.0,
                "I_SPECIES_HEIGHT_1": 3.0,
            },
        ]
    )


def _curves() -> pd.DataFrame:
    ages = np.arange(0, 21)
    return pd.DataFrame(
        {
            "AU": [21000] * len(ages),
            "Age": ages,
            "Yield": ages * 1.0,
            "Height": ages * 0.2,
        }
    )


def _au_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    )


def test_build_validation_rows_matches_au_and_predicts_height() -> None:
    """The observed row is matched to the AU and compared with TIPSY height."""
    frame = build_validation_rows(
        cover=_cover(),
        curves=_curves(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
    )
    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["local_au"] == 21000
    assert row["observed_height_m"] == 3.0
    assert row["predicted_height_m"] == 2.0
    assert row["error_m"] == -1.0
    assert row["age_class"] == "5-15"
    assert row["observed_si"] == 9.0
    assert row["checkpoint_si"] == 9.0


def test_build_validation_rows_filters_age_and_mixed_stand() -> None:
    """Young and mixed observations are excluded by the defaults."""
    frame = build_validation_rows(
        cover=_cover(),
        curves=_curves(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
        min_age=5,
        min_leading_percent=80.0,
    )
    assert frame["opening_id"].tolist() == [1]


def test_build_validation_rows_rejects_unmatched_data() -> None:
    """No usable observations is a blocking input error."""
    with pytest.raises(ValueError, match="no observed cover"):
        build_validation_rows(
            cover=_cover().iloc[0:0],
            curves=_curves(),
            au_table=_au_table(),
            stratum_by_leading={"Hw": "CWH_HW"},
            si_medians={("CWH_HW", "L"): 9.0},
        )


def test_summarize_validation_reports_bias_and_error() -> None:
    """The summary carries count, bias, MAE, and RMSE."""
    frame = pd.DataFrame(
        {
            "stratum_code": ["CWH_HW", "CWH_HW"],
            "si_level": ["L", "L"],
            "age_class": ["5-15", "5-15"],
            "observed_height_m": [3.0, 5.0],
            "predicted_height_m": [2.0, 7.0],
            "error_m": [-1.0, 2.0],
            "observed_si": [10.0, 10.0],
            "checkpoint_si": [9.0, 9.0],
        }
    )
    summary = summarize_validation(frame)
    row = summary.iloc[0]
    assert row["n"] == 2
    assert row["bias_m"] == 0.5
    assert row["mae_m"] == 1.5
    assert row["rmse_m"] == pytest.approx(1.581, abs=0.001)
    assert row["relative_bias"] == pytest.approx(0.125, abs=0.001)
    assert row["si_gap_m"] == 1.0


def test_finite_rejects_missing_and_nonfinite() -> None:
    """Numeric coercion rejects blanks, text, and non-finite values."""
    assert _finite(None) is None
    assert _finite("text") is None
    assert _finite(float("nan")) is None
    assert _finite("4.5") == 4.5


def test_species_mix_returns_empty_for_unknown_or_zero() -> None:
    """Unknown and zero-percent species do not produce a mix."""
    assert _species_mix({"I_SPECIES_CODE_1": "ZZ", "I_SPECIES_PERCENT_1": 100.0}) == {}
    assert _species_mix({"I_SPECIES_CODE_1": "HW", "I_SPECIES_PERCENT_1": 0.0}) == {}


def test_build_validation_rows_skips_invalid_and_unmatched_rows() -> None:
    """Missing ids, SI, species, and unmatched AUs are skipped."""
    rows = _cover().to_dict(orient="records")
    base = dict(rows[0])
    variants = []
    for changes in (
        {"OPENING_ID": None},
        {"FOREST_COVER_ID": None},
        {"SITE_INDEX": None},
        {"I_SPECIES_CODE_1": "ZZ"},
        {"I_SPECIES_CODE_1": "BA"},
        {"I_SPECIES_PERCENT_1": 0.0},
    ):
        row = dict(base)
        row.update(changes)
        variants.append(row)
    with pytest.raises(ValueError, match="no observed cover"):
        build_validation_rows(
            cover=pd.DataFrame(variants),
            curves=_curves(),
            au_table=_au_table(),
            stratum_by_leading={"Hw": "CWH_HW"},
            si_medians={("CWH_HW", "L"): 9.0},
        )


def test_cli_writes_observation_and_summary_csvs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI writes the observation and summary tables."""
    cover_path = tmp_path / "cover.gpkg"
    gpd.GeoDataFrame(
        _cover().iloc[[0]].copy(),
        geometry=[box(0, 0, 1, 1)],
        crs=3005,
    ).to_file(cover_path, driver="GPKG")
    curves_path = tmp_path / "curves.csv"
    _curves().to_csv(curves_path, index=False)
    au_path = tmp_path / "au.csv"
    pd.DataFrame(
        {
            "au_id": [4701000],
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    ).to_csv(au_path, index=False)
    checkpoint = tmp_path / "checkpoint.feather"
    feather.write_feather(
        pd.DataFrame({"au": [4701000], "SITE_INDEX": [9.0], "si_level": ["L"]}),
        checkpoint,
    )
    out = tmp_path / "obs.csv"
    summary_out = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_tipsy_height.py",
            "--tsa",
            "47",
            "--cover",
            str(cover_path),
            "--curves",
            str(curves_path),
            "--au-table",
            str(au_path),
            "--checkpoint",
            str(checkpoint),
            "--out",
            str(out),
            "--summary-out",
            str(summary_out),
        ],
    )
    main()
    assert out.is_file()
    assert summary_out.is_file()
    assert pd.read_csv(out).iloc[0]["predicted_height_m"] == 2.0
