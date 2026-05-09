#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    generated_workbench_dir,
    invoke_agent_skill,
    load_workbench_state,
    project_security_rule_set,
    repo_relative,
    save_workbench_state,
    selected_agent,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or revise an Agent-First project lifecycle plan.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--revision-reason", default="", help="Why this lifecycle plan is being revised.")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated lifecycle plan scaffold.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = generated_workbench_dir(args.project)
    values = {
        "project_id": args.project,
        "generated_at": utc_now(),
    }
    lifecycle_path = write_rendered_template("lifecycle-plan.md", out_dir / "07-lifecycle-plan.md", values, overwrite=args.overwrite)

    state = load_workbench_state(args.project)
    previous_status = state.get("status", "new")
    state["status"] = "lifecycle-planned"
    state["lifecycle_plan"] = repo_relative(lifecycle_path)
    state["lifecycle_plan_updated_at"] = utc_now()
    state["lifecycle_review_required"] = False
    state["lifecycle_review_reason"] = ""
    if args.revision_reason:
        state.setdefault("lifecycle_revisions", []).append(
            {
                "reason": args.revision_reason,
                "path": repo_relative(lifecycle_path),
                "updated_at": state["lifecycle_plan_updated_at"],
                "previous_status": previous_status,
            }
        )
    save_workbench_state(args.project, state)
    print(f"Created lifecycle plan scaffold: {lifecycle_path}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    context_lines = [
        f"Project id: {args.project}",
        f"Security rule set: {project_security_rule_set(args.project)}",
        f"Lifecycle plan output: {repo_relative(lifecycle_path)}",
        f"Material intake index, if any: {repo_relative(out_dir / 'material-intake' / 'index.md')}",
        f"Change request index, if any: {repo_relative(out_dir / 'change-requests' / 'index.md')}",
        "Generate a full project lifecycle plan before planning individual stages.",
        f"After the lifecycle plan is drafted and human-confirmed, the Agent may create or complete project repositories before stage development: python scripts/init_project_repositories.py --project {args.project} --confirmed",
        "Repository initialization must never overwrite an existing remote repository or replace a different local origin.",
        "The repository creation reminder should appear after planning, not during workbench initialization or every resume.",
        "Read material intake and change request indexes before revising scope or stage roadmap.",
        "The lifecycle plan must guide all later stage plans.",
    ]
    if args.revision_reason:
        context_lines.append(f"Revision reason: {args.revision_reason}")

    return invoke_agent_skill(
        agent,
        ".claude/skills/plan-project-lifecycle/SKILL.md",
        context_lines,
        label=f"Plan project lifecycle for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

