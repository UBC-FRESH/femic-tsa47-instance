"""The TSR input builder derives conifer mixes and writes BTC-ready rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.feather as feather
import pytest

from build_tsr_tipsy_input import _as_float, _integer_mix, build_tsr_input, derive_species_mix


def _checkpoint(path: Path) -> Path:
    rows = [
        {
            "au": 4601000,
            "thlb_area": 10.0,
            "SPECIES_CD_1": "CW",
            "SPECIES_PCT_1": 60.0,
            "SPECIES_CD_2": "HW",
            "SPECIES_PCT_2": 30.0,
            "SPECIES_CD_3": "DR",
            "SPECIES_PCT_3": 10.0,
            "SPECIES_CD_4": None,
            "SPECIES_PCT_4": None,
            "SPECIES_CD_5": None,
            "SPECIES_PCT_5": None,
            "SPECIES_CD_6": None,
            "SPECIES_PCT_6": None,
        },
        {
            "au": 4601000,
            "thlb_area": 30.0,
            "SPECIES_CD_1": "CW",
            "SPECIES_PCT_1": 40.0,
            "SPECIES_CD_2": "HW",
            "SPECIES_PCT_2": 20.0,
            "SPECIES_CD_3": "BA",
            "SPECIES_PCT_3": 40.0,
            "SPECIES_CD_4": None,
            "SPECIES_PCT_4": None,
            "SPECIES_CD_5": None,
            "SPECIES_PCT_5": None,
            "SPECIES_CD_6": None,
            "SPECIES_PCT_6": None,
        },
    ]
    feather.write_feather(pd.DataFrame(rows), path)
    return path


def _au_table(path: Path) -> Path:
    pd.DataFrame(
        {
            "au_id": [4601000],
            "source_managed_local_au_id": [21000],
        }
    ).to_csv(path, index=False)
    return path


def _source_input() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "feature_id": 21000,
                "bec_zone": "CWH",
                "bec_subzone": "",
                "planted_species1": "Fdi",
                "planted_density1": 720,
                "planted_species2": "Hwc",
                "planted_density2": 480,
                "planted_species3": "",
                "planted_density3": 0,
                "planted_species4": "",
                "planted_density4": 0,
                "planted_species5": "",
                "planted_density5": 0,
                "genetic_worth1": "",
                "genetic_worth2": "",
                "genetic_worth3": "",
                "genetic_worth4": "",
                "genetic_worth5": "",
                "planting_delay": 1,
                "planted_percent": 100,
                "natural_species1": "",
                "natural_density1": "",
                "natural_species2": "",
                "natural_density2": "",
                "natural_species3": "",
                "natural_density3": "",
                "natural_species4": "",
                "natural_density4": "",
                "natural_species5": "",
                "natural_density5": "",
                "oaf1": 0.59,
                "oaf2": 0.95,
                "opening_id": 21000,
                "fd_si": 9.2,
                "hw_si": 9.2,
                "cw_si": 0.0,
            }
        ]
    )


def test_derive_species_mix_keeps_conifers_and_top_three(tmp_path: Path) -> None:
    """Deciduous codes are excluded and shares are normalized over conifers."""
    mix = derive_species_mix(
        checkpoint_path=_checkpoint(tmp_path / "checkpoint.feather"),
        au_table_path=_au_table(tmp_path / "au.csv"),
    )
    totals = sum(mix[21000].values())
    assert 21000 in mix
    assert totals == 100.0
    assert "Dr" not in mix[21000]
    assert mix[21000]["Cw"] > mix[21000]["Ba"] > mix[21000]["Hw"]


def test_integer_mix_sums_the_density() -> None:
    """Integer species shares reproduce the requested density exactly."""
    result = _integer_mix({"Cw": 50.0, "Hw": 25.0, "Ba": 25.0}, total=1000)
    assert sum(value for _code, value in result) == 1000
    assert [value for _code, value in result] == [500, 250, 250]


def test_build_tsr_input_sets_oaf_si_and_species() -> None:
    """The builder replaces the VRI OAF and writes TSR-consistent rows."""
    frame = build_tsr_input(
        source_input=_source_input(),
        mix_by_au={21000: {"Cw": 60.0, "Hw": 30.0, "Ba": 10.0}},
        density=1000,
        oaf1=0.85,
        oaf2=0.95,
        regen_delay=1,
    )
    row = frame.iloc[0]
    assert row["planted_species1"] == "Cw"
    assert row["planted_species2"] == "Hw"
    assert row["planted_species3"] == "Ba"
    assert row["planted_density1"] + row["planted_density2"] + row["planted_density3"] == 1000
    assert row["oaf1"] == 0.85
    assert row["oaf2"] == 0.95
    assert row["planting_delay"] == 1
    assert row["fd_si"] == 9.2
    assert row["cw_si"] == 9.2
    assert row["natural_species1"] == ""


def test_build_tsr_input_auto_delay_for_cedar() -> None:
    """Omitted delay uses one year for a cedar-leading mix."""
    frame = build_tsr_input(
        source_input=_source_input(),
        mix_by_au={21000: {"Cw": 100.0}},
        density=1000,
        oaf1=0.85,
        oaf2=0.95,
        regen_delay=None,
    )
    assert frame.iloc[0]["planting_delay"] == 1


def test_as_float_rejects_missing_and_text() -> None:
    """Numeric coercion returns None for blanks and text."""
    assert _as_float(None) is None
    assert _as_float("text") is None
    assert _as_float("4.5") == 4.5


def test_cli_writes_the_tsr_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI entry point writes the TSR-consistent CSV."""
    import sys

    from build_tsr_tipsy_input import main

    source = tmp_path / "source.csv"
    _source_input().to_csv(source, index=False)
    out = tmp_path / "out.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_tsr_tipsy_input.py",
            "--tsa",
            "46",
            "--checkpoint",
            str(_checkpoint(tmp_path / "checkpoint.feather")),
            "--au-table",
            str(_au_table(tmp_path / "au.csv")),
            "--source-input",
            str(source),
            "--out",
            str(out),
            "--density",
            "1000",
        ],
    )
    main()
    frame = pd.read_csv(out)
    assert len(frame) == 1
    assert frame.iloc[0]["oaf1"] == 0.85
