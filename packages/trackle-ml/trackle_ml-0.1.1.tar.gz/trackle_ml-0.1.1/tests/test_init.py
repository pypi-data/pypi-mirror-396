"""
Tests for Trackle init and run info.
"""

import json
from pathlib import Path

import trackle


def test_init_creates_run(tmp_path: Path) -> None:
    trackle.init(run_name="demo", base_dir=str(tmp_path))
    trackle.finish()
    runs_dir = tmp_path / "runs"
    run_dirs = list(runs_dir.iterdir())
    assert run_dirs, "run directory should be created"
    run_json = json.loads((run_dirs[0] / "run.json").read_text())
    assert run_json["run_name"] == "demo"
    assert run_json["created_at"]
    assert run_json["finished_at"]

