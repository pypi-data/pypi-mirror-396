"""
Utility helpers for Trackle.
"""

from __future__ import annotations

import datetime as dt
import os
import random
import string
from pathlib import Path
from typing import Any, Mapping


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def timestamp(ts: dt.datetime | None = None) -> str:
    ts = ts or now_utc()
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_id(length: int = 6) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def new_run_id(ts: dt.datetime | None = None) -> str:
    ts_str = (ts or now_utc()).strftime("%Y%m%d-%H%M%S")
    return f"{ts_str}_{short_id()}"


def atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)


def ensure_jsonable(data: Mapping[str, Any]) -> dict[str, Any]:
    return dict(data)

