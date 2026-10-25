#!/usr/bin/env python3
"""Summarize FAIB ground-plot validation by sample type, species, and age.

The validation observations are produced by ``validate_tipsy_ground_plots.py``.
This script keeps the reporting separate from the plot-matching lane so the
sample frame can be audited and re-summarized without rebuilding the curves.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

METRICS = ("volume", "dbh", "height", "stems")
GROUPINGS: dict[str, tuple[str, ...]] = {
    "sample": ("sample_type",),
    "species": ("species",),
    "age": ("age_class",),
    "species_age": ("species", "age_class"),
    "sample_species": ("sample_type", "species"),
    "sample_age": ("sample_type", "age_class"),
}
OUTPUT_COLUMNS = (
    "grouping",
    "sample_type",
    "species",
    "age_class",
    "metric",
    "n",
    "mean_observed",
    "mean_predicted",
    "bias",
    "mae",
    "rmse",
    "relative_bias",
)


def _metric_row(group: pd.DataFrame, metric: str) -> dict[str, Any] | None:
    """Return one metric row for a group, or None when no valid pairs remain."""
    observed = group[f"observed_{metric}"]
    predicted = group[f"predicted_{metric}"]
    valid = pd.concat([observed, predicted], axis=1).dropna()
    valid = valid[(valid.iloc[:, 0] > 0) & (valid.iloc[:, 1] > 0)]
    if valid.empty:
        return None
    errors = valid.iloc[:, 1] - valid.iloc[:, 0]
    return {
        "metric": metric,
        "n": len(valid),
        "mean_observed": round(float(valid.iloc[:, 0].mean()), 2),
        "mean_predicted": round(float(valid.iloc[:, 1].mean()), 2),
        "bias": round(float(errors.mean()), 2),
        "mae": round(float(errors.abs().mean()), 2),
        "rmse": round(float(np.sqrt(np.mean(np.square(errors)))), 2),
        "relative_bias": round(float(errors.mean() / valid.iloc[:, 0].mean()), 3),
    }


def summarize_strata(frame: pd.DataFrame) -> pd.DataFrame:
    """Return long-form validation metrics for every supported stratum.

    Parameters
    ----------
    frame : pandas.DataFrame
        Observations from ``validate_tipsy_ground_plots.py``. It must contain
        ``sample_type``, ``species``, ``age_class``, and observed/predicted
        columns for volume, DBH, height, and stems.

    Returns
    -------
    pandas.DataFrame
        One row per grouping, stratum, and metric with ``n`` and error metrics.

    Raises
    ------
    ValueError
        When the observation table is empty.
    """
    if frame.empty:
        raise ValueError("ground-plot observations are empty")
    records: list[dict[str, Any]] = []
    for grouping, keys in GROUPINGS.items():
        for values, group in frame.groupby(list(keys), observed=True, dropna=False):
            key_values: tuple[Any, ...] = values if isinstance(values, tuple) else (values,)
            base: dict[str, Any] = {
                "grouping": grouping,
                "sample_type": "",
                "species": "",
                "age_class": "",
            }
            base.update({key: str(value) for key, value in zip(keys, key_values, strict=True)})
            for metric in METRICS:
                metrics = _metric_row(group, metric)
                if metrics is not None:
                    records.append({**base, **metrics})
    return pd.DataFrame(records, columns=OUTPUT_COLUMNS)


def main() -> None:
    """Write the stratified ground-plot validation table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    frame = pd.read_csv(args.observations)
    summary = summarize_strata(frame)
    out = args.out or Path(f"config/tsr/tipsy_ground_plot_validation_stratified.tsa{args.tsa}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, index=False)
    print(f"wrote {len(summary)} metric rows to {out}")


if __name__ == "__main__":
    main()
