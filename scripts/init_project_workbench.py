#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    ensure_workbench_dirs,
    generated_workbench_dir,
    invoke_agent_skill,
    list_material_files,
    load_workbench_state,
    pre_project_materials_dir,
    project_security_rule_set,
    repo_relative,
    save_workbench_state,
    selected_agent,
    utc_now,
    write_rendered_template,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize Agent-First project workbench outputs.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    add_agent_argument(parser)
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_workbench_dirs(args.project)
    out_dir = generated_workbench_dir(args.project)
    material_dir = pre_project_materials_dir(args.project)
    materials = list_material_files(args.project)
    values = {
        "project_id": args.project,
        "generated_at": utc_now(),
        "material_list": "\n".join(f"- {item}" for item in materials) if materials else "- 未发现前期资料。",
    }

    created = [
        write_rendered_template("info-alignment.md", out_dir / "info-alignment.md", values, overwrite=args.overwrite),
        write_rendered_template("project-kickoff-checklist.md", out_dir / "project-kickoff-checklist.md", values, overwrite=args.overwrite),
        write_rendered_template("responsibility-questions.md", out_dir / "responsibility-questions.md", values, overwrite=args.overwrite),
        write_rendered_template("asset-pack-skeleton.md", out_dir / "asset-pack-skeleton.md", values, overwrite=args.overwrite),
        write_rendered_template("risk-action-list.md", out_dir / "risk-action-list.md", values, overwrite=args.overwrite),
    ]

    state = load_workbench_state(args.project)
    state["status"] = "initialized"
    state["pre_project_materials"] = repo_relative(material_dir)
    state["generated_outputs"] = [repo_relative(path) for path in created]
    save_workbench_state(args.project, state)

    print(f"Initialized workbench scaffold: {out_dir}")
    print(f"Pre-project materials: {material_dir}")
    if materials:
        print("Detected pre-project material files:")
        for item in materials:
            print(f"- {item}")
    else:
        print("No pre-project material files detected yet.")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/init-project-workbench/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Security rule set: {project_security_rule_set(args.project)}",
            f"Pre-project material directory: {material_dir}",
            f"Generated workbench directory: outputs/generated/workbench/{args.project}/",
            "Generate or update info alignment, kickoff checklist, responsibility questions, asset pack skeleton, and risk/action list.",
        ],
        label=f"Initialize Agent-First workbench for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
