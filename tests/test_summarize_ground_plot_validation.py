"""Tests for the stratified ground-plot validation summary."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

from summarize_ground_plot_validation import _metric_row, main, summarize_strata


def _observations() -> pd.DataFrame:
    """Return a small frame with two sample types, two species, and three ages."""
    return pd.DataFrame(
        {
            "sample_type": ["CMI", "CMI", "VRI", "VRI"],
            "species": ["Hw", "Cw", "Hw", "Hw"],
            "age_class": ["31-50", "51-80", "31-50", "81-200"],
            "observed_volume": [100.0, 200.0, 300.0, 500.0],
            "predicted_volume": [80.0, 150.0, 250.0, 480.0],
            "observed_dbh": [20.0, 25.0, 30.0, 40.0],
            "predicted_dbh": [16.0, 18.0, 24.0, 36.0],
            "observed_height": [20.0, 25.0, 28.0, 32.0],
            "predicted_height": [18.0, 20.0, 25.0, 30.0],
            "observed_stems": [800.0, 700.0, 600.0, 500.0],
            "predicted_stems": [700.0, 650.0, 500.0, 480.0],
        }
    )


def test_summarize_strata_reports_every_group_and_sample_size() -> None:
    """Every grouping is emitted with its sample size and signed bias."""
    summary = summarize_strata(_observations())

    assert len(summary) == 68
    sample = summary[(summary["grouping"] == "sample") & (summary["metric"] == "volume")]
    cmi = sample[sample["sample_type"] == "CMI"].iloc[0]
    assert cmi["n"] == 2
    assert cmi["mean_observed"] == 150.0
    assert cmi["mean_predicted"] == 115.0
    assert cmi["bias"] == -35.0

    species = summary[(summary["grouping"] == "species") & (summary["metric"] == "volume")]
    hw = species[species["species"] == "Hw"].iloc[0]
    assert hw["n"] == 3
    assert hw["bias"] == -30.0

    age = summary[(summary["grouping"] == "sample_age") & (summary["metric"] == "dbh")]
    assert set(age["age_class"]) == {"31-50", "51-80", "81-200"}


def test_summarize_strata_rejects_empty_observations() -> None:
    """An empty observation table is an error, not an empty report."""
    with pytest.raises(ValueError, match="empty"):
        summarize_strata(pd.DataFrame())


def test_metric_row_skips_all_missing_pairs() -> None:
    """A stratum without a valid observed/predicted pair is omitted."""
    frame = pd.DataFrame(
        {
            "observed_volume": [None, None],
            "predicted_volume": [None, None],
        }
    )
    assert _metric_row(frame, "volume") is None


def test_main_writes_the_stratified_table(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI writes the long-form table to the requested path."""
    observations = tmp_path / "observations.csv"
    out = tmp_path / "stratified.csv"
    _observations().to_csv(observations, index=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "summarize_ground_plot_validation.py",
            "--tsa",
            "46",
            "--observations",
            str(observations),
            "--out",
            str(out),
        ],
    )

    main()

    written = pd.read_csv(out)
    assert len(written) == 68
    assert set(written["metric"]) == {"volume", "dbh", "height", "stems"}
    assert "metric rows" in capsys.readouterr().out
