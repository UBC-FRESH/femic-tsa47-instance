"""Tests for the TSA boundary builder."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from build_aoi import build_aoi, main


def _write_source(path: Path) -> None:
    """Write a small FADM-like GeoPackage with current, block, and retired rows."""
    frame = gpd.GeoDataFrame(
        {
            "TSA_NUMBER": ["46", "46", "46", "47"],
            "TSA_NUMBER_DESCRIPTION": ["GBR North TSA"] * 3 + ["GBR South TSA"],
            "TSB_NUMBER": [None, "V 46A", None, None],
            "RETIREMENT_DATE": [None, None, "2017-01-05", None],
            "FEATURE_AREA_SQM": [10000.0, 4000.0, 10000.0, 5000.0],
        },
        geometry=[box(0, 0, 10, 10), box(0, 0, 4, 10), box(0, 0, 10, 10), box(20, 0, 30, 10)],
        crs="EPSG:3005",
    )
    frame.to_file(path, layer="WHSE_ADMIN_BOUNDARIES_FADM_TSA", driver="GPKG")


def test_build_aoi_selects_only_the_current_dissolved_feature(tmp_path: Path) -> None:
    """A supply block and a retired row are not the model boundary."""
    source = tmp_path / "tsa.gpkg"
    _write_source(source)
    out = tmp_path / "tsa46_full.gpkg"

    summary = build_aoi(source=source, tsa_number="46", out=out)

    result = gpd.read_file(out, layer="tsa46_full")
    assert len(result) == 1
    assert summary["gross_area_ha"] == pytest.approx(0.01)
    assert summary["tsa_number"] == "46"
    assert summary["crs"] == "EPSG:3005"


def test_build_aoi_rejects_a_missing_boundary(tmp_path: Path) -> None:
    """A TSA with no current dissolved row is an error."""
    source = tmp_path / "tsa.gpkg"
    _write_source(source)
    with pytest.raises(ValueError, match="expected one"):
        build_aoi(source=source, tsa_number="99", out=tmp_path / "out.gpkg")


def test_build_aoi_rejects_a_duplicate_current_row(tmp_path: Path) -> None:
    """Two current dissolved rows for one TSA are ambiguous and rejected."""
    source = tmp_path / "tsa.gpkg"
    frame = gpd.GeoDataFrame(
        {
            "TSA_NUMBER": ["46", "46"],
            "TSA_NUMBER_DESCRIPTION": ["GBR North TSA", "GBR North TSA"],
            "TSB_NUMBER": [None, None],
            "RETIREMENT_DATE": [None, None],
        },
        geometry=[box(0, 0, 10, 10), box(10, 0, 20, 10)],
        crs="EPSG:3005",
    )
    frame.to_file(source, layer="WHSE_ADMIN_BOUNDARIES_FADM_TSA", driver="GPKG")
    with pytest.raises(ValueError, match="found 2"):
        build_aoi(source=source, tsa_number="46", out=tmp_path / "out.gpkg")


def test_main_writes_the_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI entry point writes the GeoPackage and its summary JSON."""
    source = tmp_path / "tsa.gpkg"
    _write_source(source)
    out = tmp_path / "tsa46_full.gpkg"
    summary_path = tmp_path / "tsa46_full.summary.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_aoi.py",
            "--source",
            str(source),
            "--tsa-number",
            "46",
            "--out",
            str(out),
            "--summary",
            str(summary_path),
        ],
    )

    main()

    document = json.loads(summary_path.read_text(encoding="utf-8"))
    assert document["out_layer"] == "tsa46_full"
    assert out.is_file()
