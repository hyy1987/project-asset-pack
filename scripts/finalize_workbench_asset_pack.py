#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import (
    add_agent_argument,
    generated_asset_pack_dir,
    generated_workbench_dir,
    invoke_agent_skill,
    list_material_files,
    load_project_config,
    load_workbench_state,
    project_security_rule_set,
    REPO_ROOT,
    repo_relative,
    reviewed_workbench_dir,
    save_workbench_state,
    selected_agent,
    utc_now,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize workbench process outputs into a standard asset pack draft.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated scaffold files.")
    return parser.parse_args()


def write_text_if_needed(path: Path, content: str, overwrite: bool) -> Path:
    if path.exists() and not overwrite:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_standard_template(template_rel: str, output_path: Path, values: dict[str, str], overwrite: bool) -> Path:
    template_path = REPO_ROOT / "templates" / template_rel
    if not template_path.is_file():
        raise RuntimeError(f"Missing template: {template_path}")
    content = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return write_text_if_needed(output_path, content, overwrite)


def main() -> int:
    args = parse_args()
    config = load_project_config(args.project)
    project_name = config.get("project_name", args.project)
    out_dir = generated_asset_pack_dir(args.project)
    workbench_generated = generated_workbench_dir(args.project)
    workbench_reviewed = reviewed_workbench_dir(args.project)
    state = load_workbench_state(args.project)
    values = {
        "project_id": args.project,
        "project_name": project_name,
        "generated_at": utc_now(),
    }

    created = [
        write_standard_template("asset-pack/asset-pack-draft.md", out_dir / "asset-pack-draft.md", values, args.overwrite)
    ]

    template_pairs = [
        ("review-report/review-report.md", "review-report.md"),
        ("missing-materials/missing-materials.md", "missing-materials.md"),
        ("risk-list/risk-list.md", "risk-list.md"),
        ("reusable-assets/reusable-assets.md", "reusable-assets.md"),
    ]
    for template_rel, output_name in template_pairs:
        created.append(write_standard_template(template_rel, out_dir / output_name, values, args.overwrite))

    stages = state.get("stages", {})
    stage_lines = []
    for stage_id, stage in sorted(stages.items()):
        stage_lines.extend(
            [
                f"- 阶段 ID：{stage_id}",
                f"  - 名称：{stage.get('title', '待确认')}",
                f"  - 状态：{stage.get('status', '待确认')}",
                f"  - 计划：{stage.get('plan', '待确认')}",
                f"  - 报告：{stage.get('report', '待确认')}",
                f"  - 评审：{stage.get('review', '待确认')}",
            ]
        )
    archive_summary = f"""# 工作台结题归档摘要

项目：{project_name}

项目 ID：{args.project}

生成时间：{utc_now()}

## 工作台状态

- 当前状态：{state.get('status', '待确认')}
- 当前阶段：{state.get('current_stage_id', '待确认')}
- 最近通过阶段：{state.get('last_approved_stage_id', '待确认')}
- 全周期规划：{state.get('lifecycle_plan', '待确认')}

## 前期资料

{chr(10).join(f'- {item}' for item in list_material_files(args.project)) or '- 未发现前期资料。'}

## 工作台输入输出

- 工作台 AI 输出：{repo_relative(workbench_generated)}
- 工作台人工确认与评审：{repo_relative(workbench_reviewed)}
- 工作台状态文件：workspace/workbench/{args.project}/state.json
- 全周期规划文件：{state.get('lifecycle_plan', '待确认')}

## 阶段记录

{chr(10).join(stage_lines) if stage_lines else '- 未发现阶段记录。'}

## 归档说明

本摘要用于把工作台过程资料汇总为标准项目资产包初稿。归档结果仍为 AI 初稿，必须经过人工评审后才能定稿。
"""
    created.append(write_text_if_needed(out_dir / "workbench-archive-summary.md", archive_summary, args.overwrite))

    state["status"] = "asset-pack-draft-generated"
    state["asset_pack_draft"] = {
        "generated_at": utc_now(),
        "output_dir": repo_relative(out_dir),
        "files": [repo_relative(path) for path in created],
    }
    save_workbench_state(args.project, state)

    print(f"Created asset pack draft scaffold from workbench: {out_dir}")
    for path in created:
        print(f"- {path}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/finalize-workbench-asset-pack/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Project name: {project_name}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Workbench generated directory: {repo_relative(workbench_generated)}",
            f"Workbench reviewed directory: {repo_relative(workbench_reviewed)}",
            f"Lifecycle plan: {state.get('lifecycle_plan', '<missing>')}",
            f"Standard asset pack draft directory: {repo_relative(out_dir)}",
            "Generate the standard asset pack draft files from workbench process evidence.",
        ],
        label=f"Finalize workbench asset pack for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
