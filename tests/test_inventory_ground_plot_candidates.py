"""Tests for the ground-plot candidate inventory."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

from inventory_ground_plot_candidates import _age_series, inventory_source, main


def _header() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "TSA": [46, 46, 46, 47],
            "SITE_IDENTIFIER": [1, 2, 3, 4],
            "SAMPLE_ESTABLISHMENT_TYPE": ["CMI", "NFI", "NFI", "VRI"],
        }
    )


def _visits() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "SITE_IDENTIFIER": [1, 2, 2, 3, 4],
            "CLSTR_ID": ["1-M1", "2-M1", "2-M2", "3-M1", "4-M1"],
            "PROJ_AGE_ADJ": [40.0, None, 50.0, 90.0, 40.0],
            "PROJ_AGE_1": [None, 40.0, None, None, None],
        }
    )


def test_inventory_source_counts_sites_visits_and_young_rows() -> None:
    """Counts are split by sample type and include an ALL row."""
    inventory = inventory_source(header=_header(), visits=_visits(), tsa=46, source="NONPSP")

    assert len(inventory) == 3
    cmi = inventory[inventory["sample_type"] == "CMI"].iloc[0]
    assert cmi["sites"] == 1
    assert cmi["visits"] == 1
    assert cmi["remeasured_sites"] == 0
    assert cmi["young_sites"] == 1

    nfi = inventory[inventory["sample_type"] == "NFI"].iloc[0]
    assert nfi["sites"] == 2
    assert nfi["visits"] == 3
    assert nfi["remeasured_sites"] == 1
    assert nfi["young_sites"] == 1
    assert nfi["age_known_visits"] == 3

    total = inventory[inventory["sample_type"] == "ALL"].iloc[0]
    assert total["sites"] == 3
    assert total["visits"] == 4
    assert total["remeasured_sites"] == 1
    assert total["management_origin_field"] == "absent"


def test_age_series_without_fallback_column() -> None:
    """A visit table without PROJ_AGE_1 still reports known ages."""
    age = _age_series(pd.DataFrame({"PROJ_AGE_ADJ": [20.0, None]}))
    assert age.iloc[0] == 20.0
    assert pd.isna(age.iloc[1])


def test_main_writes_the_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI reads both sources and writes the inventory CSV."""
    psp_header = tmp_path / "psp_header.csv"
    psp_visits = tmp_path / "psp_visits.csv"
    nonpsp_header = tmp_path / "nonpsp_header.csv"
    nonpsp_visits = tmp_path / "nonpsp_visits.csv"
    out = tmp_path / "inventory.csv"
    pd.DataFrame(
        {
            "TSA": [46],
            "SITE_IDENTIFIER": [10],
            "SAMPLE_ESTABLISHMENT_TYPE": ["PSP_G"],
        }
    ).to_csv(psp_header, index=False)
    pd.DataFrame({"SITE_IDENTIFIER": [10], "PROJ_AGE_ADJ": [60.0]}).to_csv(psp_visits, index=False)
    _header().to_csv(nonpsp_header, index=False)
    _visits().to_csv(nonpsp_visits, index=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_ground_plot_candidates.py",
            "--tsa",
            "46",
            "--psp-header",
            str(psp_header),
            "--psp-visits",
            str(psp_visits),
            "--nonpsp-header",
            str(nonpsp_header),
            "--nonpsp-visits",
            str(nonpsp_visits),
            "--out",
            str(out),
        ],
    )

    main()

    written = pd.read_csv(out)
    assert set(written["source"]) == {"PSP", "NONPSP"}
    assert (written["management_origin_field"] == "absent").all()
    assert "inventory rows" in capsys.readouterr().out


def test_inventory_source_handles_empty_tsa() -> None:
    """A TSA with no header rows reports zero candidates, not a fabricated sample."""
    empty = _header().iloc[0:0]
    inventory = inventory_source(header=empty, visits=_visits(), tsa=99, source="PSP")
    assert len(inventory) == 1
    assert inventory.iloc[0]["sample_type"] == "ALL"
    assert inventory.iloc[0]["sites"] == 0
