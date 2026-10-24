"""Tests for the safe sliver merge."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from merge_slivers import merge_slivers


def _write_fixture(
    path: Path,
    *,
    au: str = "A",
    retention: float = 0.0,
    disconnected: bool = False,
) -> None:
    """Write two touching blocks, or one small isolated block."""
    second = box(5, 0, 7, 1) if disconnected else box(1, 0, 3, 1)
    frame = gpd.GeoDataFrame(
        {
            "FRAGMENT_I": [1, 2],
            "BLOCK": [1, 2],
            "AREA_HA": [0.5, 2.0],
            "F_AGE": [100.0, 105.0],
            "AU": [au, "A"],
            "IFM": ["unmanaged", "unmanaged"],
            "ORIGIN": ["natural", "natural"],
            "SILV_STATE": ["baseline", "baseline"],
            "RETENTION": [retention, 0.0],
            "TSA": ["47", "47"],
        },
        geometry=[box(0, 0, 1, 0.5), second],
        crs="EPSG:3005",
    )
    frame.to_file(path, driver="GPKG")


def test_a_safe_sliver_merges_and_preserves_area(tmp_path: Path) -> None:
    """A same-AU, same-IFM, age-safe sliver is absorbed by its neighbour."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source)
    out = tmp_path / "merged.gpkg"
    summary = merge_slivers(fragments_path=source, out_path=out, cutoff_ha=1.0)
    result = gpd.read_file(out)
    assert len(result) == 1
    assert int(result.iloc[0]["BLOCK"]) == 2
    assert result.iloc[0]["AREA_HA"] == pytest.approx(2.5)
    assert result.iloc[0]["F_AGE"] == pytest.approx(104.0)
    assert summary["merged_blocks"] == 1
    assert summary["area_before_ha"] == summary["area_after_ha"]


def test_a_different_au_is_not_merged(tmp_path: Path) -> None:
    """A neighbour with a different AU is left alone."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, au="B")
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert summary["skipped"]["different_au"] == 1


def test_a_retention_sliver_is_not_merged(tmp_path: Path) -> None:
    """A retention-bearing fragment is never merged."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, retention=0.2)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert summary["skipped"]["retention"] == 1


def test_an_isolated_sliver_is_not_merged(tmp_path: Path) -> None:
    """A small block with no touching neighbour is kept."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, disconnected=True)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert summary["skipped"]["no_touching_neighbour"] == 1
