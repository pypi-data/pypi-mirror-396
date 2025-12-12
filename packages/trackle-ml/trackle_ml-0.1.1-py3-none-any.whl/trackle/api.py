"""
Top-level Python API for Trackle.
Placeholder implementations will be filled in later.
"""

from __future__ import annotations

from .run import Run

_active_run: Run | None = None


def init(run_name: str | None = None, base_dir: str | None = None, tags: list[str] | None = None) -> Run:
    """Start a new run and set it as active."""
    global _active_run
    _active_run = Run(run_name=run_name, base_dir=base_dir, tags=tags)
    return _active_run


def _require_active() -> Run:
    if _active_run is None:
        raise RuntimeError("No active Trackle run. Call trackle.init() first.")
    return _active_run


def log_params(params: dict) -> None:
    run = _require_active()
    run.log_params(params)


def log_param(key: str, value) -> None:
    log_params({key: value})


def log_metric(key: str, value, step: int | None = None) -> None:
    run = _require_active()
    run.log_metric(key, value, step=step)


def log_artifact(path: str, name: str | None = None) -> None:
    run = _require_active()
    run.log_artifact(path, name=name)


def set_note(text: str) -> None:
    run = _require_active()
    run.set_note(text)


def finish() -> None:
    run = _require_active()
    run.finish()
    clear_active()


def clear_active() -> None:
    """Reset the active run (primarily for tests)."""
    global _active_run
    _active_run = None

