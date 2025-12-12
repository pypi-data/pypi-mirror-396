"""
Tests for git context capture.
"""

from pathlib import Path

from trackle import git


def test_git_capture_returns_keys(tmp_path: Path) -> None:
    info = git.capture(tmp_path)
    assert set(info.keys()) == {"commit", "branch", "is_dirty", "remote"}

