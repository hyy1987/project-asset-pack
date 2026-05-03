#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import save_baseline, sync_project_repositories


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save current remote-synced repository baseline for an asset pack project.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Use current local upstream refs without running git fetch. Useful for offline validation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshots = sync_project_repositories(args.project, fetch=not args.no_fetch, fast_forward=True)
    path = save_baseline(args.project, snapshots, source="save-remote-baseline")
    print(f"Saved repository baseline: {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
