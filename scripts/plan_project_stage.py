#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    invoke_agent_skill,
    load_workbench_state,
    project_security_rule_set,
    repo_relative,
    save_workbench_state,
    selected_agent,
    stage_generated_dir,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an Agent-First stage plan.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--title", required=True, help="Stage title")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = stage_generated_dir(args.project, args.stage_id)
    state = load_workbench_state(args.project)
    lifecycle_plan = state.get("lifecycle_plan") or f"outputs/generated/workbench/{args.project}/lifecycle-plan.md"
    values = {
        "project_id": args.project,
        "stage_id": args.stage_id,
        "stage_title": args.title,
        "generated_at": utc_now(),
        "lifecycle_plan": lifecycle_plan,
    }
    plan_path = write_rendered_template("stage-plan.md", out_dir / "stage-plan.md", values, overwrite=args.overwrite)

    state["status"] = "stage-planned"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": args.title,
            "status": "planned",
            "plan": repo_relative(plan_path),
            "lifecycle_plan": lifecycle_plan,
        }
    )
    save_workbench_state(args.project, state)
    print(f"Created stage plan scaffold: {plan_path}")
    if not state.get("lifecycle_plan"):
        print("Warning: lifecycle plan is not recorded in state yet. Run plan_project_lifecycle.py before finalizing stage plans.")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/plan-project-stage/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {args.title}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Lifecycle plan: {lifecycle_plan}",
            f"Material intake index, if any: outputs/generated/workbench/{args.project}/material-intake/index.md",
            f"Change request index, if any: outputs/generated/workbench/{args.project}/change-requests/index.md",
            f"Stage plan output: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-plan.md",
            "Stage plan must follow the lifecycle plan. If the lifecycle plan is missing or outdated, ask to create or revise it first.",
            "Only include change requests in this stage when their status and target stage are human-confirmed.",
        ],
        label=f"Plan stage {args.stage_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
