# Trackle

Trackle is a lightweight, local-first, git-aware ML experiment tracker.

## Goals

- Local filesystem storage only
- No servers or networking
- Simple Python API and CLI
- Git-based reproducibility

## Quick start

```bash
pip install -e .
```

```python
import trackle

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
trackle list-runs [--base DIR] [--limit N]
trackle diff-runs <run_a> <run_b> [--base DIR]
trackle plot-metrics <run_id> [--key metric] [--base DIR]
```

## Extras

- `pip install trackle[viz]` to enable matplotlib plotting in the CLI.
- `pip install trackle[rich]` to enable richer CLI output (if extended later).

