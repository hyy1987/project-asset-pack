#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import load_workbench_state, repo_relative, reviewed_workbench_dir, save_workbench_state, utc_now, write_rendered_template


VALID_DECISIONS = {"confirmed", "changes-requested", "blocked"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human confirmation for Agent/project information alignment.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    parser.add_argument("--overwrite", action="store_true", help="Overwrite reviewed confirmation scaffold.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = reviewed_workbench_dir(args.project)
    values = {
        "project_id": args.project,
        "generated_at": utc_now(),
    }
    confirmation_path = write_rendered_template(
        "manual-human-confirmation.md",
        out_dir / "human-confirmation.md",
        values,
        overwrite=args.overwrite,
    )

    state = load_workbench_state(args.project)
    state["status"] = "context-confirmed" if args.decision == "confirmed" else "context-review-required"
    state["context_confirmation"] = {
        "decision": args.decision,
        "path": repo_relative(confirmation_path),
        "reviewed_at": utc_now(),
    }
    save_workbench_state(args.project, state)

    print(f"Created human confirmation record: {confirmation_path}")
    print(f"Decision: {args.decision}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
