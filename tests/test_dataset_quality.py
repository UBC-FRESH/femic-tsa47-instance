"""Tests for the tracked provenance sidecar and build hook."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apply_dataset_quality import apply_quality


def _dataset(tmp_path: Path) -> Path:
    dataset = tmp_path / "matrix"
    dataset.mkdir()
    (dataset / "manifest.json").write_text(
        json.dumps({"schema_version": "0.1", "tables": {}, "sources": [], "metadata": {}}),
        encoding="utf-8",
    )
    return dataset


def test_apply_quality_copies_and_reports_ok(tmp_path: Path) -> None:
    """The tracked sidecar makes the dataset provenance report ok."""
    dataset = _dataset(tmp_path)
    sidecar = tmp_path / "dataset_quality.yaml"
    sidecar.write_text(
        "schema_version: 1\ninventory:\n  vintage: '2025'\nlimitations:\n  - test\n",
        encoding="utf-8",
    )
    report = apply_quality(dataset, sidecar)
    assert (dataset / "data_quality.yaml").is_file()
    assert report["summary"]["provenance_supplied"] is True
    assert report["summary"]["status"] == "ok"


def test_apply_quality_rejects_a_missing_sidecar(tmp_path: Path) -> None:
    """A missing sidecar fails before writing anything."""
    dataset = _dataset(tmp_path)
    with pytest.raises(FileNotFoundError, match="sidecar"):
        apply_quality(dataset, tmp_path / "missing.yaml")


def test_apply_quality_rejects_a_missing_dataset(tmp_path: Path) -> None:
    """A missing compiled dataset is a named failure."""
    sidecar = tmp_path / "dataset_quality.yaml"
    sidecar.write_text("schema_version: 1\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="dataset"):
        apply_quality(tmp_path / "missing", sidecar)


def test_main_returns_zero_on_a_pass_and_one_on_a_failure(tmp_path: Path) -> None:
    """The CLI check mirrors the report status."""
    from apply_dataset_quality import main

    dataset = _dataset(tmp_path)
    sidecar = tmp_path / "dataset_quality.yaml"
    sidecar.write_text("schema_version: 1\ninventory:\n  vintage: '2025'\n", encoding="utf-8")
    assert main(["--dataset", str(dataset), "--sidecar", str(sidecar), "--check"]) == 0
    broken = tmp_path / "broken.yaml"
    broken.write_text("- invalid\n", encoding="utf-8")
    assert main(["--dataset", str(dataset), "--sidecar", str(broken), "--check"]) == 1
