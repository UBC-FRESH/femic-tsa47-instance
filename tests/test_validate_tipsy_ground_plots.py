"""Tests for the Nemora/FAIB ground-plot validation table."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.feather as feather
import pytest

from validate_tipsy_ground_plots import (
    _finite,
    _schema_columns,
    build_validation_rows,
    main,
    summarize_validation,
)


def _header() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "SITE_IDENTIFIER": [1],
            "BEC_ZONE": ["CWH"],
            "SAMPLE_ESTABLISHMENT_TYPE": ["CMI"],
        }
    )


def _manifest() -> pd.DataFrame:
    return pd.DataFrame({"cluster_id": ["1-M1"], "visit_number": [1], "site_identifier": [1]})


def _smries() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "CLSTR_ID": ["1-M1"],
            "VISIT_NUMBER": [1],
            "UTIL": [12.5],
            "VHA_NTWB_LS": [100.0],
            "QMD_LS": [20.0],
            "STEMS_HA_LS": [800.0],
        }
    )


def _species() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "CLSTR_ID": ["1-M1"],
            "VISIT_NUMBER": [1],
            "UTIL": [12.5],
            "SPECIES": ["HW"],
            "SP_PCT_BA_LS": [100.0],
        }
    )


def _siteage() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "CLSTR_ID": ["1-M1"],
            "VISIT_NUMBER": [1],
            "SPECIES": ["HW"],
            "AGET_TLSO": [50.0],
            "HT_TLSO": [20.0],
            "SI_M_TLSO": [9.0],
        }
    )


def _curves() -> pd.DataFrame:
    ages = np.arange(0, 61)
    return pd.DataFrame(
        {
            "AU": [21000] * len(ages),
            "Age": ages,
            "Yield": ages * 2.0,
            "Height": ages * 0.4,
            "DBHg000": [20.0] * len(ages),
            "StemCount125": [800.0] * len(ages),
        }
    )


def _au_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "au_id": [4601001],
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    )


def test_schema_columns_detects_non_psp() -> None:
    """The non-PSP summary schema is recognized."""
    assert _schema_columns(_smries())["schema"] == "non_psp"


def test_build_validation_rows_matches_au_and_metrics() -> None:
    """A synthetic CMI plot produces observed/predicted metrics at age 50."""
    frame = build_validation_rows(
        header=_header(),
        manifest=_manifest(),
        smries=_smries(),
        species=_species(),
        siteage=_siteage(),
        curves=_curves(),
        au_table=_au_table(),
        stratum_by_leading={"Hw": "CWH_HW"},
        si_medians={("CWH_HW", "L"): 9.0},
    )
    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["sample_type"] == "CMI"
    assert row["local_au"] == 21000
    assert row["observed_volume"] == 100.0
    assert row["predicted_volume"] == 100.0
    assert row["observed_dbh"] == 20.0
    assert row["predicted_dbh"] == 20.0
    assert row["age_class"] == "31-50"


def test_build_validation_rows_rejects_unmatched() -> None:
    """No matching age/species is a blocking input error."""
    with pytest.raises(ValueError, match="no ground-plot rows"):
        build_validation_rows(
            header=_header().iloc[0:0],
            manifest=_manifest(),
            smries=_smries(),
            species=_species(),
            siteage=_siteage(),
            curves=_curves(),
            au_table=_au_table(),
            stratum_by_leading={"Hw": "CWH_HW"},
            si_medians={("CWH_HW", "L"): 9.0},
        )


def test_summarize_validation_reports_bias() -> None:
    """A perfect prediction has zero bias and error."""
    frame = pd.DataFrame(
        {
            "sample_type": ["CMI"],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
            "age_class": ["31-50"],
            "observed_volume": [100.0],
            "predicted_volume": [100.0],
            "observed_dbh": [20.0],
            "predicted_dbh": [20.0],
            "observed_height": [20.0],
            "predicted_height": [20.0],
            "observed_stems": [800.0],
            "predicted_stems": [800.0],
        }
    )
    summary = summarize_validation(frame)
    assert set(summary["metric"]) == {"volume", "dbh", "height", "stems"}
    assert (summary["bias"] == 0.0).all()


def test_finite_rejects_missing() -> None:
    """Numeric coercion rejects blanks and text."""
    assert _finite(None) is None
    assert _finite("text") is None
    assert _finite("4.5") == 4.5


def test_cli_writes_validation_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI writes observations and summary CSVs."""
    header = tmp_path / "header.csv"
    manifest = tmp_path / "manifest.csv"
    smries = tmp_path / "smries.csv"
    species = tmp_path / "species.csv"
    siteage = tmp_path / "siteage.csv"
    curves = tmp_path / "curves.csv"
    au_table = tmp_path / "au.csv"
    checkpoint = tmp_path / "checkpoint.feather"
    _header().to_csv(header, index=False)
    _manifest().to_csv(manifest, index=False)
    _smries().to_csv(smries, index=False)
    _species().to_csv(species, index=False)
    _siteage().to_csv(siteage, index=False)
    _curves().to_csv(curves, index=False)
    _au_table().to_csv(au_table, index=False)
    feather.write_feather(
        pd.DataFrame({"au": [4601001], "SITE_INDEX": [9.0], "si_level": ["L"]}),
        checkpoint,
    )
    out = tmp_path / "obs.csv"
    summary_out = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_tipsy_ground_plots.py",
            "--tsa",
            "46",
            "--header",
            str(header),
            "--manifest",
            str(manifest),
            "--smries",
            str(smries),
            "--species",
            str(species),
            "--siteage",
            str(siteage),
            "--curves",
            str(curves),
            "--au-table",
            str(au_table),
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


def test_predict_returns_none_for_missing_column() -> None:
    """A missing TIPSY column is skipped rather than interpolated."""
    from validate_tipsy_ground_plots import _predict

    assert _predict(_curves(), 50.0, "not_a_column") is None


def test_schema_columns_detects_psp_and_rejects_unknown() -> None:
    """PSP columns are recognized; an unknown schema is a clear error."""
    psp = pd.DataFrame(
        {
            "VHA_DWB_LIV": [1.0],
            "QMD_LIV": [1.0],
            "STEMS_HA_LIV": [1.0],
            "SP_PCT_BA_LI": [1.0],
            "AGE_TOT1": [1.0],
            "HTOP1": [1.0],
            "SI1": [1.0],
        }
    )
    assert _schema_columns(psp)["schema"] == "psp"
    with pytest.raises(ValueError, match="Unrecognized FAIB summary"):
        _schema_columns(pd.DataFrame({"other": [1]}))


def test_build_validation_rows_skips_bad_manifest_rows() -> None:
    """Missing site, visit, key, age, AU mapping, or curve are skipped."""
    bad_manifests = [
        pd.DataFrame({"cluster_id": ["x"], "visit_number": [1], "site_identifier": [999]}),
        pd.DataFrame({"cluster_id": ["x"], "visit_number": [None], "site_identifier": [1]}),
        pd.DataFrame({"cluster_id": ["missing"], "visit_number": [1], "site_identifier": [1]}),
    ]
    for manifest in bad_manifests:
        with pytest.raises(ValueError, match="no ground-plot rows"):
            build_validation_rows(
                header=_header(),
                manifest=manifest,
                smries=_smries(),
                species=_species(),
                siteage=_siteage(),
                curves=_curves(),
                au_table=_au_table(),
                stratum_by_leading={"Hw": "CWH_HW"},
                si_medians={("CWH_HW", "L"): 9.0},
            )
    no_age = _siteage()
    no_age["AGET_TLSO"] = None
    with pytest.raises(ValueError, match="no ground-plot rows"):
        build_validation_rows(
            header=_header(),
            manifest=_manifest(),
            smries=_smries(),
            species=_species(),
            siteage=no_age,
            curves=_curves(),
            au_table=_au_table(),
            stratum_by_leading={"Hw": "CWH_HW"},
            si_medians={("CWH_HW", "L"): 9.0},
        )
    with pytest.raises(ValueError, match="no ground-plot rows"):
        build_validation_rows(
            header=_header(),
            manifest=_manifest(),
            smries=_smries(),
            species=_species(),
            siteage=_siteage(),
            curves=_curves(),
            au_table=_au_table().iloc[0:0],
            stratum_by_leading={"Hw": "CWH_HW"},
            si_medians={("CWH_HW", "L"): 9.0},
        )


def test_summarize_validation_skips_all_missing_metrics() -> None:
    """Metrics with no positive observed/predicted pairs are omitted."""
    frame = pd.DataFrame(
        {
            "sample_type": ["CMI"],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
            "age_class": ["31-50"],
            "observed_volume": [None],
            "predicted_volume": [None],
            "observed_dbh": [None],
            "predicted_dbh": [None],
            "observed_height": [None],
            "predicted_height": [None],
            "observed_stems": [None],
            "predicted_stems": [None],
        }
    )
    assert summarize_validation(frame).empty
