"""
Tests for artifact copying.
"""

from pathlib import Path

import trackle


def test_log_artifact_copies_file(tmp_path: Path) -> None:
    src = tmp_path / "source.txt"
    src.write_text("hello")

    trackle.init(base_dir=str(tmp_path))
    trackle.log_artifact(str(src))
    trackle.finish()

    run_dir = next((tmp_path / "runs").iterdir())
    dest = run_dir / "artifacts" / "source.txt"
    assert dest.exists()
    assert dest.read_text() == "hello"

