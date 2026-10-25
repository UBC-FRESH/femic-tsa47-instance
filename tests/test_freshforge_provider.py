"""Tests for the TSA 47 FreshForge provider."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

import pytest

freshforge = pytest.importorskip("freshforge")

from tsa47_workflow import PROVIDER_ID, provider_factory  # noqa: E402


def _runner(
    commands: list[tuple[tuple[str, ...], Path]],
) -> Callable[[tuple[str, ...], Path], subprocess.CompletedProcess[str]]:
    def run(command: tuple[str, ...], cwd: Path) -> subprocess.CompletedProcess[str]:
        commands.append((command, cwd))
        return subprocess.CompletedProcess(args=list(command), returncode=0, stdout="ok", stderr="")

    return run


def test_pyproject_exposes_the_provider_entry_point() -> None:
    """The package installs the tsa47.ws4 provider for FreshForge discovery."""
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["entry-points"]["freshforge.providers"]["tsa47_ws4"] == (
        "tsa47_workflow:provider_factory"
    )


def test_provider_metadata_and_nodes() -> None:
    """The provider advertises the four workflow nodes."""
    metadata = provider_factory().metadata()
    assert metadata.id == PROVIDER_ID
    assert {node.id for node in metadata.node_types} == {
        "build_dataset",
        "validate_dataset",
        "build_baseline_schedule",
        "simulate",
    }


def test_build_dataset_command() -> None:
    """The build command wraps ws4 build."""
    from freshforge.execution import RunContext
    from freshforge.records import RunStatus, WorkflowNode

    commands: list[tuple[tuple[str, ...], Path]] = []
    provider = provider_factory()
    provider._command_runner = _runner(commands)
    metadata = provider.metadata()
    node_type = next(item for item in metadata.node_types if item.id == "build_dataset")
    node = WorkflowNode(
        id="build",
        provider="tsa47.ws4.build_dataset",
        parameters={
            "instance_root": ".",
            "xml": "output/model.xml",
            "fragments": "output/fragments.shp",
            "out": "runtime/matrix",
        },
    )
    result = provider.run_node(
        node, node_type, context=RunContext(workflow_id="wf", workdir=Path("."))
    )
    assert result.status is RunStatus.SUCCESS
    assert commands[0][0] == (
        sys.executable,
        "-m",
        "ws4.cli",
        "build",
        "--xml",
        "output/model.xml",
        "--fragments",
        "output/fragments.shp",
        "--out",
        "runtime/matrix",
    )


@pytest.mark.parametrize(
    ("node_id", "parameters", "expected"),
    [
        (
            "validate_dataset",
            {"instance_root": ".", "dataset": "runtime/matrix"},
            (sys.executable, "-m", "ws4.cli", "validate", "--dataset", "runtime/matrix"),
        ),
        (
            "build_baseline_schedule",
            {
                "instance_root": ".",
                "dataset": "runtime/matrix",
                "out": "runtime/baseline.csv",
                "target_age": "60",
            },
            (
                sys.executable,
                "scripts/build_baseline_schedule.py",
                "--dataset",
                "runtime/matrix",
                "--out",
                "runtime/baseline.csv",
                "--target-age",
                "60",
            ),
        ),
        (
            "simulate",
            {
                "instance_root": ".",
                "dataset": "runtime/matrix",
                "schedule": "runtime/baseline.csv",
                "out": "runtime/run",
                "years": "100",
            },
            (
                sys.executable,
                "-m",
                "ws4.cli",
                "simulate",
                "--dataset",
                "runtime/matrix",
                "--schedule",
                "runtime/baseline.csv",
                "--out",
                "runtime/run",
                "--years",
                "100",
            ),
        ),
    ],
)
def test_other_node_commands(
    node_id: str,
    parameters: dict[str, str],
    expected: tuple[str, ...],
) -> None:
    """Each workflow node builds the expected command."""
    from freshforge.execution import RunContext
    from freshforge.records import RunStatus, WorkflowNode

    commands: list[tuple[tuple[str, ...], Path]] = []
    provider = provider_factory()
    provider._command_runner = _runner(commands)
    metadata = provider.metadata()
    node_type = next(item for item in metadata.node_types if item.id == node_id)
    node = WorkflowNode(id=node_id, provider=f"tsa47.ws4.{node_id}", parameters=parameters)
    result = provider.run_node(
        node, node_type, context=RunContext(workflow_id="wf", workdir=Path("."))
    )
    assert result.status is RunStatus.SUCCESS
    assert commands[0][0] == expected
