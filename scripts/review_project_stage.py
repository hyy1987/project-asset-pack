#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    invoke_claude_skill,
    load_workbench_state,
    repo_relative,
    reviewed_workbench_dir,
    save_workbench_state,
    stage_reviewed_dir,
    utc_now,
    write_rendered_template,
)


VALID_DECISIONS = {"approve", "changes-requested", "blocked"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human review for an Agent-First project stage.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    parser.add_argument("--no-claude", action="store_true", help="Only create review record scaffold; do not invoke Claude Code.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite reviewed scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = load_workbench_state(args.project)
    stage = state.get("stages", {}).get(args.stage_id, {})
    title = args.title or stage.get("title") or args.stage_id
    out_dir = stage_reviewed_dir(args.project, args.stage_id)
    values = {
        "project_id": args.project,
        "stage_id": args.stage_id,
        "stage_title": title,
        "generated_at": utc_now(),
        "decision": args.decision,
    }
    review_path = write_rendered_template("stage-review.md", out_dir / "stage-review.md", values, overwrite=args.overwrite)

    state["status"] = "stage-approved" if args.decision == "approve" else "stage-review-required"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": title,
            "status": args.decision,
            "review": repo_relative(review_path),
            "reviewed_at": utc_now(),
        }
    )
    if args.decision == "approve":
        state["last_approved_stage_id"] = args.stage_id
    save_workbench_state(args.project, state)

    reviewed_workbench_dir(args.project).mkdir(parents=True, exist_ok=True)
    print(f"Created stage review record: {review_path}")
    print(f"Decision: {args.decision}")

    if args.no_claude:
        return 0

    return invoke_claude_skill(
        ".claude/skills/review-project-stage/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Human review decision: {args.decision}",
            f"Stage review output: outputs/reviewed/workbench/{args.project}/stages/{args.stage_id}/stage-review.md",
        ],
        label=f"Review stage {args.stage_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
