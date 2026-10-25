"""FreshForge provider for the TSA 47 ws4 model-build workflow.

The provider wraps the existing ws4 build, validation, baseline-schedule, and
simulation commands. It adds no model logic; every step stays inspectable.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROVIDER_ID = "tsa47.ws4"
PROVIDER_VERSION = "0.1.0"

CommandRunner = Callable[[tuple[str, ...], Path], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class _NodeContract:
    """Declarative contract for one provider node type."""

    id: str
    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()


_NODE_CONTRACTS: tuple[_NodeContract, ...] = (
    _NodeContract(
        id="build_dataset",
        name="Build ws4 dataset",
        description="Compile a ForestModel XML recipe and fragment inventory into a ws4 matrix.",
        outputs=("dataset",),
        parameters=("instance_root", "xml", "fragments", "out"),
        artifacts=("manifest",),
    ),
    _NodeContract(
        id="validate_dataset",
        name="Validate ws4 dataset",
        description="Validate a compiled ws4 dataset against its manifest and schema invariants.",
        inputs=("dataset",),
        outputs=("validated_dataset",),
        parameters=("instance_root", "dataset"),
    ),
    _NodeContract(
        id="build_baseline_schedule",
        name="Build baseline schedule",
        description="Build a deterministic clearcut-at-target-age schedule.",
        inputs=("validated_dataset",),
        outputs=("schedule",),
        parameters=("instance_root", "dataset", "out", "target_age"),
        artifacts=("schedule", "summary"),
    ),
    _NodeContract(
        id="simulate",
        name="Simulate ws4 schedule",
        description="Replay a schedule over the compiled dataset and write a run directory.",
        inputs=("schedule",),
        outputs=("run",),
        parameters=("instance_root", "dataset", "schedule", "out", "years"),
        artifacts=("run",),
    ),
)


class Tsa47Ws4Provider:
    """FreshForge provider for the TSA 47 ws4 workflow."""

    def __init__(self, command_runner: CommandRunner | None = None) -> None:
        self._command_runner = command_runner or _default_command_runner

    def metadata(self) -> Any:
        """Return FreshForge provider metadata."""
        return _provider_metadata()

    def validate_node(self, node: Any, node_type: Any, *, location: str) -> tuple[Any, ...]:
        """Validate one node's declared inputs and parameters."""
        return _validate_contract_node(node, node_type, location=location)

    def run_node(self, node: Any, node_type: Any, *, context: Any) -> Any:
        """Execute one workflow node and return provider-owned outputs."""
        result_type, run_status = _freshforge_run_result_types()
        diagnostic, severity = _freshforge_diagnostic_types()
        try:
            command, cwd = _build_command(str(node_type.id), node)
        except ValueError as exc:
            return result_type(
                status=run_status.FAILED,
                diagnostics=(
                    diagnostic(
                        severity=severity.ERROR,
                        code="tsa47.ws4.parameters.invalid",
                        message=str(exc),
                        location=f"nodes.{node.id}.parameters",
                    ),
                ),
            )
        completed = self._command_runner(command, cwd)
        data: dict[str, Any] = {
            "command": list(command),
            "cwd": str(cwd),
            "returncode": completed.returncode,
        }
        if completed.stdout:
            data["stdout"] = completed.stdout
        if completed.stderr:
            data["stderr"] = completed.stderr
        diagnostics: tuple[Any, ...] = ()
        if completed.returncode != 0:
            diagnostics = (
                diagnostic(
                    severity=severity.ERROR,
                    code="tsa47.ws4.command.failed",
                    message=(
                        f"ws4 command for node '{node.id}' exited with "
                        f"return code {completed.returncode}."
                    ),
                    location=f"nodes.{node.id}",
                ),
            )
        return result_type(
            status=run_status.SUCCESS if completed.returncode == 0 else run_status.FAILED,
            outputs=node.outputs if isinstance(node.outputs, dict) else {},
            artifacts=_resolved_artifacts(node, cwd),
            diagnostics=diagnostics,
            data=data,
        )


def provider_factory() -> Tsa47Ws4Provider:
    """Return the provider instance for FreshForge entry-point discovery."""
    return Tsa47Ws4Provider()


def _provider_metadata() -> Any:
    node_type_metadata, provider_metadata = _freshforge_metadata_types()
    return provider_metadata(
        id=PROVIDER_ID,
        version=PROVIDER_VERSION,
        name="TSA 47 ws4 provider",
        description="Instance-owned FreshForge nodes for the TSA 47 ws4 build and baseline run.",
        node_types=tuple(
            node_type_metadata(
                id=contract.id,
                name=contract.name,
                description=contract.description,
                inputs=contract.inputs,
                outputs=contract.outputs,
                parameters=contract.parameters,
                artifacts=contract.artifacts,
            )
            for contract in _NODE_CONTRACTS
        ),
    )


def _build_command(node_id: str, node: Any) -> tuple[tuple[str, ...], Path]:
    cwd = Path(_parameter(node, "instance_root"))
    if node_id == "build_dataset":
        return (
            _python_ws4(
                "build",
                "--xml",
                _parameter(node, "xml"),
                "--fragments",
                _parameter(node, "fragments"),
                "--out",
                _parameter(node, "out"),
            ),
            cwd,
        )
    if node_id == "validate_dataset":
        return (_python_ws4("validate", "--dataset", _parameter(node, "dataset")), cwd)
    if node_id == "build_baseline_schedule":
        return (
            (
                sys.executable,
                "scripts/build_baseline_schedule.py",
                "--dataset",
                _parameter(node, "dataset"),
                "--out",
                _parameter(node, "out"),
                "--target-age",
                _parameter(node, "target_age"),
            ),
            cwd,
        )
    if node_id == "simulate":
        return (
            _python_ws4(
                "simulate",
                "--dataset",
                _parameter(node, "dataset"),
                "--schedule",
                _parameter(node, "schedule"),
                "--out",
                _parameter(node, "out"),
                "--years",
                _parameter(node, "years"),
            ),
            cwd,
        )
    raise ValueError(f"no execution hook for node type '{node_id}'")


def _python_ws4(*args: str) -> tuple[str, ...]:
    return (sys.executable, "-m", "ws4.cli", *args)


def _parameter(node: Any, key: str) -> str:
    value = node.parameters.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"node '{node.id}' requires parameter '{key}'")
    return str(value)


def _validate_contract_node(node: Any, node_type: Any, *, location: str) -> tuple[Any, ...]:
    diagnostic, severity = _freshforge_diagnostic_types()
    diagnostics: list[Any] = []
    for key in node_type.inputs:
        if key not in node.inputs:
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code="tsa47.ws4.inputs.missing",
                    message=f"missing input '{key}'",
                    location=f"{location}.inputs.{key}",
                )
            )
    for key in node_type.parameters:
        value = node.parameters.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code="tsa47.ws4.parameters.missing",
                    message=f"missing parameter '{key}'",
                    location=f"{location}.parameters.{key}",
                )
            )
    return tuple(diagnostics)


def _resolved_artifacts(node: Any, cwd: Path) -> dict[str, Any]:
    artifacts = node.artifacts if isinstance(node.artifacts, dict) else {}
    return {
        key: str(cwd / value) if isinstance(value, (str, Path)) else value
        for key, value in artifacts.items()
    }


def _default_command_runner(
    command: tuple[str, ...], cwd: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), cwd=cwd, check=False, capture_output=True, text=True)


def _freshforge_metadata_types() -> tuple[Any, Any]:
    from freshforge.providers import NodeTypeMetadata, ProviderMetadata

    return NodeTypeMetadata, ProviderMetadata


def _freshforge_diagnostic_types() -> tuple[Any, Any]:
    from freshforge.records import Diagnostic, DiagnosticSeverity

    return Diagnostic, DiagnosticSeverity


def _freshforge_run_result_types() -> tuple[Any, Any]:
    from freshforge.records import ProviderRunResult, RunStatus

    return ProviderRunResult, RunStatus
