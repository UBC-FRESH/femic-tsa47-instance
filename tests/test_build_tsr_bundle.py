"""The TSR bundle builder replaces only treated curves."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from build_tsr_bundle import build_treated_curve_points, replace_treated_curves


def _bundle(path: Path) -> Path:
    path.mkdir()
    pd.DataFrame(
        {
            "au_id": [4601000, 4602000],
            "source_managed_local_au_id": [21000, 22000],
            "treated_curve_id": [4621000, 4622000],
        }
    ).to_csv(path / "au_table.csv", index=False)
    pd.DataFrame({"curve_id": [4601000, 4621000], "curve_type": ["untreated", "treated"]}).to_csv(
        path / "curve_table.csv", index=False
    )
    pd.DataFrame(
        {
            "curve_id": [4601000, 4601000, 4621000, 4621000],
            "x": [1, 2, 1, 2],
            "y": [1.0, 2.0, 3.0, 4.0],
        }
    ).to_csv(path / "curve_points_table.csv", index=False)
    return path


def _curves(path: Path) -> Path:
    pd.DataFrame(
        {
            "AU": [21000, 21000, 22000, 22000],
            "Age": [0, 100, 0, 100],
            "Yield": [0.0, 100.0, 0.0, 200.0],
        }
    ).to_csv(path, index=False)
    return path


def test_build_treated_curve_points_interpolates_annual_ages(tmp_path: Path) -> None:
    """Annual ages are linear interpolations of the BTC ages."""
    au_table = pd.read_csv(_bundle(tmp_path / "bundle") / "au_table.csv")
    points = build_treated_curve_points(
        au_table=au_table, curves=pd.read_csv(_curves(tmp_path / "c.csv"))
    )
    assert set(points["curve_id"]) == {4621000, 4622000}
    first = points[(points.curve_id == 4621000) & (points.x == 50)]
    assert first.iloc[0]["y"] == 50.0
    assert points["x"].min() == 1
    assert points["x"].max() == 300


def test_replace_treated_curves_keeps_untreated(tmp_path: Path) -> None:
    """The destination bundle keeps untreated points and replaces treated ones."""
    source = _bundle(tmp_path / "bundle")
    output = replace_treated_curves(
        bundle_dir=source,
        curves_path=_curves(tmp_path / "c.csv"),
        output_dir=tmp_path / "out",
    )
    points = pd.read_csv(output / "curve_points_table.csv")
    untreated = points[points.curve_id == 4601000]
    assert untreated["y"].tolist() == [1.0, 2.0]
    treated = points[points.curve_id == 4621000]
    assert len(treated) == 300
    assert treated[treated.x == 100].iloc[0]["y"] == 100.0
    assert (output / "curve_table.csv").is_file()


def test_replace_treated_curves_rejects_missing_au(tmp_path: Path) -> None:
    """A curve table that omits a managed AU is rejected."""
    source = _bundle(tmp_path / "bundle")
    curves = tmp_path / "c.csv"
    pd.DataFrame({"AU": [21000, 21000], "Age": [0, 100], "Yield": [0.0, 1.0]}).to_csv(
        curves, index=False
    )
    with pytest.raises(ValueError, match="missing managed AU"):
        replace_treated_curves(
            bundle_dir=source,
            curves_path=curves,
            output_dir=tmp_path / "out",
        )


def test_build_treated_curve_points_requires_columns() -> None:
    """Missing BTC columns produce a clear error."""
    with pytest.raises(ValueError, match="missing columns"):
        build_treated_curve_points(
            au_table=pd.DataFrame(
                {"source_managed_local_au_id": [21000], "treated_curve_id": [4621000]}
            ),
            curves=pd.DataFrame({"AU": [21000]}),
        )


def test_cli_writes_the_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI entry point writes a replacement bundle."""
    import sys

    from build_tsr_bundle import main

    source = _bundle(tmp_path / "bundle")
    curves = _curves(tmp_path / "c.csv")
    out = tmp_path / "out"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_tsr_bundle.py",
            "--bundle-dir",
            str(source),
            "--curves",
            str(curves),
            "--out",
            str(out),
        ],
    )
    main()
    assert (out / "curve_points_table.csv").is_file()
