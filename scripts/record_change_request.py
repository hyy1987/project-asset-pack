#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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


VALID_STATUSES = {
    "new",
    "triaged",
    "needs-clarification",
    "accepted-current-stage",
    "accepted-future-stage",
    "rejected",
    "done",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a client request or requirement change into the workbench change queue.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--request-id", default="", help="Request id, for example CR-2026-001. Defaults to next id.")
    parser.add_argument("--title", required=True, help="Change request title.")
    parser.add_argument("--source", default="", help="Source material id, material record, meeting, or chat note.")
    parser.add_argument("--material-id", default="", help="Related material intake id, for example MI-2026-001.")
    parser.add_argument("--stage-id", default="", help="Stage where the request was raised or may affect.")
    parser.add_argument("--target-stage", default="", help="Target stage after triage.")
    parser.add_argument(
        "--request-type",
        default="new-requirement",
        choices=("new-requirement", "requirement-change", "scope-change", "bug", "clarification", "other"),
    )
    parser.add_argument("--priority", default="medium", choices=("low", "medium", "high", "urgent"))
    parser.add_argument("--status", default="new", choices=sorted(VALID_STATUSES))
    parser.add_argument("--description", default="", help="Original request description.")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing change request record.")
    return parser.parse_args()


def request_dir(project_id: str) -> Path:
    return generated_workbench_dir(project_id) / "change-requests"


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


def next_request_id(project_id: str) -> str:
    root = request_dir(project_id)
    year = utc_now()[:4]
    prefix = f"CR-{year}"
    number = max(existing_ids(root, prefix), default=0) + 1
    return f"{prefix}-{number:03d}"


def update_index(project_id: str, requests: list[dict[str, str]]) -> Path:
    root = request_dir(project_id)
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 需求变更队列",
        "",
        f"项目 ID：{project_id}",
        f"更新时间：{utc_now()}",
        "",
        "## 状态说明",
        "",
        "- `new`：新记录，尚未评审。",
        "- `triaged`：已初步归类，但尚未进入阶段计划。",
        "- `needs-clarification`：需要甲方或内部进一步确认。",
        "- `accepted-current-stage`：已确认进入当前阶段，必须更新阶段计划和质量门禁。",
        "- `accepted-future-stage`：已确认进入后续阶段，必须更新全周期规划。",
        "- `rejected`：不纳入交付范围。",
        "- `done`：已完成并通过评审。",
        "",
        "| CR ID | 标题 | 类型 | 优先级 | 状态 | 影响阶段 | 目标阶段 | 来源 | 记录 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for item in requests:
        lines.append(
            "| {request_id} | {title} | {request_type} | {priority} | {status} | {stage_id} | {target_stage} | {source} | {record} |".format(
                request_id=item.get("request_id", ""),
                title=item.get("title", ""),
                request_type=item.get("request_type", ""),
                priority=item.get("priority", ""),
                status=item.get("status", "new"),
                stage_id=item.get("stage_id", "未关联"),
                target_stage=item.get("target_stage", "待评审"),
                source=item.get("source", ""),
                record=item.get("record", ""),
            )
        )
    if not requests:
        lines.append("| 待记录 | 待补充 | 待确认 | 待确认 | new | 待确认 | 待评审 | 待确认 | 待确认 |")
    path = root / "index.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    request_id = args.request_id or next_request_id(args.project)
    root = request_dir(args.project)
    record_path = root / f"{request_id}.md"
    values = {
        "project_id": args.project,
        "request_id": request_id,
        "generated_at": utc_now(),
        "title": args.title,
        "source": args.source or "聊天补充或待关联资料",
        "material_id": args.material_id or "未关联",
        "stage_id": args.stage_id or "未关联",
        "request_type": args.request_type,
        "priority": args.priority,
        "status": args.status,
        "target_stage": args.target_stage or "待评审",
        "description": args.description or "待 Agent 或人工补充原始需求描述。",
    }
    write_rendered_template("change-request.md", record_path, values, overwrite=args.overwrite)

    state = load_workbench_state(args.project)
    requests = state.setdefault("change_requests", [])
    requests = [item for item in requests if item.get("request_id") != request_id]
    requests.append(
        {
            "request_id": request_id,
            "title": args.title,
            "request_type": args.request_type,
            "priority": args.priority,
            "status": args.status,
            "stage_id": args.stage_id or "未关联",
            "target_stage": args.target_stage or "待评审",
            "source": args.source or args.material_id or "聊天补充",
            "material_id": args.material_id or "",
            "record": repo_relative(record_path),
            "recorded_at": utc_now(),
        }
    )
    state["change_requests"] = sorted(requests, key=lambda item: item.get("request_id", ""))
    index_path = update_index(args.project, state["change_requests"])
    state["change_request_index"] = repo_relative(index_path)
    state["status"] = "change-request-recorded"
    state["latest_change_request_id"] = request_id
    state["lifecycle_review_required"] = True
    state["lifecycle_review_reason"] = f"Change request {request_id} recorded; triage before updating lifecycle or stage plans."
    save_workbench_state(args.project, state)

    print(f"Created change request record: {record_path}")
    print(f"Updated change request index: {index_path}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/record-change-request/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Change request id: {request_id}",
            f"Change request record: {repo_relative(record_path)}",
            f"Change request index: {repo_relative(index_path)}",
            "Analyze impact and keep the request in the queue until a human confirms status and target stage.",
            "Do not implement the request directly from this record.",
        ],
        label=f"Record change request {request_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
