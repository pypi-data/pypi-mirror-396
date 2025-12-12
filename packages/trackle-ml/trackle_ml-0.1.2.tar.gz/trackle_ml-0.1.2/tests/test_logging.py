"""
Tests for params and metrics logging.
"""

import json
from pathlib import Path

import trackle


def test_log_params_and_metrics(tmp_path: Path) -> None:
    trackle.init(base_dir=str(tmp_path))
    trackle.log_params({"lr": 0.1})
    trackle.log_metric("loss", 1.0, step=0)
    trackle.log_metric("loss", 0.5, step=1)
    trackle.finish()

    run_dir = next((tmp_path / "runs").iterdir())
    params = json.loads((run_dir / "params.json").read_text())
    assert params["lr"] == 0.1

    metrics_lines = (run_dir / "metrics.csv").read_text().strip().splitlines()
    assert metrics_lines[0] == "step,key,value,timestamp"
    assert metrics_lines[1].startswith("0,loss,1.0,")
    assert metrics_lines[2].startswith("1,loss,0.5,")

