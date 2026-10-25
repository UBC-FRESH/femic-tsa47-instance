#!/usr/bin/env python3
"""Copy the tracked provenance sidecar beside a compiled matrix and check it."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any, cast

from ws4.opt.repro import dataset_quality  # type: ignore[import-not-found]  # installed in the instance runtime, not the mypy path


def apply_quality(dataset: Path, sidecar: Path) -> dict[str, Any]:
    """Copy the sidecar into the dataset and return the quality report.

    Parameters
    ----------
    dataset : Path
        The compiled matrix directory.
    sidecar : Path
        The tracked ``config/dataset_quality.yaml``.

    Returns
    -------
    dict of str to Any
        The P26 quality report.

    Raises
    ------
    FileNotFoundError
        When the sidecar or dataset directory is missing.
    """
    if not sidecar.is_file():
        raise FileNotFoundError(f"missing provenance sidecar: {sidecar}")
    if not dataset.is_dir():
        raise FileNotFoundError(f"missing compiled dataset: {dataset}")
    destination = dataset / "data_quality.yaml"
    if sidecar.resolve() != destination.resolve():
        shutil.copyfile(sidecar, destination)
    return cast(dict[str, Any], dataset_quality(dataset))


def main(argv: list[str] | None = None) -> int:
    """Run the apply/check from the command line.

    Parameters
    ----------
    argv : list of str or None, optional
        Arguments to parse. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` on a passing check, ``1`` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = apply_quality(args.dataset, args.sidecar)
    summary = report["summary"]
    assert isinstance(summary, dict)
    print(f"provenance: {summary.get('status')} ({args.dataset / 'data_quality.yaml'})")
    if args.check and summary.get("status") != "ok":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
