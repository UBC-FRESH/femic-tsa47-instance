#!/usr/bin/env python3
"""Run the bounded instance FreshForge graph with local providers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _diagnostic(item: Any) -> dict[str, Any]:
    return {
        "code": str(item.code),
        "message": str(item.message),
        "location": str(item.location),
    }


def _node(item: Any) -> dict[str, Any]:
    return {
        "id": item.id,
        "status": str(item.status),
        "command": item.data.get("command"),
        "artifacts": dict(item.artifacts),
        "diagnostics": [_diagnostic(d) for d in item.diagnostics],
    }


def main(argv: list[str] | None = None) -> int:
    """Run the smoke graph or validate it with --dry-run.

    Parameters
    ----------
    argv : list of str or None, optional
        Arguments to parse. None reads sys.argv.

    Returns
    -------
    int
        0 on success, 1 on a failed node or validation.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workflow",
        type=Path,
        default=ROOT / "workflows" / "freshforge" / "tsa47_ws4_smoke.yaml",
    )
    parser.add_argument("--workdir", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    from femic.freshforge import provider_factory as femic_provider
    from freshforge.execution import run_workflow
    from freshforge.loading import load_workflow
    from freshforge.providers import ProviderRegistry
    from freshforge.validation import validate_workflow_with_providers

    from tsa47_workflow import provider_factory

    spec, load_diagnostics = load_workflow(args.workflow)
    diagnostics = [_diagnostic(d) for d in load_diagnostics]
    if spec is None:
        print(json.dumps({"status": "failed", "diagnostics": diagnostics}, indent=2))
        return 1
    registry = ProviderRegistry()
    registry.register(femic_provider())
    registry.register(provider_factory())
    if args.dry_run:
        validation = validate_workflow_with_providers(spec, registry=registry)
        diagnostics.extend(_diagnostic(d) for d in validation)
        status = "validated" if not diagnostics else "failed"
        evidence: dict[str, Any] = {
            "workflow": spec.id,
            "status": status,
            "diagnostics": diagnostics,
        }
    else:
        result = run_workflow(spec, registry=registry, workdir=args.workdir)
        diagnostics.extend(_diagnostic(d) for d in result.diagnostics)
        evidence = {
            "workflow": spec.id,
            "status": str(result.status),
            "diagnostics": diagnostics,
            "nodes": [_node(node) for node in result.nodes],
        }
    out = args.out or (ROOT / "runtime" / "smoke" / "evidence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["status"] in {"validated", "success", "RunStatus.SUCCESS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
