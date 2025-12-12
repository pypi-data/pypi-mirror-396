"""
Git state capture helpers.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _run_git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip()


def capture(repo_path: str | Path | None = None) -> dict[str, Any]:
    cwd = Path(repo_path) if repo_path else Path.cwd()
    def _cmd(subargs: list[str]) -> str | None:
        return _run_git(["-C", str(cwd), *subargs])

    info = {
        "commit": _cmd(["rev-parse", "HEAD"]),
        "branch": _cmd(["rev-parse", "--abbrev-ref", "HEAD"]),
        "is_dirty": bool(_cmd(["status", "--porcelain"])),
        "remote": _cmd(["config", "--get", "remote.origin.url"]),
    }
    return info

