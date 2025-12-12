"""
List runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import storage


def _format_duration(duration_s: float | None) -> str:
    if duration_s is None:
        return "-"
    return f"{duration_s:.2f}s"


def _summarize_run(root: Path) -> dict[str, Any]:
    info = storage.load_run_info(root)
    params = storage.load_params(root)
    metrics = storage.load_metrics(root)
    return {
        "id": root.name,
        "name": info.get("run_name") or "",
        "created_at": info.get("created_at") or "",
        "finished": bool(info.get("finished_at")),
        "duration_s": info.get("duration_s"),
        "param_count": len(params),
        "metric_rows": len(metrics),
    }


def run(base_dir: str | None, limit: int) -> None:
    runs = storage.iter_run_dirs(base_dir)
    if not runs:
        print("No runs found.")
        return
    rows = [_summarize_run(r) for r in runs][-limit:]
    print(f"{'id':<24}  {'name':<16}  {'created':<20}  {'fin':<3}  {'dur':<8}  p  m")
    for row in rows:
        print(
            f"{row['id']:<24}  "
            f"{row['name']:<16}  "
            f"{row['created_at']:<20}  "
            f"{'y' if row['finished'] else 'n':<3}  "
            f"{_format_duration(row['duration_s']):<8}  "
            f"{row['param_count']:<2} "
            f"{row['metric_rows']:<2}"
        )

