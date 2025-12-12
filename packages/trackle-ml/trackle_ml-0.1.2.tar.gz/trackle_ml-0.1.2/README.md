# Trackle

Trackle is a lightweight, local-first, git-aware ML experiment tracker.

## Goals

- Local filesystem storage only
- No servers or networking
- Simple Python API and CLI
- Git-based reproducibility

## Installation

```bash
pip install trackle-ml            # from PyPI
# or for development
pip install -e .

# optional extras
# pip install trackle-ml[viz]     # matplotlib plots
# pip install trackle-ml[rich]    # richer CLI output (if extended)
```

## Quick start

```python
import trackle_ml as trackle

trackle.init(run_name="demo")
trackle.log_params({"lr": 0.01})
trackle.log_metric("loss", 0.5, step=1)
trackle.finish()
```

## Storage layout

Runs are stored locally (default `./trackle_experiments`):

```
trackle_experiments/
  runs/
    <run_id>/
      run.json       # metadata: name, created_at, finished_at, duration_s, tags
      params.json    # merged params
      metrics.csv    # step,key,value,timestamp
      context.json   # env info (python/os/hw/torch)
      git.json       # git commit/branch/dirty/remote
      artifacts/     # copied artifacts
      notes.md       # optional note
```

## CLI

```
trackle-ml list-runs [--base DIR] [--limit N]
trackle-ml diff-runs <run_a> <run_b> [--base DIR]
trackle-ml plot-metrics <run_id> [--key metric] [--base DIR]
```

