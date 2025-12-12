"""
Filesystem storage helpers.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from . import utils

DEFAULT_BASE = Path("trackle_experiments")


def resolve_base(base_dir: str | None) -> Path:
    return Path(base_dir) if base_dir else DEFAULT_BASE


def create_run_dir(base_dir: str | None, run_id: str, run_name: str | None) -> Path:
    base = resolve_base(base_dir)
    run_dir = base / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    if run_name:
        (run_dir / "run_name.txt").write_text(run_name, encoding="utf-8")
    return run_dir


def write_json(path: Path, data: dict[str, Any]) -> None:
    utils.atomic_write(path, json.dumps(data, indent=2, sort_keys=True))


def write_params(root: Path | None, params: dict[str, Any]) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    params_path = root / "params.json"
    existing: dict[str, Any] = {}
    if params_path.exists():
        existing = json.loads(params_path.read_text(encoding="utf-8"))
    existing.update(params)
    write_json(params_path, existing)


def append_metric(root: Path | None, key: str, value: Any, step: int | None = None) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    metrics_path = root / "metrics.csv"
    header_needed = not metrics_path.exists()
    with metrics_path.open("a", encoding="utf-8") as f:
        if header_needed:
            f.write("step,key,value,timestamp\n")
        step_val = "" if step is None else step
        f.write(f"{step_val},{key},{value},{utils.timestamp()}\n")


def store_artifact(root: Path | None, path: str, name: str | None = None) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Artifact source not found: {src}")
    artifacts_dir = root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    dest_name = name or src.name
    dest = artifacts_dir / dest_name
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def write_context(root: Path | None, context: dict[str, Any]) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    write_json(root / "context.json", context)


def write_git(root: Path | None, git_info: dict[str, Any]) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    write_json(root / "git.json", git_info)


def write_note(root: Path | None, text: str) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    utils.atomic_write(root / "notes.md", text)


def write_run_info(
    root: Path | None,
    run_name: str | None,
    created_at: str,
    finished_at: str | None,
    duration_s: float | None,
    tags: Iterable[str] | None,
) -> None:
    if root is None:
        raise ValueError("Run root is not set")
    info = {
        "run_name": run_name,
        "created_at": created_at,
        "finished_at": finished_at,
        "duration_s": duration_s,
        "tags": list(tags) if tags else [],
    }
    write_json(root / "run.json", info)


def load_run_info(root: Path) -> dict[str, Any]:
    path = root / "run.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_params(root: Path) -> dict[str, Any]:
    path = root / "params.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_metrics(root: Path) -> list[dict[str, str]]:
    path = root / "metrics.csv"
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            if header is None:
                header = line.split(",")
                continue
            parts = line.split(",")
            rows.append(dict(zip(header, parts)))
    return rows


def iter_run_dirs(base_dir: str | None) -> list[Path]:
    base = resolve_base(base_dir) / "runs"
    if not base.exists():
        return []
    return sorted([p for p in base.iterdir() if p.is_dir()])

