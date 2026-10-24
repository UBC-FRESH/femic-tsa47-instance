"""Tests for the managed-land SI holdout input builder."""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyarrow.feather as feather
import pytest
from shapely.geometry import box

from build_managed_si_input import (
    _finite,
    _species_mix,
    apply_managed_si,
    main,
    managed_si_by_cell,
    observed_management_rows,
)


def _cover() -> pd.DataFrame:
    rows = []
    for opening_id, si in ((1, 10.0), (2, 20.0)):
        rows.append(
            {
                "OPENING_ID": opening_id,
                "BGC_ZONE_CODE": "CWH",
                "SITE_INDEX": si,
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
            }
        )
    return pd.DataFrame(rows)


def _au_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "au_id": [4601001],
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    )


def test_observed_management_rows_assigns_au_and_si() -> None:
    """Observed rows carry the model AU and observed SI."""
    frame = observed_management_rows(
        cover=_cover(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
    )
    assert frame["opening_id"].tolist() == [1, 2]
    assert frame["observed_si"].tolist() == [10.0, 20.0]
    assert frame["stratum_code"].tolist() == ["CWH_HW", "CWH_HW"]


def test_managed_si_by_cell_uses_training_only() -> None:
    """The holdout row does not contribute to the managed SI."""
    observations = observed_management_rows(
        cover=_cover(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
    )
    result = managed_si_by_cell(
        observations=observations,
        holdout_mod=2,
        holdout_seed=0,
        min_train_n=1,
    )
    row = result.iloc[0]
    assert row["n_train"] == 1
    assert row["n_holdout"] == 1
    assert row["managed_si"] == 10.0


def test_managed_si_by_cell_respects_minimum_training_count() -> None:
    """A cell with too few training rows is not used."""
    observations = observed_management_rows(
        cover=_cover(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
    )
    result = managed_si_by_cell(
        observations=observations,
        holdout_mod=2,
        holdout_seed=0,
        min_train_n=2,
    )
    assert not bool(result.iloc[0]["used"])
    assert result.iloc[0]["managed_si"] is None


def test_apply_managed_si_changes_all_si_columns() -> None:
    """A mapped AU gets the managed SI on every species column."""
    base = pd.DataFrame(
        {
            "feature_id": [21000, 22000],
            "fd_si": [1.0, 2.0],
            "hw_si": [1.0, 2.0],
            "cw_si": [1.0, 2.0],
        }
    )
    managed = pd.DataFrame(
        [
            {
                "stratum_code": "CWH_HW",
                "si_level": "L",
                "n_train": 10,
                "n_holdout": 2,
                "managed_si": 23.0,
                "used": True,
            }
        ]
    )
    au_table = pd.DataFrame(
        {
            "source_managed_local_au_id": [21000, 22000],
            "stratum_code": ["CWH_HW", "CWH_HW"],
            "si_level": ["L", "M"],
        }
    )
    updated, applied = apply_managed_si(
        base_input=base,
        au_table=au_table,
        managed_si=managed,
    )
    assert updated.iloc[0]["fd_si"] == 23.0
    assert updated.iloc[0]["hw_si"] == 23.0
    assert updated.iloc[1]["fd_si"] == 2.0
    assert len(applied) == 1


def test_finite_and_species_mix_helpers() -> None:
    """The scalar helpers reject blanks and normalize species."""
    assert _finite(None) is None
    assert _finite("4.5") == 4.5
    assert _species_mix({"I_SPECIES_CODE_1": "HW", "I_SPECIES_PERCENT_1": 100}) == {"Hw": 100.0}


def test_cli_writes_managed_si_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI writes the modified input and the audit table."""
    cover_path = tmp_path / "cover.gpkg"
    gpd.GeoDataFrame(
        _cover(),
        geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)],
        crs=3005,
    ).to_file(cover_path, driver="GPKG")
    base_path = tmp_path / "base.csv"
    pd.DataFrame(
        {
            "feature_id": [21000],
            "fd_si": [1.0],
            "hw_si": [1.0],
            "cw_si": [1.0],
        }
    ).to_csv(base_path, index=False)
    au_path = tmp_path / "au.csv"
    _au_table().to_csv(au_path, index=False)
    checkpoint = tmp_path / "checkpoint.feather"
    feather.write_feather(
        pd.DataFrame({"au": [4601001], "SITE_INDEX": [9.0], "si_level": ["L"]}),
        checkpoint,
    )
    out_input = tmp_path / "input.csv"
    out_summary = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_managed_si_input.py",
            "--tsa",
            "46",
            "--cover",
            str(cover_path),
            "--base-input",
            str(base_path),
            "--au-table",
            str(au_path),
            "--checkpoint",
            str(checkpoint),
            "--holdout-mod",
            "2",
            "--holdout-seed",
            "0",
            "--min-train-n",
            "1",
            "--out-input",
            str(out_input),
            "--out-summary",
            str(out_summary),
        ],
    )
    main()
    assert out_input.is_file()
    assert out_summary.is_file()
    assert pd.read_csv(out_input).iloc[0]["fd_si"] == 10.0
