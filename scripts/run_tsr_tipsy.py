#!/usr/bin/env python3
"""Run BatchTIPSY and write FEMIC long-format managed curves.

This wraps ``femic.pipeline.tipsy.run_btc_cli`` with the Linux/Wine lane used
by the North Island instance. The BTC output is transposed; the parsed long
table is what ``build_tsr_bundle.py`` expects.
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol, cast

import pandas as pd


class _BTCRunResult(Protocol):
    """The subset of FEMIC's BTC result this module reads."""

    exit_code: int
    stderr_log_path: Path


def _run_btc_cli(**kwargs: object) -> _BTCRunResult:
    """Import and call FEMIC's BTC runner lazily.

    The import is local so this module can be imported in a checkout that does
    not have the femic package installed, such as the instance's CI job.
    """
    from femic.pipeline.tipsy import run_btc_cli

    return cast(_BTCRunResult, run_btc_cli(**kwargs))


def _parse_curves(output_csv: Path) -> pd.DataFrame:
    """Parse BTC output lazily for the same reason."""
    from femic.pipeline.tipsy import parse_btc_tsr_transposed_output

    return cast(
        pd.DataFrame,
        parse_btc_tsr_transposed_output(output_csv=output_csv, pd_module=pd),
    )


def btc_error_rows(error_csv: Path) -> pd.DataFrame:
    """Return data rows from a BatchTIPSY error CSV, or an empty frame.

    Parameters
    ----------
    error_csv : Path
        The error CSV written by BatchTIPSY.

    Returns
    -------
    pandas.DataFrame
        The error rows, or a header-only frame when BTC reported no errors.
    """
    if not error_csv.is_file():
        raise FileNotFoundError(f"BTC error CSV not found: {error_csv}")
    return pd.read_csv(error_csv)


def run_and_parse(
    *,
    input_csv: Path,
    curves_csv: Path,
    output_csv: Path,
    error_csv: Path,
    btc_exe: Path,
    scratch_dir: Path,
    log_dir: Path,
    run_id: str,
    env: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Run BTC, reject any error rows, and write parsed long curves.

    Parameters
    ----------
    input_csv : Path
        BTC ``MSYT.csv``-style input.
    curves_csv : Path
        Destination for the parsed ``AU,Age,Yield`` table.
    output_csv : Path
        BTC transposed output path.
    error_csv : Path
        BTC error path.
    btc_exe : Path
        ``TIPSYbtc.exe`` or the Wine wrapper.
    scratch_dir : Path
        Writable BTC scratch root.
    log_dir : Path
        Manifest and stdout/stderr directory.
    run_id : str
        Run identifier used in log names.
    env : Mapping[str, str] or None
        Extra environment, such as the Wine prefix and display.

    Returns
    -------
    pandas.DataFrame
        Parsed long-format managed curves.
    """
    result = _run_btc_cli(
        input_csv=input_csv,
        mode="TSR",
        output_csv=output_csv,
        error_csv=error_csv,
        executable_path=btc_exe,
        report_preset_name="tsr-unattended-default",
        copy_install=True,
        scratch_root=scratch_dir,
        log_dir=log_dir,
        run_id=run_id,
        env=dict(env or {}),
    )
    if result.exit_code != 0:
        raise RuntimeError(f"BTC exited with {result.exit_code}; see {result.stderr_log_path}")
    errors = btc_error_rows(error_csv)
    if not errors.empty:
        sample = errors.head(5).to_dict(orient="records")
        raise RuntimeError(f"BTC reported {len(errors)} error rows: {sample}")
    curves = _parse_curves(output_csv)
    curves_csv.parent.mkdir(parents=True, exist_ok=True)
    curves.to_csv(curves_csv, index=False)
    return curves


def main() -> None:
    """Run BTC and write long-format curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--curves", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--error", type=Path)
    parser.add_argument(
        "--btc-exe", type=Path, default=Path("tipsy_io/btc_install/tipsybtc-wine.sh")
    )
    parser.add_argument("--scratch-dir", type=Path)
    parser.add_argument("--log-dir", type=Path, default=Path("tipsy_io/logs"))
    parser.add_argument("--wineprefix", default=os.environ.get("FEMIC_BTC_WINEPREFIX"))
    parser.add_argument("--display", default=os.environ.get("FEMIC_BTC_DISPLAY", ":99"))
    parser.add_argument("--run-id")
    args = parser.parse_args()

    input_csv = args.input or Path(f"tipsy_io/runs/03_input-tsa{args.tsa}_tsr.csv")
    curves_csv = args.curves or Path(f"tipsy_io/runs/curves_tsa{args.tsa}_tsr.csv")
    output_csv = args.output or Path(f"tipsy_io/runs/04_output-tsa{args.tsa}_tsr.csv")
    error_csv = args.error or Path(f"tipsy_io/runs/04_error-tsa{args.tsa}_tsr.csv")
    scratch_dir = args.scratch_dir or Path(f"tipsy_io/scratch/tsa{args.tsa}_tsr")
    run_id = args.run_id or f"tsa{args.tsa}_tipsy_tsr"
    env: dict[str, str] = {"WINEDEBUG": "-all"}
    if args.wineprefix:
        env["FEMIC_BTC_WINEPREFIX"] = args.wineprefix
    if args.display:
        env["FEMIC_BTC_DISPLAY"] = args.display
    curves = run_and_parse(
        input_csv=input_csv,
        curves_csv=curves_csv,
        output_csv=output_csv,
        error_csv=error_csv,
        btc_exe=args.btc_exe,
        scratch_dir=scratch_dir,
        log_dir=args.log_dir,
        run_id=run_id,
        env=env,
    )
    print(f"wrote {len(curves)} curve rows for {curves['AU'].nunique()} AUs to {curves_csv}")


if __name__ == "__main__":
    main()
