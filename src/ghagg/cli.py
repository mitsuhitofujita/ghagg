import argparse
import json
import logging
import sys
from datetime import date

from ghagg.aggregator import aggregate
from ghagg.fetcher import fetch_pull_requests
from ghagg.storage import save


def _parse_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: '{value}'. Expected YYYY-MM-DD.")
    return value


def _parse_repo(value: str) -> str:
    if "/" not in value or value.count("/") != 1:
        raise argparse.ArgumentTypeError(f"Invalid repo format: '{value}'. Expected 'owner/repo'.")
    owner, name = value.split("/")
    if not owner or not name:
        raise argparse.ArgumentTypeError(f"Invalid repo format: '{value}'. Expected 'owner/repo'.")
    return value


def _run_fetch(args):
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    prs = fetch_pull_requests(args.repo, args.since, args.until)
    filepath = save(prs, args.repo, args.since, args.until, args.label, args.output_dir)
    print(f"Done. {len(prs)} PRs saved to {filepath}")


def _run_aggregate(args):
    result = aggregate(args.label, args.data_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="ghagg",
        description="GitHub PR data aggregation tool",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # fetch subcommand
    fetch_parser = subparsers.add_parser("fetch", help="Fetch PR data from GitHub")
    fetch_parser.add_argument("label", help="Label for grouping output (e.g. 2025, 2026)")
    fetch_parser.add_argument("repo", type=_parse_repo, help="GitHub repository (owner/repo)")
    fetch_parser.add_argument("--since", required=True, type=_parse_date, help="Start date (YYYY-MM-DD)")
    fetch_parser.add_argument("--until", required=True, type=_parse_date, help="End date (YYYY-MM-DD)")
    fetch_parser.add_argument("--output-dir", default="data/json/", help="Output directory (default: data/json/)")

    # aggregate subcommand
    agg_parser = subparsers.add_parser("aggregate", help="Aggregate PR stats per member from saved JSON")
    agg_parser.add_argument("label", help="Label to aggregate (e.g. 2025, 2026)")
    agg_parser.add_argument("--data-dir", default="data/json/", help="Data directory (default: data/json/)")

    args = parser.parse_args()
    if args.command == "fetch":
        _run_fetch(args)
    elif args.command == "aggregate":
        _run_aggregate(args)


if __name__ == "__main__":
    main()
