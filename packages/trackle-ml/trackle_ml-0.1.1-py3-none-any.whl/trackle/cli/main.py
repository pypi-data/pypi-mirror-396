"""
Command-line entrypoint for Trackle.
"""

from __future__ import annotations

import argparse
import sys

from . import diff_runs
from . import list_runs
from . import plot_metrics


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="trackle", description="Trackle CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-runs", help="List recorded runs")
    p_list.add_argument("--base", dest="base_dir", help="Base experiments directory", default=None)
    p_list.add_argument("--limit", type=int, default=20, help="Maximum runs to show")

    p_diff = subparsers.add_parser("diff-runs", help="Diff two runs")
    p_diff.add_argument("run_a")
    p_diff.add_argument("run_b")
    p_diff.add_argument("--base", dest="base_dir", help="Base experiments directory", default=None)

    p_plot = subparsers.add_parser("plot-metrics", help="Summarize metrics")
    p_plot.add_argument("run_id")
    p_plot.add_argument("--key", dest="metric_key", help="Metric key to focus on", default=None)
    p_plot.add_argument("--base", dest="base_dir", help="Base experiments directory", default=None)

    args = parser.parse_args(argv)

    if args.command == "list-runs":
        list_runs.run(base_dir=args.base_dir, limit=args.limit)
    elif args.command == "diff-runs":
        diff_runs.run(args.run_a, args.run_b, base_dir=args.base_dir)
    elif args.command == "plot-metrics":
        plot_metrics.run(args.run_id, base_dir=args.base_dir, metric_key=args.metric_key)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

