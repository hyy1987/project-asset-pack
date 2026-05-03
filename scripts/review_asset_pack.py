#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import REPO_ROOT, invoke_claude_skill, load_project_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review generated asset pack drafts and write formal reviewed outputs.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument(
        "--comments",
        help="Optional manual review comments file. Defaults to docs/manual/review-comments/<project_id>.md",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print Claude context without invoking Claude Code.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_project_config(args.project)

    generated_dir = REPO_ROOT / config.get("output", {}).get("generated", f"outputs/generated/{args.project}")
    reviewed_dir = REPO_ROOT / config.get("output", {}).get("reviewed", f"outputs/reviewed/{args.project}")
    comments_path = Path(args.comments) if args.comments else REPO_ROOT / "docs" / "manual" / "review-comments" / f"{args.project}.md"
    if not comments_path.is_absolute():
        comments_path = (REPO_ROOT / comments_path).resolve()

    if not generated_dir.is_dir():
        print(f"Generated asset pack directory is missing: {generated_dir}")
        return 1

    context = [
        f"Project id: {args.project}",
        f"Project config: configs/projects/{args.project}.yaml",
        f"Generated draft directory: {generated_dir.relative_to(REPO_ROOT).as_posix()}",
        f"Reviewed output directory: {reviewed_dir.relative_to(REPO_ROOT).as_posix()}",
        f"Manual review comments file: {comments_path.relative_to(REPO_ROOT).as_posix() if comments_path.exists() else '<missing>'}",
    ]
    if not comments_path.exists():
        context.append("Manual review comments are missing. Continue, but clearly mark that human comments were not provided.")

    if args.dry_run:
        print("\n".join(context))
        return 0

    return invoke_claude_skill(
        ".claude/skills/review-asset-pack/SKILL.md",
        context,
        label=f"Review asset pack for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
