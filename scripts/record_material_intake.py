#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import (
    REPO_ROOT,
    add_agent_argument,
    generated_workbench_dir,
    invoke_agent_skill,
    load_workbench_state,
    project_docs_root,
    project_security_rule_set,
    repo_relative,
    save_workbench_state,
    selected_agent,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record new project material into the Agent-First workbench.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--material-id", default="", help="Material id, for example MI-2026-001. Defaults to next id.")
    parser.add_argument("--source", default="", help="Source file, directory, URL, or chat note reference.")
    parser.add_argument("--title", default="", help="Material title.")
    parser.add_argument(
        "--material-type",
        default="unknown",
        choices=("requirement-doc", "meeting-note", "design-doc", "api-doc", "test-doc", "delivery-doc", "chat-note", "other", "unknown"),
    )
    parser.add_argument("--stage-id", default="", help="Related stage id if any.")
    parser.add_argument("--description", default="", help="Short source description or chat-provided note.")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing material record.")
    return parser.parse_args()


def material_dir(project_id: str) -> Path:
    return generated_workbench_dir(project_id) / "material-intake"


def existing_ids(root: Path, prefix: str) -> list[int]:
    if not root.exists():
        return []
    values: list[int] = []
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d{{3,}})\.md$")
    for path in root.glob(f"{prefix}-*.md"):
        match = pattern.match(path.name)
        if match:
            values.append(int(match.group(1)))
    return values


def next_material_id(project_id: str) -> str:
    root = material_dir(project_id)
    year = utc_now()[:4]
    prefix = f"MI-{year}"
    number = max(existing_ids(root, prefix), default=0) + 1
    return f"{prefix}-{number:03d}"


def source_display(project_id: str, raw_source: str) -> str:
    if not raw_source:
        return "聊天补充或待提供资料路径"
    path = Path(raw_source)
    if not path.is_absolute():
        candidate = (REPO_ROOT / path).resolve()
        if not candidate.exists():
            candidate = (project_docs_root(project_id) / path).resolve()
    else:
        candidate = path
    if candidate.exists():
        return repo_relative(candidate)
    return raw_source


def update_index(project_id: str, state_materials: list[dict[str, str]]) -> Path:
    root = material_dir(project_id)
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 资料接入索引",
        "",
        f"项目 ID：{project_id}",
        f"更新时间：{utc_now()}",
        "",
        "| 资料 ID | 标题 | 类型 | 关联阶段 | 来源 | 记录 | 状态 |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in state_materials:
        lines.append(
            "| {material_id} | {title} | {material_type} | {stage_id} | {source} | {record} | {status} |".format(
                material_id=item.get("material_id", ""),
                title=item.get("title", ""),
                material_type=item.get("material_type", ""),
                stage_id=item.get("stage_id", "未关联"),
                source=item.get("source", ""),
                record=item.get("record", ""),
                status=item.get("status", "recorded"),
            )
        )
    if not state_materials:
        lines.append("| 待记录 | 待补充 | 待确认 | 待确认 | 待确认 | 待确认 | 待处理 |")
    path = root / "index.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    material_id = args.material_id or next_material_id(args.project)
    root = material_dir(args.project)
    record_path = root / f"{material_id}.md"
    source = source_display(args.project, args.source)
    title = args.title or material_id
    values = {
        "project_id": args.project,
        "material_id": material_id,
        "generated_at": utc_now(),
        "title": title,
        "source": source,
        "material_type": args.material_type,
        "stage_id": args.stage_id or "未关联",
        "intake_mode": "script",
        "description": args.description or "待 Agent 或人工补充资料说明。",
    }
    write_rendered_template("material-intake.md", record_path, values, overwrite=args.overwrite)

    state = load_workbench_state(args.project)
    materials = state.setdefault("material_intake", [])
    materials = [item for item in materials if item.get("material_id") != material_id]
    materials.append(
        {
            "material_id": material_id,
            "title": title,
            "material_type": args.material_type,
            "stage_id": args.stage_id or "未关联",
            "source": source,
            "record": repo_relative(record_path),
            "status": "recorded",
            "recorded_at": utc_now(),
        }
    )
    state["material_intake"] = sorted(materials, key=lambda item: item.get("material_id", ""))
    index_path = update_index(args.project, state["material_intake"])
    state["material_intake_index"] = repo_relative(index_path)
    state["status"] = "material-intake-recorded"
    state["latest_material_intake_id"] = material_id
    save_workbench_state(args.project, state)

    print(f"Created material intake record: {record_path}")
    print(f"Updated material intake index: {index_path}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/record-material-intake/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Material id: {material_id}",
            f"Material source: {source}",
            f"Material record: {repo_relative(record_path)}",
            f"Material index: {repo_relative(index_path)}",
            "Analyze the material, update the material record, identify impacts, and suggest change requests if needed.",
            "Do not update lifecycle or stage plans until human confirms how the material should affect scope.",
        ],
        label=f"Record material intake {material_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
