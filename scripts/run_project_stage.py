#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    invoke_claude_skill,
    load_workbench_state,
    project_security_rule_set,
    repo_relative,
    save_workbench_state,
    stage_generated_dir,
    utc_now,
    workbench_allows_code_changes,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an Agent-First project stage through Claude Code.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    parser.add_argument("--allow-code-changes", action="store_true", help="Pass explicit human authorization for code changes.")
    parser.add_argument("--no-claude", action="store_true", help="Only create report scaffold; do not invoke Claude Code.")
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
    if not asset_update_path.exists() or args.overwrite:
        asset_update_path.write_text(
            f"# 阶段资产包更新\n\n项目 ID：{args.project}\n阶段 ID：{args.stage_id}\n生成时间：{utc_now()}\n\n待 Agent 根据阶段执行结果更新。\n",
            encoding="utf-8",
        )

    config_allows = workbench_allows_code_changes(args.project)
    code_changes_authorized = bool(args.allow_code_changes and config_allows)
    if args.allow_code_changes and not config_allows:
        print("Code changes were requested, but workbench.allow_code_changes is not true in project config.")
        print("Claude will be instructed not to modify business repositories.")

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
            "code_changes_authorized": code_changes_authorized,
        }
    )
    save_workbench_state(args.project, state)
    print(f"Created stage report scaffold: {report_path}")
    print(f"Code changes authorized: {code_changes_authorized}")

    if args.no_claude:
        return 0

    return invoke_claude_skill(
        ".claude/skills/run-project-stage/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Project config allows code changes: {config_allows}",
            f"Human explicitly authorized code changes for this run: {args.allow_code_changes}",
            f"Effective code changes authorized: {code_changes_authorized}",
            f"Stage plan: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-plan.md",
            f"Stage report output: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-report.md",
            f"Asset pack update output: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/asset-pack-update.md",
        ],
        label=f"Run stage {args.stage_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
