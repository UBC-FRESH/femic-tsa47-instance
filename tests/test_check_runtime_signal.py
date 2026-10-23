"""Tests for the compiled runtime-signal gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

from check_runtime_signal import check_runtime_signal, main


def _write_fixture(
    tmp_path: Path,
    *,
    drop_label: str | None = None,
    add_orphan: bool = False,
    bad_curve_id: int | None = None,
) -> tuple[Path, Path]:
    """Write a minimal dataset and AU table."""
    dataset = tmp_path / "matrix"
    bundle = tmp_path / "bundle"
    dataset.mkdir()
    bundle.mkdir()
    labels = [
        "feature.Area.og1.CWH_CW_H",
        "feature.Area.og2.CWH_CW_H",
        "feature.Area.og1.CWH_HW_L",
        "feature.Area.og2.CWH_HW_L",
    ]
    if drop_label is not None:
        labels.remove(drop_label)
    features = pd.DataFrame(
        {"track_id": range(1, len(labels) + 1), "label": labels, "curve_id": [11] * len(labels)}
    )
    if bad_curve_id is not None:
        features.loc[0, "curve_id"] = bad_curve_id
    features.to_parquet(dataset / "features.parquet")
    pd.DataFrame(
        {"track_id": [1, 2], "treatment": ["CC", "CC"], "label": ["p", "p"], "curve_id": [11, 11]}
    ).to_parquet(dataset / "products.parquet")
    pd.DataFrame({"curve_id": [11, 12], "x": [0, 0], "y": [0.0, 0.0]}).to_parquet(
        dataset / "curves.parquet"
    )
    track_ids = [1, 2, 3] + ([5] if add_orphan else [])
    names = [f"AU({value})+IFM(managed)+ORIGIN(natural)" for value in track_ids]
    pd.DataFrame({"track_id": track_ids, "name": names}).to_parquet(dataset / "tracks.parquet")
    pd.DataFrame(
        {
            "fragment_id": track_ids,
            "block_id": track_ids,
            "area_ha": [10.0, 10.0, 10.0] + ([10.0] if add_orphan else []),
            "track_id": track_ids,
        }
    ).to_parquet(dataset / "fragments.parquet")
    pd.DataFrame(
        {
            "stratum_code": ["CWH_CW", "CWH_HW"],
            "si_level": ["H", "L"],
        }
    ).to_csv(bundle / "au_table.csv", index=False)
    return dataset, bundle


def test_runtime_signal_passes_for_complete_pairs(tmp_path: Path) -> None:
    """Every AU/species label and track signal resolves."""
    dataset, bundle = _write_fixture(tmp_path)
    summary = check_runtime_signal(dataset=dataset, bundle=bundle)
    assert summary["status"] == "ok"
    assert summary["pair_count"] == 2


def test_runtime_signal_reports_a_missing_label(tmp_path: Path) -> None:
    """A missing og1 label is a compiled-signal defect."""
    dataset, bundle = _write_fixture(tmp_path, drop_label="feature.Area.og1.CWH_CW_H")
    summary = check_runtime_signal(dataset=dataset, bundle=bundle)
    assert summary["status"] == "error"
    missing = summary["missing_labels"]
    assert isinstance(missing, list)
    assert "feature.Area.og1.CWH_CW_H" in missing


def test_runtime_signal_reports_a_missing_curve(tmp_path: Path) -> None:
    """A feature curve id that is absent from curves.parquet is a defect."""
    dataset, bundle = _write_fixture(tmp_path, bad_curve_id=99)
    summary = check_runtime_signal(dataset=dataset, bundle=bundle)
    assert summary["status"] == "error"
    curves = summary["missing_curves"]
    assert isinstance(curves, list)
    assert 99 in curves


def test_runtime_signal_reports_an_orphan_track(tmp_path: Path) -> None:
    """A track with area but no feature or product label is a defect."""
    dataset, bundle = _write_fixture(tmp_path, add_orphan=True)
    summary = check_runtime_signal(dataset=dataset, bundle=bundle)
    assert summary["status"] == "error"
    orphans = summary["orphan_tracks"]
    assert isinstance(orphans, list)
    first = orphans[0]
    assert isinstance(first, dict)
    assert first["track_id"] == 5


def test_runtime_signal_reports_zero_initial_area(tmp_path: Path) -> None:
    """A zero initial area for an AU/species pair is a defect when a run is given."""
    dataset, bundle = _write_fixture(tmp_path)
    run = tmp_path / "run"
    run.mkdir()
    pd.DataFrame(
        {
            "offset": [-1, -1],
            "account": ["feature.Area.og1.CWH_CW_H", "feature.Area.og1.CWH_HW_L"],
            "value": [0.0, 10.0],
        }
    ).to_csv(run / "account_values.csv", index=False)
    summary = check_runtime_signal(dataset=dataset, bundle=bundle, run=run)
    assert summary["status"] == "error"
    zero_area = summary["zero_area"]
    assert isinstance(zero_area, list)
    assert "feature.Area.og1.CWH_CW_H" in zero_area


def test_runtime_signal_cli_exits_non_zero_on_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI returns a non-zero status when the gate fails."""
    dataset, bundle = _write_fixture(tmp_path, drop_label="feature.Area.og1.CWH_CW_H")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_runtime_signal.py",
            "--dataset",
            str(dataset),
            "--bundle",
            str(bundle),
        ],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
