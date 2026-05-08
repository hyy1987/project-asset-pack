#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    generated_workbench_dir,
    invoke_agent_skill,
    load_workbench_state,
    project_experience_path,
    repo_relative,
    rule_candidates_path,
    save_workbench_state,
    selected_agent,
    stage_generated_dir,
    stage_reviewed_dir,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize stage experience into project experience records.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated experience scaffold.")
    return parser.parse_args()


def ensure_project_experience(project_id: str) -> str:
    path = project_experience_path(project_id)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# 项目经验库\n\n项目 ID：{project_id}\n\n用于记录后续阶段必须读取和遵守的项目经验。不要写聊天流水账，只记录可执行规则。\n",
            encoding="utf-8",
        )
    return repo_relative(path)


def ensure_rule_candidates(project_id: str) -> str:
    path = rule_candidates_path(project_id)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# 长期规则候选\n\n项目 ID：{project_id}\n\n这里记录可能适合沉淀到通用 workflow 的规则候选，必须经过人工确认后才能升级为长期规则。\n",
            encoding="utf-8",
        )
    return repo_relative(path)


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
    experience_path = write_rendered_template("experience-notes.md", out_dir / "experience-notes.md", values, overwrite=args.overwrite)
    project_experience = ensure_project_experience(args.project)
    rule_candidates = ensure_rule_candidates(args.project)

    state["status"] = "stage-experience-summarized"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": title,
            "experience_notes": repo_relative(experience_path),
            "experience_updated_at": utc_now(),
        }
    )
    state["project_experience"] = project_experience
    state["rule_candidates"] = rule_candidates
    save_workbench_state(args.project, state)
    print(f"Created stage experience scaffold: {experience_path}")
    print(f"Project experience file: {project_experience}")
    print(f"Rule candidates file: {rule_candidates}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/summarize-stage-experience/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Stage report: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/stage-report.md",
            f"Quality gate: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/quality-gate.md",
            f"Stage review: outputs/reviewed/workbench/{args.project}/stages/{args.stage_id}/stage-review.md",
            f"Stage experience output: outputs/generated/workbench/{args.project}/stages/{args.stage_id}/experience-notes.md",
            f"Project experience file: {project_experience}",
            f"Rule candidates file: {rule_candidates}",
        ],
        label=f"Summarize stage experience for {args.project} {args.stage_id}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
