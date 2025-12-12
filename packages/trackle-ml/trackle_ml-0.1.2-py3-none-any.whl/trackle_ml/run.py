"""
Run lifecycle and state management.
"""

from __future__ import annotations

import atexit
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import context
from . import git
from . import storage
from . import utils


@dataclass
class Run:
    run_name: str | None = None
    base_dir: str | None = None
    tags: Iterable[str] | None = None
    run_id: str = field(default_factory=utils.new_run_id)
    root: Path | None = None
    finished: bool = False
    created_at: str = field(default_factory=utils.timestamp)
    _started: dt.datetime = field(default_factory=utils.now_utc, repr=False)

    def __post_init__(self) -> None:
        self.root = storage.create_run_dir(self.base_dir, self.run_id, self.run_name)
        storage.write_run_info(
            self.root,
            self.run_name,
            self.created_at,
            finished_at=None,
            duration_s=None,
            tags=self.tags,
        )
        storage.write_context(self.root, context.capture())
        storage.write_git(self.root, git.capture(self.base_dir))
        atexit.register(self._finish_silent)

    def _ensure_active(self) -> None:
        if self.finished:
            raise RuntimeError("Run already finished; no further logging allowed.")

    def log_params(self, params: dict[str, Any]) -> None:
        self._ensure_active()
        storage.write_params(self.root, params)

    def log_metric(self, key: str, value: Any, step: int | None = None) -> None:
        self._ensure_active()
        storage.append_metric(self.root, key, value, step=step)

    def log_artifact(self, path: str, name: str | None = None) -> None:
        self._ensure_active()
        storage.store_artifact(self.root, path, name=name)

    def set_note(self, text: str) -> None:
        self._ensure_active()
        storage.write_note(self.root, text)

    def finish(self) -> None:
        if self.finished:
            return
        finished_at_dt = utils.now_utc()
        duration_s = (finished_at_dt - self._started).total_seconds()
        storage.write_run_info(
            self.root,
            self.run_name,
            self.created_at,
            finished_at=utils.timestamp(finished_at_dt),
            duration_s=duration_s,
            tags=self.tags,
        )
        self.finished = True

    def _finish_silent(self) -> None:
        try:
            self.finish()
        except Exception:
            # Avoid raising during interpreter shutdown.
            pass

