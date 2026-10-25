"""The TSR runner rejects BTC errors and writes long-form curves."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import run_tsr_tipsy


def _btc_output(path: Path) -> Path:
    pd.DataFrame(
        {
            "feature_id": [21000],
            "MVcon_0": [0.0],
            "MVcon_10": [10.0],
            "MVdec_0": [0.0],
            "MVdec_10": [0.0],
            "HTcon_0": [0.0],
            "HTcon_10": [2.0],
            "HTdec_0": [0.0],
            "HTdec_10": [0.0],
            "gVol_0": [0.0],
            "gVol_10": [12.0],
            "CC_0": [0.0],
            "CC_10": [5.0],
        }
    ).to_csv(path, index=False)
    return path


def test_btc_error_rows_reads_header_only(tmp_path: Path) -> None:
    """A header-only error file means no errors."""
    path = tmp_path / "error.csv"
    path.write_text("feature_id,RowNum,Type\n", encoding="utf-8")
    assert run_tsr_tipsy.btc_error_rows(path).empty


def test_btc_error_rows_rejects_missing_file(tmp_path: Path) -> None:
    """A missing error file is a hard failure."""
    with pytest.raises(FileNotFoundError):
        run_tsr_tipsy.btc_error_rows(tmp_path / "missing.csv")


def test_run_and_parse_writes_curves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A clean BTC run is parsed into the long curve table."""
    output = _btc_output(tmp_path / "out.csv")
    error = tmp_path / "error.csv"
    error.write_text("feature_id,RowNum,Type\n", encoding="utf-8")
    curves = tmp_path / "curves.csv"

    def fake_run(**_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(exit_code=0, stderr_log_path=tmp_path / "stderr.log")

    monkeypatch.setattr(run_tsr_tipsy, "_run_btc_cli", fake_run)
    monkeypatch.setattr(
        run_tsr_tipsy,
        "_parse_curves",
        lambda _path: pd.DataFrame({"AU": [21000, 21000], "Age": [0, 10], "Yield": [0.0, 10.0]}),
    )
    result = run_tsr_tipsy.run_and_parse(
        input_csv=tmp_path / "input.csv",
        curves_csv=curves,
        output_csv=output,
        error_csv=error,
        btc_exe=tmp_path / "btc",
        scratch_dir=tmp_path / "scratch",
        log_dir=tmp_path / "logs",
        run_id="test",
    )
    assert result["AU"].tolist() == [21000, 21000]
    assert result["Age"].tolist() == [0, 10]
    assert curves.is_file()


def test_run_and_parse_rejects_error_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Any BTC error row aborts the lane."""
    output = _btc_output(tmp_path / "out.csv")
    error = tmp_path / "error.csv"
    error.write_text("feature_id,RowNum,Type\n21000,2,Error\n", encoding="utf-8")
    monkeypatch.setattr(
        run_tsr_tipsy,
        "_run_btc_cli",
        lambda **_kwargs: SimpleNamespace(exit_code=0, stderr_log_path=tmp_path / "s.log"),
    )
    with pytest.raises(RuntimeError, match="error rows"):
        run_tsr_tipsy.run_and_parse(
            input_csv=tmp_path / "input.csv",
            curves_csv=tmp_path / "curves.csv",
            output_csv=output,
            error_csv=error,
            btc_exe=tmp_path / "btc",
            scratch_dir=tmp_path / "scratch",
            log_dir=tmp_path / "logs",
            run_id="test",
        )


def test_run_and_parse_rejects_nonzero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-zero BTC exit aborts the lane."""
    monkeypatch.setattr(
        run_tsr_tipsy,
        "_run_btc_cli",
        lambda **_kwargs: SimpleNamespace(exit_code=1, stderr_log_path=tmp_path / "s.log"),
    )
    with pytest.raises(RuntimeError, match="exited with 1"):
        run_tsr_tipsy.run_and_parse(
            input_csv=tmp_path / "input.csv",
            curves_csv=tmp_path / "curves.csv",
            output_csv=tmp_path / "out.csv",
            error_csv=tmp_path / "error.csv",
            btc_exe=tmp_path / "btc",
            scratch_dir=tmp_path / "scratch",
            log_dir=tmp_path / "logs",
            run_id="test",
        )


def test_cli_runs_the_lane(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI entry point passes the TSA defaults to the runner."""
    import sys

    monkeypatch.setattr(
        run_tsr_tipsy,
        "run_and_parse",
        lambda **kwargs: pd.DataFrame({"AU": [21000], "Age": [10], "Yield": [1.0]}),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_tsr_tipsy.py", "--tsa", "46", "--wineprefix", str(tmp_path / "wine")],
    )
    run_tsr_tipsy.main()


def test_run_and_parse_passes_indicator_banks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Indicator banks are forwarded so DBH/stem columns can be requested."""
    captured: dict[str, object] = {}

    def fake_run(**kwargs: object) -> SimpleNamespace:
        captured.update(kwargs)
        return SimpleNamespace(exit_code=0, stderr_log_path=tmp_path / "stderr.log")

    error = tmp_path / "error.csv"
    error.write_text("feature_id,RowNum,Type\n", encoding="utf-8")
    monkeypatch.setattr(run_tsr_tipsy, "_run_btc_cli", fake_run)
    monkeypatch.setattr(
        run_tsr_tipsy,
        "_parse_curves",
        lambda _path: pd.DataFrame({"AU": [21000], "Age": [10], "Yield": [1.0]}),
    )
    run_tsr_tipsy.run_and_parse(
        input_csv=tmp_path / "input.csv",
        curves_csv=tmp_path / "curves.csv",
        output_csv=tmp_path / "out.csv",
        error_csv=error,
        btc_exe=tmp_path / "btc",
        scratch_dir=tmp_path / "scratch",
        log_dir=tmp_path / "logs",
        run_id="test",
        indicator_banks=["stand-structure-basic"],
    )
    assert captured["indicator_bank_names"] == ["stand-structure-basic"]
