"""Tests for the harvest-coverage gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

from check_harvest_coverage import check_harvest_coverage, load_allowlist, main


def _write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Write a dataset with one managed and one unmanaged AU."""
    dataset = tmp_path / "matrix"
    dataset.mkdir()
    pd.DataFrame(
        {
            "fragment_id": [1, 2, 3],
            "block_id": [10, 20, 30],
            "area_ha": [120.0, 30.0, 500.0],
            "track_id": [1, 2, 3],
        }
    ).to_parquet(dataset / "fragments.parquet")
    pd.DataFrame(
        {
            "track_id": [1, 2, 3],
            "name": [
                "AU(1)+IFM(managed)+ORIGIN(natural)+SILV_STATE(baseline)+RETENTION(0)+treatment()",
                "AU(2)+IFM(managed)+ORIGIN(natural)+SILV_STATE(baseline)+RETENTION(0)+treatment()",
                "AU(3)+IFM(unmanaged)+ORIGIN(natural)+SILV_STATE(baseline)+RETENTION(0)+treatment()",
            ],
        }
    ).to_parquet(dataset / "tracks.parquet")
    schedule = tmp_path / "schedule.csv"
    pd.DataFrame({"block_id": [10], "treatment": ["CC"], "offset": [0]}).to_csv(
        schedule, index=False
    )
    return dataset, schedule


def test_coverage_passes_when_every_au_is_harvested_or_small(tmp_path: Path) -> None:
    """AU 1 is harvested and AU 2 is below the threshold."""
    dataset, schedule = _write_fixture(tmp_path)
    summary = check_harvest_coverage(dataset=dataset, schedule=schedule)
    assert summary["status"] == "ok"
    assert summary["uncovered"] == []


def test_coverage_reports_an_uncovered_au(tmp_path: Path) -> None:
    """A managed AU above the threshold with no harvest fails."""
    dataset, schedule = _write_fixture(tmp_path)
    summary = check_harvest_coverage(dataset=dataset, schedule=schedule, min_managed_ha=10.0)
    assert summary["status"] == "error"
    uncovered = summary["uncovered"]
    assert isinstance(uncovered, list)
    first = uncovered[0]
    assert isinstance(first, dict)
    assert first["au"] == "2"


def test_coverage_accepts_an_allowlisted_au(tmp_path: Path) -> None:
    """An allowlist entry with a reason clears the gap."""
    dataset, schedule = _write_fixture(tmp_path)
    allowlist = tmp_path / "allowlist.json"
    allowlist.write_text(
        json.dumps({"aus": [{"au": "2", "reason": "not selected by the benchmark"}]}),
        encoding="utf-8",
    )
    summary = check_harvest_coverage(
        dataset=dataset, schedule=schedule, min_managed_ha=10.0, allowlist=allowlist
    )
    assert summary["status"] == "ok"
    uncovered = summary["uncovered"]
    assert isinstance(uncovered, list)
    first = uncovered[0]
    assert isinstance(first, dict)
    assert first["allowed"] is True


def test_load_allowlist_rejects_a_malformed_document(tmp_path: Path) -> None:
    """An allowlist without an 'aus' list is rejected."""
    allowlist = tmp_path / "allowlist.json"
    allowlist.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="aus"):
        load_allowlist(allowlist)


def test_coverage_cli_exits_non_zero_on_a_gap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI returns a non-zero status for an unexpected gap."""
    dataset, schedule = _write_fixture(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_harvest_coverage.py",
            "--dataset",
            str(dataset),
            "--schedule",
            str(schedule),
            "--min-managed-ha",
            "10",
        ],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
