#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    generated_asset_pack_dir,
    get_project_repositories,
    invoke_agent_skill,
    project_docs_root,
    repo_relative,
    reviewed_asset_pack_dir,
    run_git,
    selected_agent,
)


VALID_PERIODS = {"daily", "weekly", "milestone", "release", "handover"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a project health check through an Agent client.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--period", default="weekly", choices=sorted(VALID_PERIODS))
    add_agent_argument(parser)
    parser.add_argument("--dry-run", action="store_true", help="Print Agent context without invoking an Agent client.")
    return parser.parse_args()


def repo_status_lines(project_id: str) -> list[str]:
    lines: list[str] = []
    for repo in get_project_repositories(project_id):
        path = repo["path"]
        if not path.is_dir() or not (path / ".git").exists():
            lines.append(f"- {repo['name']}: not a git repository or path missing")
            continue
        branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, capture_output=True).strip()
        head = run_git(["rev-parse", "HEAD"], cwd=path, capture_output=True).strip()
        status = run_git(["status", "--short"], cwd=path, capture_output=True).strip()
        dirty = "dirty" if status else "clean"
        lines.append(f"- {repo['name']}: branch {branch}, HEAD {head[:12]}, worktree {dirty}")
    return lines


def main() -> int:
    args = parse_args()
    generated_dir = generated_asset_pack_dir(args.project)
    reviewed_dir = reviewed_asset_pack_dir(args.project)
    health_dir = project_docs_root(args.project) / "outputs" / "generated" / "project-health"

    context = [
        f"Project id: {args.project}",
        f"Period: {args.period}",
        f"Project config: configs/projects/{args.project}.yaml",
        f"Generated asset pack directory: {repo_relative(generated_dir)}",
        f"Reviewed asset pack directory: {repo_relative(reviewed_dir)}",
        f"Health output directory: {repo_relative(health_dir)}",
        "Current repository status:",
        *repo_status_lines(args.project),
    ]
    if not generated_dir.exists() and not reviewed_dir.exists():
        context.append("No generated or reviewed asset pack exists yet. Mark asset pack sync status as missing.")

    if args.dry_run:
        print("\n".join(context))
        return 0

    return invoke_agent_skill(
        selected_agent(args),
        ".claude/skills/check-project-health/SKILL.md",
        context,
        label=f"Check project health for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
