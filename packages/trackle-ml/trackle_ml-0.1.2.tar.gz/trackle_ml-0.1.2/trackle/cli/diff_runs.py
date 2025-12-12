"""
Diff two runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import storage


def _load(run_id: str, base_dir: str | None) -> dict[str, Any]:
    root = storage.resolve_base(base_dir) / "runs" / run_id
    if not root.exists():
        raise SystemExit(f"Run not found: {run_id}")
    return {
        "info": storage.load_run_info(root),
        "params": storage.load_params(root),
        "metrics": storage.load_metrics(root),
    }


def _dict_diff(a: dict[str, Any], b: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    added = [k for k in b.keys() if k not in a]
    removed = [k for k in a.keys() if k not in b]
    changed = [k for k in a.keys() if k in b and a[k] != b[k]]
    return added, removed, changed


def run(run_a: str, run_b: str, base_dir: str | None) -> None:
    a = _load(run_a, base_dir)
    b = _load(run_b, base_dir)
    added, removed, changed = _dict_diff(a["params"], b["params"])

    print(f"Params added in {run_b}:", added or "none")
    print(f"Params removed from {run_b}:", removed or "none")
    print(f"Params changed:", changed or "none")

    metrics_a = {row["key"] for row in a["metrics"]}
    metrics_b = {row["key"] for row in b["metrics"]}
    print(f"Metrics only in {run_a}:", sorted(metrics_a - metrics_b) or "none")
    print(f"Metrics only in {run_b}:", sorted(metrics_b - metrics_a) or "none")

