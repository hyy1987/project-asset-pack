#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import (
    add_agent_argument,
    ensure_workbench_dirs,
    generated_asset_pack_dir,
    generated_workbench_dir,
    get_project_repositories,
    invoke_agent_skill,
    list_material_files,
    load_workbench_state,
    pre_project_materials_dir,
    project_experience_path,
    project_security_rule_set,
    repo_relative,
    reviewed_asset_pack_dir,
    run_git,
    save_workbench_state,
    selected_agent,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start an Agent-First workbench for an active in-progress project without requiring asset pack or health reports first."
    )
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated workbench scaffold files.")
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


def repository_status_lines(project_id: str) -> tuple[list[str], list[dict[str, Any]]]:
    lines: list[str] = []
    records: list[dict[str, Any]] = []
    for repo in get_project_repositories(project_id):
        path = repo["path"]
        record: dict[str, Any] = {
            "name": repo["name"],
            "path": repo_relative(path),
            "description": repo.get("description", ""),
        }
        if not path.is_dir():
            record["status"] = "missing"
            lines.append(f"{repo['name']}：路径不存在，{repo_relative(path)}")
            records.append(record)
            continue
        if not (path / ".git").exists():
            record["status"] = "not-git"
            lines.append(f"{repo['name']}：不是 Git 仓库，{repo_relative(path)}")
            records.append(record)
            continue
        try:
            branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, capture_output=True).strip()
            head = run_git(["rev-parse", "HEAD"], cwd=path, capture_output=True).strip()
            status = run_git(["status", "--short"], cwd=path, capture_output=True).strip()
            record.update(
                {
                    "status": "dirty" if status else "clean",
                    "branch": branch,
                    "head": head,
                    "worktree_status": status,
                }
            )
            dirty_label = "有本地变更" if status else "干净"
            lines.append(f"{repo['name']}：{repo_relative(path)}，分支 {branch}，HEAD {head[:12]}，工作区{dirty_label}")
        except Exception as exc:
            record["status"] = "inspect-failed"
            record["reason"] = str(exc)
            lines.append(f"{repo['name']}：状态读取失败，{repo_relative(path)}，原因：{exc}")
        records.append(record)
    return lines, records


def ensure_project_experience(project_id: str, source_files: list[str], overwrite: bool = False) -> str:
    path = project_experience_path(project_id)
    if path.exists() and not overwrite:
        return repo_relative(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# 项目经验库",
                "",
                f"项目 ID：{project_id}",
                "",
                "本项目作为在研项目接入工作台。后续阶段计划和执行前必须读取本文件。",
                "",
                "## 接入来源",
                "",
                format_list(source_files, "本次接入未发现已有资产包，以上下文确认和业务仓库状态为主。"),
                "",
                "## 后续必须遵守",
                "",
                "- 不把仓库状态或历史资料中的推断直接写成已确认事实。",
                "- 下一阶段开发前必须确认当前交付范围、验收标准和不做范围。",
                "- 风险、缺口和遗留问题必须进入阶段计划或风险行动清单。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return repo_relative(path)


def main() -> int:
    args = parse_args()
    ensure_workbench_dirs(args.project)

    out_dir = generated_workbench_dir(args.project)
    material_dir = pre_project_materials_dir(args.project)
    generated_asset_dir = generated_asset_pack_dir(args.project)
    reviewed_asset_dir = reviewed_asset_pack_dir(args.project)

    materials = list_material_files(args.project)
    repo_lines, repo_records = repository_status_lines(args.project)
    generated_asset_files = list_markdown_files(generated_asset_dir)
    reviewed_asset_files = list_markdown_files(reviewed_asset_dir)
    source_files = [*reviewed_asset_files, *generated_asset_files]

    values = {
        "project_id": args.project,
        "generated_at": utc_now(),
        "pre_project_materials": repo_relative(material_dir),
        "material_list": format_list(materials, "未发现前期资料。"),
        "repository_list": format_list(repo_lines, "项目配置中未发现业务仓库。"),
        "generated_asset_pack_files": format_list(generated_asset_files, "未发现已有 AI 资产包初稿。"),
        "reviewed_asset_pack_files": format_list(reviewed_asset_files, "未发现人工评审后的资产包。"),
    }

    created = [
        write_rendered_template("active-project-intake.md", out_dir / "active-project-intake.md", values, overwrite=args.overwrite),
        write_rendered_template("info-alignment.md", out_dir / "info-alignment.md", values, overwrite=args.overwrite),
        write_rendered_template("project-kickoff-checklist.md", out_dir / "project-kickoff-checklist.md", values, overwrite=args.overwrite),
        write_rendered_template("responsibility-questions.md", out_dir / "responsibility-questions.md", values, overwrite=args.overwrite),
        write_rendered_template("asset-pack-skeleton.md", out_dir / "asset-pack-skeleton.md", values, overwrite=args.overwrite),
        write_rendered_template("risk-action-list.md", out_dir / "risk-action-list.md", values, overwrite=args.overwrite),
    ]

    project_experience = ensure_project_experience(args.project, source_files, overwrite=args.overwrite)

    state = load_workbench_state(args.project)
    state["status"] = "active-project-adopted"
    state["pre_project_materials"] = repo_relative(material_dir)
    state["project_experience"] = project_experience
    state["active_project_intake"] = {
        "adopted_at": utc_now(),
        "generated_asset_pack_dir": repo_relative(generated_asset_dir),
        "reviewed_asset_pack_dir": repo_relative(reviewed_asset_dir),
        "repositories": repo_records,
        "generated_asset_pack_files": generated_asset_files,
        "reviewed_asset_pack_files": reviewed_asset_files,
        "intake_summary": repo_relative(created[0]),
    }
    state["generated_outputs"] = sorted(set(state.get("generated_outputs", []) + [repo_relative(path) for path in created]))
    state["lifecycle_review_required"] = True
    state["lifecycle_review_reason"] = "Active in-progress project adopted into workbench; generate or revise lifecycle plan before stage work."
    save_workbench_state(args.project, state)

    print(f"Started active project workbench: {out_dir}")
    print(f"Active project intake: {created[0]}")
    print(f"Project experience file: {project_experience}")
    if not source_files:
        print("No existing asset pack found; continuing with project config, repositories, and materials.")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/start-active-project-workbench/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Active project intake summary: {repo_relative(created[0])}",
            f"Generated asset pack directory, optional: {repo_relative(generated_asset_dir)}",
            f"Reviewed asset pack directory, optional: {repo_relative(reviewed_asset_dir)}",
            f"Project experience file: {project_experience}",
            "Start an Agent-First workbench for an active in-progress project.",
            "Existing asset packs are optional context, not prerequisites.",
            "Update info alignment, kickoff checklist, asset pack skeleton, risk/action list, and lifecycle planning inputs.",
            "Do not start stage development until lifecycle plan and next stage plan are generated or revised.",
        ],
        label=f"Start active project workbench for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
