"""
Summarize metrics for a run.
"""

from __future__ import annotations

from statistics import mean
from typing import Any, Dict, List

from .. import storage


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _summaries(rows: List[Dict[str, str]], metric_key: str | None) -> Dict[str, Dict[str, Any]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        if metric_key and row["key"] != metric_key:
            continue
        val = _to_float(row["value"])
        if val is None:
            continue
        grouped.setdefault(row["key"], []).append(val)
    summary: dict[str, dict[str, Any]] = {}
    for key, vals in grouped.items():
        summary[key] = {
            "count": len(vals),
            "min": min(vals),
            "max": max(vals),
            "mean": mean(vals),
            "last": vals[-1],
        }
    return summary


def run(run_id: str, base_dir: str | None, metric_key: str | None) -> None:
    root = storage.resolve_base(base_dir) / "runs" / run_id
    rows = storage.load_metrics(root)
    if not rows:
        print("No metrics recorded.")
        return
    summaries = _summaries(rows, metric_key)
    if not summaries:
        print("No numeric metrics to summarize.")
        return
    print(f"Metrics summary for {run_id}:")
    for key, stats in summaries.items():
        print(
            f"- {key}: count={stats['count']} "
            f"min={stats['min']:.4f} max={stats['max']:.4f} "
            f"mean={stats['mean']:.4f} last={stats['last']:.4f}"
        )

