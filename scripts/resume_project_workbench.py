#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import (
    generated_workbench_dir,
    invoke_claude_skill,
    list_material_files,
    load_workbench_state,
    pre_project_materials_dir,
    project_security_rule_set,
    repo_relative,
    reviewed_workbench_dir,
    save_workbench_state,
    utc_now,
    workbench_state_path,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume an Agent-First workbench session.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", default="", help="Optional stage id to focus on.")
    parser.add_argument("--no-claude", action="store_true", help="Only generate resume brief; do not invoke Claude Code.")
    parser.add_argument("--overwrite", action="store_true", help="Compatibility flag; resume brief is always refreshed.")
    return parser.parse_args()


def list_markdown_files(root: Path, limit: int = 80) -> list[str]:
    if not root.exists():
        return []
    files: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            files.append(repo_relative(path))
            if len(files) >= limit:
                break
    return files


def format_list(items: list[str], empty: str) -> str:
    if not items:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in items)


def build_stage_summary(state: dict[str, Any]) -> str:
    stages = state.get("stages", {})
    if not stages:
        return "- 尚未发现阶段记录。"

    lines: list[str] = []
    for stage_id, stage in sorted(stages.items()):
        lines.append(f"- 阶段 ID：{stage_id}")
        lines.append(f"  - 名称：{stage.get('title', '待确认')}")
        lines.append(f"  - 状态：{stage.get('status', '待确认')}")
        if stage.get("plan"):
            lines.append(f"  - 阶段计划：{stage['plan']}")
        if stage.get("report"):
            lines.append(f"  - 阶段报告：{stage['report']}")
        if stage.get("asset_pack_update"):
            lines.append(f"  - 资产包更新：{stage['asset_pack_update']}")
        if stage.get("review"):
            lines.append(f"  - 人工评审：{stage['review']}")
    return "\n".join(lines)


def infer_next_action(state: dict[str, Any], stage_id: str | None) -> str:
    status = state.get("status", "new")
    current_stage_id = stage_id or state.get("current_stage_id")
    stages = state.get("stages", {})
    stage = stages.get(current_stage_id, {}) if current_stage_id else {}

    if status == "new":
        return "未发现已初始化的工作台状态。请先运行初始化流程。"
    if status == "initialized":
        return "工作台已初始化。下一步应人工确认信息对齐稿和项目启动清单，然后记录确认结果。"
    if status == "context-review-required":
        return "信息对齐仍需人工确认。请先补充或修正人工确认记录。"
    if status == "context-confirmed":
        return "项目上下文已确认。下一步应生成或确认第一阶段计划。"
    if status == "stage-planned":
        return f"阶段 {current_stage_id or '待确认'} 已有计划。下一步应确认阶段目标，并在授权边界内执行阶段任务。"
    if status == "stage-running":
        if stage.get("report"):
            return f"阶段 {current_stage_id or '待确认'} 已进入执行并已有报告草稿。下一步应补齐自检、测试、风险和资产包更新，然后提交人工评审。"
        return f"阶段 {current_stage_id or '待确认'} 已进入执行。下一步应生成阶段报告和资产包更新。"
    if status == "stage-review-required":
        return f"阶段 {current_stage_id or '待确认'} 未通过或仍需评审。下一步应根据评审意见返工。"
    if status == "stage-approved":
        return f"阶段 {state.get('last_approved_stage_id') or current_stage_id or '待确认'} 已通过评审。下一步可以规划下一阶段，或在阶段性归档时生成标准资产包初稿。"
    if status == "asset-pack-draft-generated":
        return "工作台过程资料已归档为标准资产包初稿。下一步应执行人工资产包评审定稿。"
    return "请根据状态文件、已评审资料和当前阶段输出确认下一步。"


def main() -> int:
    args = parse_args()
    state_path = workbench_state_path(args.project)
    if not state_path.is_file():
        print(f"Workbench state does not exist: {state_path}")
        print("Run init_project_workbench.py first, unless you intentionally moved the workspace state.")
        return 2

    state = load_workbench_state(args.project)
    generated_dir = generated_workbench_dir(args.project)
    reviewed_dir = reviewed_workbench_dir(args.project)
    material_dir = pre_project_materials_dir(args.project)
    stage_id = args.stage_id or state.get("current_stage_id") or ""

    values = {
        "project_id": args.project,
        "generated_at": utc_now(),
        "status": str(state.get("status", "待确认")),
        "current_stage_id": str(stage_id or "待确认"),
        "last_approved_stage_id": str(state.get("last_approved_stage_id", "待确认")),
        "state_file": repo_relative(state_path),
        "pre_project_materials": repo_relative(material_dir),
        "material_list": format_list(list_material_files(args.project), "未发现前期资料。"),
        "reviewed_outputs": format_list(list_markdown_files(reviewed_dir), "尚未发现人工评审或确认输出。"),
        "generated_outputs": format_list(list_markdown_files(generated_dir), "尚未发现 AI 初稿输出。"),
        "stage_summary": build_stage_summary(state),
        "next_action": infer_next_action(state, stage_id or None),
    }

    resume_path = write_rendered_template(
        "resume-brief.md",
        generated_dir / "resume-brief.md",
        values,
        overwrite=True,
    )

    state["last_resumed_at"] = values["generated_at"]
    state["resume_brief"] = repo_relative(resume_path)
    save_workbench_state(args.project, state)

    print(f"Created resume brief: {resume_path}")
    print(f"Workbench status: {state.get('status')}")
    print(f"Current stage: {stage_id or 'None'}")
    print(f"Next action: {values['next_action']}")

    if args.no_claude:
        return 0

    return invoke_claude_skill(
        ".claude/skills/resume-project-workbench/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Workbench state: workspace/workbench/{args.project}/state.json",
            f"Resume brief: outputs/generated/workbench/{args.project}/resume-brief.md",
            f"Current stage id: {stage_id or '<none>'}",
            f"Current status: {state.get('status')}",
            "Do not initialize the workbench again if the state file exists.",
            "Read reviewed outputs before generated outputs, then tell the user the current status and next action.",
        ],
        label=f"Resume Agent-First workbench for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
