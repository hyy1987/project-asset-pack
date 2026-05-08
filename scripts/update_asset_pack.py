#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from typing import Any

from _common import (
    add_agent_argument,
    collect_changes,
    invoke_agent_skill,
    load_baseline,
    save_baseline,
    selected_agent,
    sync_project_repositories,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update generated asset pack docs by comparing recorded remote baseline with latest synced repositories."
    )
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run Agent update even if no repository commits changed, and record a fresh baseline afterward.",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Use current local upstream refs without running git fetch. Useful for offline validation.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Fetch/sync and report changes without invoking an Agent or updating the recorded baseline.",
    )
    add_agent_argument(parser)
    return parser.parse_args()


def format_change(change: dict[str, Any]) -> list[str]:
    lines = [
        f"Repository: {change['repo']}",
        f"Branch: {change['branch']}",
        f"Upstream: {change['upstream']}",
        f"Previous documented HEAD: {change.get('previous_head') or '<missing baseline>'}",
        f"Current synced HEAD: {change['current_head']}",
        f"Reason: {change['reason']}",
    ]
    if change.get("reason") == "commit-range":
        lines.append(f"Previous commit is ancestor: {change.get('is_ancestor')}")
        lines.append(f"Commit count: {change.get('commit_count', 0)}")
        commits = change.get("commits", [])
        if commits:
            lines.append("Commits:")
            lines.extend(f"- {commit}" for commit in commits)
        files = change.get("files", [])
        if files:
            lines.append("Changed files:")
            lines.extend(f"- {file}" for file in files)
    return lines


def build_context(project_id: str, changes: list[dict[str, Any]], force: bool, previous_state: dict[str, Any] | None) -> list[str]:
    lines = [
        f"Project id: {project_id}",
        "All configured project repositories have already been checked and synced with their upstream remotes by the wrapper script.",
        f"Generated asset pack directory: outputs/generated/{project_id}/",
        f"Recorded baseline file: workspace/snapshots/{project_id}-repo-baseline.json",
    ]
    if previous_state:
        lines.extend(
            [
                f"Previous baseline recorded_at: {previous_state.get('recorded_at', '<unknown>')}",
                f"Previous baseline source: {previous_state.get('source', '<unknown>')}",
            ]
        )
    else:
        lines.append("Previous baseline is missing.")

    if force:
        lines.extend(
            [
                "",
                "Mode: force.",
                "A human requested an update pass even if repository commits did not change.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Mode: baseline-diff.",
                "Update generated asset pack docs only for repositories changed since the recorded baseline.",
            ]
        )

    if changes:
        lines.append("")
        lines.append("Repositories requiring asset pack review:")
        for change in changes:
            lines.append("")
            lines.extend(format_change(change))
    else:
        lines.append("")
        lines.append("No repository changes were detected.")

    return lines


def main() -> int:
    args = parse_args()
    previous_state = load_baseline(args.project)

    if previous_state is None and not args.force:
        print(
            f"No recorded baseline found for {args.project}. "
            f"Run `python scripts/save_remote_baseline.py --project {args.project}` after initial asset pack generation, "
            "or rerun update with --force."
        )
        return 1

    print("Checking remote repository updates and syncing local repositories when safe...")
    snapshots = sync_project_repositories(args.project, fetch=not args.no_fetch, fast_forward=True)
    changes = collect_changes(args.project, previous_state, snapshots)

    if args.check_only:
        if changes:
            print("Detected repository changes:")
            for change in changes:
                print("")
                print("\n".join(format_change(change)))
        else:
            print("No repository changes detected.")
        return 0

    if not args.force and not changes:
        print("No new remote commits detected since the recorded asset pack baseline. Skipping update.")
        return 0

    agent = selected_agent(args)
    if agent == "none":
        print("Agent invocation skipped. Asset pack was not updated and baseline was not changed.")
        print("\n".join(build_context(args.project, changes, args.force, previous_state)))
        return 0

    result = invoke_agent_skill(
        agent,
        ".claude/skills/update-asset-pack/SKILL.md",
        build_context(args.project, changes, args.force, previous_state),
        label=f"Update asset pack for {args.project}",
    )
    if result != 0:
        return result

    path = save_baseline(args.project, snapshots, source="update-asset-pack --force" if args.force else "update-asset-pack")
    print(f"Recorded updated repository baseline: {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
