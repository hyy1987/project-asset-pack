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
    workbench_allows_code_changes,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an Agent-First project stage through an Agent client.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    parser.add_argument("--allow-code-changes", action="store_true", help="Pass explicit human authorization for code changes.")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = load_workbench_state(args.project)
    stage = state.get("stages", {}).get(args.stage_id, {})
    title = args.title or stage.get("title") or args.stage_id
    out_dir = stage_generated_dir(args.project, args.stage_id)
    values = {
        "project_id": args.project,
        "stage_id": args.stage_id,
        "stage_title": title,
        "generated_at": utc_now(),
    }
    report_path = write_rendered_template("stage-report.md", out_dir / "stage-report.md", values, overwrite=args.overwrite)
    asset_update_path = out_dir / "asset-pack-update.md"
    quality_gate_path = write_rendered_template("quality-gate.md", out_dir / "quality-gate.md", {**values, "asset_pack_update": repo_relative(asset_update_path)}, overwrite=args.overwrite)
    if not asset_update_path.exists() or args.overwrite:
        asset_update_path.write_text(
            f"# 阶段资产包更新\n\n项目 ID：{args.project}\n阶段 ID：{args.stage_id}\n生成时间：{utc_now()}\n\n待 Agent 根据阶段执行结果更新。\n",
            encoding="utf-8",
        )

    config_allows = workbench_allows_code_changes(args.project)
    code_changes_authorized = bool(args.allow_code_changes and config_allows)
    if args.allow_code_changes and not config_allows:
        print("Code changes were requested, but workbench.allow_code_changes is not true in project config.")
        print("The Agent client will be instructed not to modify business repositories.")

    state["status"] = "stage-running"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": title,
            "status": "running",
            "report": repo_relative(report_path),
            "asset_pack_update": repo_relative(asset_update_path),
            "quality_gate": repo_relative(quality_gate_path),
            "code_changes_authorized": code_changes_authorized,
        }
    )
    save_workbench_state(args.project, state)
    print(f"Created stage report scaffold: {report_path}")
    print(f"Created quality gate scaffold: {quality_gate_path}")
    print(f"Code changes authorized: {code_changes_authorized}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/run-project-stage/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Project config allows code changes: {config_allows}",
            f"Human explicitly authorized code changes for this run: {args.allow_code_changes}",
            f"Effective code changes authorized: {code_changes_authorized}",
            f"Material intake index, if any: {repo_relative(out_dir.parent / 'material-intake' / 'index.md')}",
            f"Change request index, if any: {repo_relative(out_dir.parent / 'change-requests' / 'index.md')}",
            f"Stage plan: {repo_relative(out_dir / 'stage-plan.md')}",
            f"Stage report output: {repo_relative(report_path)}",
            f"Asset pack update output: {repo_relative(asset_update_path)}",
            f"Quality gate output: {repo_relative(quality_gate_path)}",
            "Do not implement new change requests unless they are explicitly included in the approved stage plan.",
            "If new requirements, requirement changes, scope changes, or acceptance-criteria changes appear during this run, pause that work and record a CR before implementation.",
            "A CR can be implemented in this stage only after human confirmation, an accepted-current-stage status, and updated stage plan plus quality gate checks.",
        ],
        label=f"Run stage {args.stage_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
