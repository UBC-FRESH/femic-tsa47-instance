"""Tests for the safe sliver merge."""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Polygon, box

from merge_slivers import _valid, main, merge_slivers


def _skipped(summary: dict[str, object]) -> dict[str, int]:
    """Return the skipped-reason counts from a summary."""
    value = summary["skipped"]
    assert isinstance(value, dict)
    return {str(key): int(count) for key, count in value.items()}


def _write_fixture(
    path: Path,
    *,
    au: str = "A",
    ifm: str = "unmanaged",
    origin: str = "natural",
    age: float = 100.0,
    retention: float = 0.0,
    disconnected: bool = False,
    both_small: bool = False,
) -> None:
    """Write two touching blocks, or one small isolated block."""
    second = box(5, 0, 7, 1) if disconnected else box(1, 0, 3, 1)
    second_area = 0.5 if both_small else 2.0
    frame = gpd.GeoDataFrame(
        {
            "FRAGMENT_I": [1, 2],
            "BLOCK": [1, 2],
            "AREA_HA": [0.5, second_area],
            "F_AGE": [age, 105.0],
            "AU": [au, "A"],
            "IFM": [ifm, "unmanaged"],
            "ORIGIN": [origin, "natural"],
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
    assert _skipped(summary)["different_au"] == 1


def test_a_different_ifm_is_not_merged(tmp_path: Path) -> None:
    """A neighbour with a different IFM is left alone."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, ifm="managed")
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["different_ifm"] == 1


def test_a_different_origin_is_not_merged(tmp_path: Path) -> None:
    """A neighbour with a different origin is left alone."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, origin="planted")
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["different_origin"] == 1


def test_an_age_difference_is_not_merged(tmp_path: Path) -> None:
    """An age difference over the tolerance is left alone."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, age=200.0)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["age_difference"] == 1


def test_a_retention_sliver_is_not_merged(tmp_path: Path) -> None:
    """A retention-bearing fragment is never merged."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, retention=0.2)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["retention"] == 1


def test_an_isolated_sliver_is_not_merged(tmp_path: Path) -> None:
    """A small block with no touching neighbour is kept."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, disconnected=True)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["no_touching_neighbour"] == 1


def test_a_small_host_is_not_used(tmp_path: Path) -> None:
    """A small block is not merged into another small candidate block."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source, both_small=True)
    summary = merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")
    assert summary["merged_blocks"] == 0
    assert _skipped(summary)["host_is_candidate"] == 2


def test_an_invalid_geometry_is_repaired() -> None:
    """An invalid polygon is made valid before it is used."""
    invalid = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
    assert not invalid.is_valid
    assert _valid(invalid).is_valid


def test_a_missing_column_is_rejected(tmp_path: Path) -> None:
    """A fragment table without a required column is rejected."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source)
    frame = gpd.read_file(source).drop(columns=["TSA"])
    frame.to_file(source, driver="GPKG")
    with pytest.raises(ValueError, match="missing"):
        merge_slivers(fragments_path=source, out_path=tmp_path / "merged.gpkg")


def test_the_cli_writes_the_merge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The command-line entry point writes the merged layer."""
    source = tmp_path / "fragments.gpkg"
    _write_fixture(source)
    out = tmp_path / "merged.gpkg"
    monkeypatch.setattr(
        sys,
        "argv",
        ["merge_slivers.py", "--fragments", str(source), "--out", str(out)],
    )
    main()
    assert out.is_file()
