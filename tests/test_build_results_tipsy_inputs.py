"""Tests for the RESULTS-derived TIPSY input workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyarrow.feather as feather
import pytest
from shapely.geometry import box

from build_results_tipsy_inputs import (
    _genetic_worth,
    _to_float,
    _to_int,
    _weighted_species,
    aggregate,
    apply_candidates_to_input,
    assign_au,
    main,
    normalize_species,
    stratum_by_leading_from_au_table,
)


def test_normalize_species_maps_results_codes() -> None:
    """RESULTS species codes map to the model's mixed-case codes."""
    assert normalize_species("FDC") == "Fd"
    assert normalize_species(" HW ") == "Hw"
    assert normalize_species(None) is None


def test_assign_au_uses_leading_species_and_si() -> None:
    """A hemlock-leading opening at low SI assigns to CWH_HW L."""
    assert assign_au(
        bec_zone="CWH",
        species_pct={"Hw": 70, "Ba": 30},
        site_index=12.0,
    ) == ("CWH_HW", "L")


def test_assign_au_rejects_unknown_leading_species() -> None:
    """An unsupported leading species is not assigned."""
    assert (
        assign_au(
            bec_zone="CWH",
            species_pct={"Dr": 100},
            site_index=20.0,
        )
        is None
    )


def test_genetic_worth_uses_data_package_values() -> None:
    """Table 45 values are attached to the species mix."""
    payload = json.loads(_genetic_worth('{"Hw": 70, "Fd": 30}'))
    assert payload == {"Hw": 0.0, "Fd": 3.0}


def test_weighted_species_combines_openings() -> None:
    """Species percentages are weighted across matching openings."""
    frame = pd.DataFrame(
        {
            "stratum_code": ["CWH_HW", "CWH_HW"],
            "si_level": ["L", "L"],
            "species_mix": ['{"Hw": 100}', '{"Hw": 50, "Ba": 50}'],
        }
    )
    result = json.loads(_weighted_species(frame, stratum="CWH_HW", level="L"))
    assert result["Hw"] == 75.0
    assert result["Ba"] == 25.0


def test_aggregate_assigns_one_opening(tmp_path: Path) -> None:
    """A synthetic RESULTS opening produces one AU candidate row."""
    aoi = gpd.GeoDataFrame({"name": ["aoi"]}, geometry=[box(0, 0, 100, 100)], crs=3005)
    openings = gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "GENERALIZED_BGC_ZONE_CODE": ["CWH"],
        },
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )
    cover = gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "FOREST_COVER_ID": [10],
            "REFERENCE_YEAR": [2020],
            "BGC_ZONE_CODE": ["CWH"],
            "SITE_INDEX": [12.0],
            "I_TOTAL_STEMS_PER_HA": [1200.0],
            "I_SPECIES_CODE_1": ["HW"],
            "I_SPECIES_PERCENT_1": [100.0],
            "I_SPECIES_CODE_2": [None],
            "I_SPECIES_PERCENT_2": [None],
            "I_SPECIES_CODE_3": [None],
            "I_SPECIES_PERCENT_3": [None],
            "I_SPECIES_CODE_4": [None],
            "I_SPECIES_PERCENT_4": [None],
            "I_SPECIES_CODE_5": [None],
            "I_SPECIES_PERCENT_5": [None],
        },
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )
    planting = gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "SILV_TREE_SPECIES_CODE": ["HW"],
            "NUMBER_PLANTED": [1200],
            "ACTUAL_TREATMENT_AREA": [1.0],
        },
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )

    result = aggregate(openings=openings, cover=cover, planting=planting, aoi=aoi)

    assert len(result) == 1
    assert result.iloc[0]["stratum_code"] == "CWH_HW"
    assert result.iloc[0]["si_level"] == "L"
    assert result.iloc[0]["oaf1"] == 0.85
    assert result.iloc[0]["oaf2"] == 0.95


def test_assign_au_rejects_missing_site_index() -> None:
    """An opening without site index cannot be assigned to an SI class."""
    assert (
        assign_au(
            bec_zone="CWH",
            species_pct={"Hw": 100.0},
            site_index=None,
        )
        is None
    )


def test_main_reads_fetched_layers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI reads the three RESULTS layers and writes the candidate CSV."""
    root = tmp_path / "bcdc"
    for name, frame in {
        "WHSE_FOREST_VEGETATION_RSLT_OPENING_SVW": _openings_frame(),
        "WHSE_FOREST_VEGETATION_RSLT_FOREST_COVER_INV_SVW": _cover_frame(),
        "WHSE_FOREST_VEGETATION_RSLT_PLANTING_SVW": _planting_frame(),
    }.items():
        directory = root / name
        directory.mkdir(parents=True)
        frame.to_file(directory / f"{name}.gpkg", driver="GPKG")
    aoi_path = tmp_path / "aoi.gpkg"
    gpd.GeoDataFrame({"name": ["aoi"]}, geometry=[box(0, 0, 100, 100)], crs=3005).to_file(
        aoi_path, driver="GPKG"
    )
    out = tmp_path / "candidates.csv"
    base_input = tmp_path / "base.csv"
    au_table = tmp_path / "au_table.csv"
    tipsy_input = tmp_path / "tipsy.csv"
    pd.DataFrame(
        {
            "feature_id": [21000],
            "bec_zone": ["CWH"],
            "planted_species1": ["Hw"],
            "planted_density1": [1.0],
            "genetic_worth1": [0.0],
            "oaf1": [1.0],
            "oaf2": [1.0],
            "hw_si": [0.0],
            "fd_si": [0.0],
        }
    ).to_csv(base_input, index=False)
    pd.DataFrame(
        {
            "au_id": [4701000],
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    ).to_csv(au_table, index=False)
    checkpoint = tmp_path / "checkpoint.feather"
    feather.write_feather(
        pd.DataFrame({"au": [4701000], "SITE_INDEX": [12.0], "si_level": ["L"]}),
        checkpoint,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_results_tipsy_inputs.py",
            "--download-root",
            str(root),
            "--aoi",
            str(aoi_path),
            "--out",
            str(out),
            "--tipsy-input",
            str(tipsy_input),
            "--base-input",
            str(base_input),
            "--au-table",
            str(au_table),
            "--checkpoint",
            str(checkpoint),
        ],
    )

    main()

    assert out.is_file()
    result = pd.read_csv(out)
    assert len(result) == 1
    assert result.iloc[0]["stratum_code"] == "CWH_HW"
    updated = pd.read_csv(tipsy_input)
    assert updated.iloc[0]["planted_species1"] == "Hw"
    assert updated.iloc[0]["planted_density1"] == 1200

    # The candidate table is still written when no TIPSY input is requested.
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_results_tipsy_inputs.py",
            "--download-root",
            str(root),
            "--aoi",
            str(aoi_path),
            "--out",
            str(out),
            "--au-table",
            str(au_table),
            "--checkpoint",
            str(checkpoint),
        ],
    )
    main()
    assert out.is_file()


def test_apply_candidates_merges_fdc_into_fd() -> None:
    """RESULTS Fdc is normalized to the model Fd code before density split."""
    candidates = pd.DataFrame(
        [
            {
                "stratum_code": "CWH_FD",
                "si_level": "M",
                "species_mix": '{"Fdc": 75, "Hw": 25}',
                "median_density": 1000.0,
                "median_si": 28.0,
                "oaf1": 0.85,
                "oaf2": 0.95,
            }
        ]
    )
    base_input = pd.DataFrame(
        {
            "feature_id": [22003],
            "bec_zone": ["CWH"],
            "planted_species1": ["Fd"],
            "planted_species4": [float("nan")],
            "planted_density1": [1.0],
            "genetic_worth1": [0.0],
            "oaf1": [1.0],
            "oaf2": [1.0],
            "fd_si": [0.0],
            "hw_si": [0.0],
        }
    )
    au_table = pd.DataFrame(
        {
            "source_managed_local_au_id": [22003],
            "stratum_code": ["CWH_FD"],
            "si_level": ["M"],
        }
    )

    updated = apply_candidates_to_input(
        candidates=candidates,
        base_input=base_input,
        au_table=au_table,
    )

    assert updated.iloc[0]["planted_species1"] == "Fd"
    assert updated.iloc[0]["planted_density1"] == 750
    assert updated["planted_density1"].dtype == "int64"
    assert updated.iloc[0]["planted_species2"] == "Hw"
    assert updated.iloc[0]["fd_si"] == 28.0
    assert updated.iloc[0]["oaf2"] == 0.95


def _openings_frame() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"OPENING_ID": [1], "GENERALIZED_BGC_ZONE_CODE": ["CWH"]},
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )


def _cover_frame() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "FOREST_COVER_ID": [10],
            "REFERENCE_YEAR": [2020],
            "BGC_ZONE_CODE": ["CWH"],
            "SITE_INDEX": [12.0],
            "I_TOTAL_STEMS_PER_HA": [1200.0],
            "I_SPECIES_CODE_1": ["HW"],
            "I_SPECIES_PERCENT_1": [100.0],
            "I_SPECIES_CODE_2": [None],
            "I_SPECIES_PERCENT_2": [None],
            "I_SPECIES_CODE_3": [None],
            "I_SPECIES_PERCENT_3": [None],
            "I_SPECIES_CODE_4": [None],
            "I_SPECIES_PERCENT_4": [None],
            "I_SPECIES_CODE_5": [None],
            "I_SPECIES_PERCENT_5": [None],
        },
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )


def _planting_frame() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "SILV_TREE_SPECIES_CODE": ["HW"],
            "NUMBER_PLANTED": [1200],
            "ACTUAL_TREATMENT_AREA": [1.0],
        },
        geometry=[box(10, 10, 20, 20)],
        crs=3005,
    )


def test_assign_au_rejects_empty_species() -> None:
    """An opening with no species composition is not assigned."""
    assert assign_au(bec_zone="CWH", species_pct={}, site_index=12.0) is None


def test_weighted_species_returns_empty_for_no_matches() -> None:
    """An AU with no rows returns an empty JSON object."""
    frame = pd.DataFrame(
        {"stratum_code": ["CWH_HW"], "si_level": ["L"], "species_mix": ['{"Hw": 100}']}
    )
    assert _weighted_species(frame, stratum="CWH_CW", level="H") == "{}"


def test_aggregate_rejects_no_assignable_openings() -> None:
    """An AOI with no assignable openings is a blocking input error."""
    aoi = gpd.GeoDataFrame({"name": ["aoi"]}, geometry=[box(0, 0, 100, 100)], crs=3005)
    openings = gpd.GeoDataFrame(
        {"OPENING_ID": [1], "GENERALIZED_BGC_ZONE_CODE": ["CWH"]},
        geometry=[box(200, 200, 210, 210)],
        crs=3005,
    )
    cover = _cover_frame()
    planting = _planting_frame()
    with pytest.raises(ValueError, match="no RESULTS openings"):
        aggregate(openings=openings, cover=cover, planting=planting, aoi=aoi)


def test_apply_candidates_skips_unmapped_unknown_and_empty() -> None:
    """Unmapped AUs, unknown species, and empty mixes are ignored safely."""
    candidates = pd.DataFrame(
        [
            {
                "stratum_code": "CWH_HW",
                "si_level": "L",
                "species_mix": '{"Hw": 100, "ZZ": 5}',
                "median_density": 1000.0,
                "median_si": 12.0,
                "oaf1": 0.85,
                "oaf2": 0.95,
            },
            {
                "stratum_code": "CWH_HW",
                "si_level": "H",
                "species_mix": '{"ZZ": 100}',
                "median_density": 1000.0,
                "median_si": 28.0,
                "oaf1": 0.85,
                "oaf2": 0.95,
            },
        ]
    )
    base_input = pd.DataFrame(
        {
            "feature_id": [21000, 99999, 23000],
            "bec_zone": ["CWH", "CWH", "CWH"],
            "planted_species1": ["", "", ""],
            "planted_density1": [0.0, 0.0, 0.0],
            "genetic_worth1": [0.0, 0.0, 0.0],
            "oaf1": [1.0, 1.0, 1.0],
            "oaf2": [1.0, 1.0, 1.0],
            "hw_si": [0.0, 0.0, 0.0],
        }
    )
    au_table = pd.DataFrame(
        {
            "source_managed_local_au_id": [21000, 23000],
            "stratum_code": ["CWH_HW", "CWH_HW"],
            "si_level": ["L", "H"],
        }
    )

    updated = apply_candidates_to_input(
        candidates=candidates,
        base_input=base_input,
        au_table=au_table,
    )

    assert updated.iloc[0]["planted_species1"] == "Hw"
    assert updated.iloc[1]["planted_species1"] == ""
    assert updated.iloc[2]["planted_species1"] == ""


def test_to_float_handles_missing_and_nonfinite() -> None:
    """Numeric coercion rejects missing, non-numeric, and non-finite values."""
    assert _to_float(None) is None
    assert _to_float("not-a-number") is None
    assert _to_float(float("nan")) is None
    assert _to_float("12.5") == 12.5
    assert _to_int("7.9") == 7
    assert _to_int(None) is None


def test_aggregate_rejects_openings_without_usable_attributes() -> None:
    """Openings without species, density, or site index do not form records."""
    aoi = gpd.GeoDataFrame({"name": ["aoi"]}, geometry=[box(0, 0, 100, 100)], crs=3005)
    openings = gpd.GeoDataFrame(
        {
            "OPENING_ID": [1, 2, 3],
            "GENERALIZED_BGC_ZONE_CODE": ["CWH", "CWH", "CWH"],
        },
        geometry=[box(1, 1, 2, 2), box(3, 3, 4, 4), box(5, 5, 6, 6)],
        crs=3005,
    )
    cover_rows = []
    for opening_id, species, si in [
        (1, None, 12.0),
        (2, "DR", 12.0),
        (3, "HW", None),
    ]:
        cover_rows.append(
            {
                "OPENING_ID": opening_id,
                "FOREST_COVER_ID": opening_id,
                "REFERENCE_YEAR": 2020,
                "BGC_ZONE_CODE": "CWH",
                "SITE_INDEX": si,
                "I_TOTAL_STEMS_PER_HA": 1200.0,
                "I_SPECIES_CODE_1": species,
                "I_SPECIES_PERCENT_1": 100.0 if species else None,
                "I_SPECIES_CODE_2": None,
                "I_SPECIES_PERCENT_2": None,
                "I_SPECIES_CODE_3": None,
                "I_SPECIES_PERCENT_3": None,
                "I_SPECIES_CODE_4": None,
                "I_SPECIES_PERCENT_4": None,
                "I_SPECIES_CODE_5": None,
                "I_SPECIES_PERCENT_5": None,
                "geometry": box(opening_id, opening_id, opening_id + 1, opening_id + 1),
            }
        )
    cover = gpd.GeoDataFrame(cover_rows, crs=3005)
    planting = gpd.GeoDataFrame(
        {
            "OPENING_ID": [1],
            "SILV_TREE_SPECIES_CODE": ["ZZ"],
            "NUMBER_PLANTED": [0],
            "ACTUAL_TREATMENT_AREA": [1.0],
        },
        geometry=[box(1, 1, 2, 2)],
        crs=3005,
    )

    with pytest.raises(ValueError, match="no RESULTS openings"):
        aggregate(openings=openings, cover=cover, planting=planting, aoi=aoi)


def test_apply_candidates_skips_bad_ids_and_missing_values() -> None:
    """Bad ids, missing candidates, and missing densities are skipped."""
    candidates = pd.DataFrame(
        [
            {
                "stratum_code": "CWH_HW",
                "si_level": "L",
                "species_mix": '{"Hw": 100}',
                "median_density": None,
                "median_si": 12.0,
                "oaf1": 0.85,
                "oaf2": 0.95,
            },
            {
                "stratum_code": "CWH_HW",
                "si_level": "M",
                "species_mix": '{"Hw": 100}',
                "median_density": 1000.0,
                "median_si": 18.0,
                "oaf1": None,
                "oaf2": None,
            },
        ]
    )
    base_input = pd.DataFrame(
        {
            "feature_id": [21000, 22000, 23000, 99999, "bad"],
            "bec_zone": ["CWH"] * 5,
            "planted_species1": ["", "", "", "", ""],
            "planted_density1": [0.0] * 5,
            "genetic_worth1": [0.0] * 5,
            "oaf1": [1.0] * 5,
            "oaf2": [1.0] * 5,
            "hw_si": [0.0] * 5,
        }
    )
    au_table = pd.DataFrame(
        {
            "source_managed_local_au_id": [21000, 22000, 23000, float("nan")],
            "stratum_code": ["CWH_HW", "CWH_HW", "CWH_HW", "CWH_HW"],
            "si_level": ["L", "M", "H", "L"],
        }
    )

    updated = apply_candidates_to_input(
        candidates=candidates,
        base_input=base_input,
        au_table=au_table,
    )

    assert updated.iloc[0]["planted_species1"] == ""
    assert updated.iloc[1]["planted_species1"] == "Hw"
    assert updated.iloc[1]["oaf1"] == 1.0
    assert updated.iloc[2]["planted_species1"] == ""
    assert updated.iloc[3]["planted_species1"] == ""
    assert updated.iloc[4]["planted_species1"] == ""


def test_stratum_map_uses_the_tsa47_au_table() -> None:
    """The AU table supplies the TSA 47 stratum map, including MH_HM and CWH_BA."""
    au_table = pd.DataFrame(
        {
            "stratum_code": ["CWH_HW", "CWH_CW", "CWH_YC", "CWH_FD", "MH_HM", "CWH_BA"],
        }
    )
    result = stratum_by_leading_from_au_table(au_table)
    assert result == {
        "Hw": "CWH_HW",
        "Cw": "CWH_CW",
        "Yc": "CWH_YC",
        "Fd": "CWH_FD",
        "Hm": "MH_HM",
        "Ba": "CWH_BA",
    }


def test_aggregate_does_not_use_overstory_stems_as_regeneration_density(
    tmp_path: Path,
) -> None:
    """No planting record leaves density blank rather than overstory stems."""
    aoi = gpd.GeoDataFrame({"name": ["aoi"]}, geometry=[box(0, 0, 100, 100)], crs=3005)
    openings = _openings_frame()
    cover = _cover_frame()
    planting = _planting_frame().iloc[0:0]
    result = aggregate(openings=openings, cover=cover, planting=planting, aoi=aoi)
    row = result.iloc[0]
    assert pd.isna(row["median_density"])
    assert row["density_source"] == "missing"


def test_apply_candidates_uses_fallback_density_when_planting_is_missing() -> None:
    """A missing RESULT density keeps the RESULTS mix and uses the fallback."""
    candidates = pd.DataFrame(
        [
            {
                "stratum_code": "CWH_HW",
                "si_level": "L",
                "species_mix": '{"Hw": 75, "Cw": 25}',
                "median_density": None,
                "median_si": 12.0,
                "oaf1": 0.85,
                "oaf2": 0.95,
            }
        ]
    )
    base_input = pd.DataFrame(
        {
            "feature_id": [21000],
            "bec_zone": ["CWH"],
            "planted_species1": ["Cw"],
            "planted_density1": [1.0],
            "genetic_worth1": [0.0],
            "oaf1": [1.0],
            "oaf2": [1.0],
            "hw_si": [0.0],
            "cw_si": [0.0],
        }
    )
    au_table = pd.DataFrame(
        {
            "source_managed_local_au_id": [21000],
            "stratum_code": ["CWH_HW"],
            "si_level": ["L"],
        }
    )
    updated = apply_candidates_to_input(
        candidates=candidates,
        base_input=base_input,
        au_table=au_table,
        fallback_density=1000.0,
    )
    assert updated.iloc[0]["planted_species1"] == "Hw"
    assert updated.iloc[0]["planted_density1"] == 750
    assert updated.iloc[0]["planted_species2"] == "Cw"
    assert updated.iloc[0]["planted_density2"] == 250
