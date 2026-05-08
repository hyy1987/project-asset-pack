#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    invoke_agent_skill,
    load_workbench_state,
    parse_quality_config,
    project_experience_path,
    repo_relative,
    run_quality_command,
    run_runtime_check,
    run_smoke_check,
    save_workbench_state,
    selected_agent,
    stage_generated_dir,
    utc_now,
    validate_quality_gate_file,
    validate_quality_command_results,
    validate_required_markdown,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check quality gate for one Agent-First project stage.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    add_agent_argument(parser)
    parser.add_argument("--run-commands", action="store_true", help="Run configured build/test/smoke quality commands.")
    parser.add_argument("--validate", action="store_true", help="Validate existing stage outputs without invoking an Agent.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when validation issues are found.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated quality gate scaffold.")
    return parser.parse_args()


def format_quality_results(project_id: str, stage_id: str, command_results: list[dict], runtime_results: list[dict], smoke_results: list[dict]) -> str:
    lines = [
        "# 质量命令执行结果",
        "",
        f"项目 ID：{project_id}",
        f"阶段 ID：{stage_id}",
        f"生成时间：{utc_now()}",
        "",
        "## 构建 / 测试 / 检查命令",
        "",
    ]
    if not command_results:
        lines.append("- 未配置质量命令。")
    for item in command_results:
        lines.extend(
            [
                f"### {item.get('name', 'unnamed')}",
                "",
                f"- 状态：{item.get('status')}",
                f"- 命令：{item.get('command', '未提供')}",
                f"- 工作目录：{item.get('cwd', '未提供')}",
                f"- 返回码：{item.get('returncode', '无')}",
                "",
                "```text",
                str(item.get("output_tail") or item.get("reason") or ""),
                "```",
                "",
            ]
        )
    lines.extend(["## 运行时启动检查", ""])
    if not runtime_results:
        lines.append("- 未配置运行时启动检查。")
    for item in runtime_results:
        health = item.get("healthcheck_result", {})
        lines.extend(
            [
                f"### {item.get('name', 'unnamed')}",
                "",
                f"- 状态：{item.get('status')}",
                f"- 启动命令：{item.get('command', '未提供')}",
                f"- 工作目录：{item.get('cwd', '未提供')}",
                f"- 健康检查：{item.get('healthcheck', '未提供')}",
                f"- 期望状态码：{item.get('expected_status', '未提供')}",
                f"- 实际状态码：{health.get('actual_status', '无')}",
                f"- 失败原因：{health.get('reason', '无')}",
                f"- 进程返回码：{item.get('process_returncode', '无')}",
                "",
                "```text",
                str(item.get("output_tail") or ""),
                "```",
                "",
            ]
        )
    lines.extend(["## 冒烟检查", ""])
    if not smoke_results:
        lines.append("- 未配置冒烟检查。")
    for item in smoke_results:
        lines.extend(
            [
                f"### {item.get('name', 'unnamed')}",
                "",
                f"- 状态：{item.get('status')}",
                f"- URL：{item.get('url', '未提供')}",
                f"- 期望状态码：{item.get('expected_status', '未提供')}",
                f"- 实际状态码：{item.get('actual_status', '无')}",
                f"- 失败原因：{item.get('reason', '无')}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    state = load_workbench_state(args.project)
    stage = state.get("stages", {}).get(args.stage_id, {})
    title = args.title or stage.get("title") or args.stage_id
    out_dir = stage_generated_dir(args.project, args.stage_id)
    asset_update = stage.get("asset_pack_update") or f"outputs/generated/workbench/{args.project}/stages/{args.stage_id}/asset-pack-update.md"
    values = {
        "project_id": args.project,
        "stage_id": args.stage_id,
        "stage_title": title,
        "generated_at": utc_now(),
        "asset_pack_update": asset_update,
    }
    quality_path = write_rendered_template("quality-gate.md", out_dir / "quality-gate.md", values, overwrite=args.overwrite)
    report_path = out_dir / "stage-report.md"
    asset_update_path = out_dir / "asset-pack-update.md"
    command_results_path = out_dir / "quality-command-results.md"

    command_issues: list[str] = []
    if args.run_commands:
        quality_config = parse_quality_config(args.project)
        command_results = [run_quality_command(command) for command in quality_config.get("commands", [])]
        runtime_results = [run_runtime_check(runtime) for runtime in quality_config.get("runtime", [])]
        smoke_results = [run_smoke_check(check) for check in quality_config.get("smoke", [])]
        if not command_results and not runtime_results and not smoke_results:
            command_issues.append("No quality.commands, quality.runtime, or quality.smoke entries configured for this project.")
        command_issues.extend(f"Quality command failed: {item.get('name')}" for item in command_results if item.get("status") != "passed")
        command_issues.extend(f"Runtime check failed: {item.get('name')}" for item in runtime_results if item.get("status") != "passed")
        command_issues.extend(f"Smoke check failed: {item.get('name')}" for item in smoke_results if item.get("status") != "passed")
        command_results_path.write_text(format_quality_results(args.project, args.stage_id, command_results, runtime_results, smoke_results), encoding="utf-8")

    state["status"] = "stage-quality-checking"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": title,
            "quality_gate": repo_relative(quality_path),
            "quality_command_results": repo_relative(command_results_path) if command_results_path.exists() else "",
            "quality_gate_updated_at": utc_now(),
        }
    )
    save_workbench_state(args.project, state)
    print(f"Created quality gate scaffold: {quality_path}")

    validation_issues = []
    validation_issues.extend(validate_required_markdown(report_path, "Stage report"))
    validation_issues.extend(validate_required_markdown(asset_update_path, "Asset pack update", allow_markers=True))
    validation_issues.extend(command_issues)
    if args.run_commands:
        validation_issues.extend(validate_required_markdown(command_results_path, "Quality command results", allow_markers=True))
        validation_issues.extend(validate_quality_command_results(command_results_path, required=True))
    validation_issues.extend(validate_quality_gate_file(quality_path))

    if args.validate or selected_agent(args) == "none":
        if validation_issues:
            print("Quality gate validation found issues:")
            for issue in validation_issues:
                print(f"- {issue}")
            if args.strict:
                return 1
        else:
            print("Quality gate validation passed.")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/check-stage-quality/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Project experience file: {repo_relative(project_experience_path(args.project))}",
            f"Stage plan: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-plan.md",
            f"Stage report: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-report.md",
            f"Asset pack update: {asset_update}",
            f"Quality command results: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/quality-command-results.md",
            f"Quality gate output: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/quality-gate.md",
        ],
        label=f"Check stage quality for {args.project} {args.stage_id}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
