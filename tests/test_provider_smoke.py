"""Tests for the bounded provider smoke workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("freshforge")
pytest.importorskip("femic.freshforge")

from femic.freshforge import provider_factory as femic_provider

if "ws4_quality" not in {node.id for node in femic_provider().metadata().node_types}:
    pytest.skip("installed femic lacks the ws4_quality provider", allow_module_level=True)

from freshforge.loading import load_workflow
from freshforge.providers import ProviderRegistry
from freshforge.validation import validate_workflow_with_providers

from run_provider_smoke import main
from tsa47_workflow import provider_factory


def test_smoke_workflow_resolves_with_local_providers() -> None:
    """The smoke graph resolves every node."""
    spec, diagnostics = load_workflow(Path("workflows/freshforge/tsa47_ws4_smoke.yaml"))
    assert spec is not None
    assert diagnostics == []
    registry = ProviderRegistry()
    registry.register(femic_provider())
    registry.register(provider_factory())
    assert validate_workflow_with_providers(spec, registry=registry) == []


def test_dry_run_writes_evidence(tmp_path: Path) -> None:
    """The runner writes a validated evidence file."""
    out = tmp_path / "evidence.json"
    code = main(
        [
            "--workflow",
            "workflows/freshforge/tsa47_ws4_smoke.yaml",
            "--dry-run",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert '"status": "validated"' in out.read_text(encoding="utf-8")
