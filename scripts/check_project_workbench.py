#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    generated_workbench_dir,
    list_material_files,
    load_workbench_state,
    pre_project_materials_dir,
    reviewed_workbench_dir,
    workbench_allows_code_changes,
    workbench_state_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Agent-First workbench files for one project.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    material_dir = pre_project_materials_dir(args.project)
    generated_dir = generated_workbench_dir(args.project)
    reviewed_dir = reviewed_workbench_dir(args.project)
    state_path = workbench_state_path(args.project)
    materials = list_material_files(args.project)

    print(f"Project: {args.project}")
    print(f"Pre-project materials: {material_dir}")
    print(f"Material files: {len(materials)}")
    print(f"Generated workbench: {generated_dir}")
    print(f"Reviewed workbench: {reviewed_dir}")
    print(f"State file: {state_path}")
    print(f"Config allows code changes: {workbench_allows_code_changes(args.project)}")

    state = load_workbench_state(args.project)
    status = state.get("status", "new")
    required = [
        generated_dir / "02-info-alignment.md",
        generated_dir / "03-project-kickoff-checklist.md",
        generated_dir / "04-responsibility-questions.md",
        generated_dir / "05-asset-pack-skeleton.md",
        generated_dir / "06-risk-action-list.md",
        state_path,
    ]
    if state.get("active_project_intake"):
        required.insert(0, generated_dir / "01-active-project-intake.md")
    if state.get("lifecycle_plan") or status in {
        "lifecycle-planned",
        "stage-planned",
        "stage-running",
        "stage-quality-checking",
        "stage-review-required",
        "stage-approved",
        "stage-experience-summarized",
        "asset-pack-draft-generated",
    }:
        required.append(generated_dir / "07-lifecycle-plan.md")

    missing = []
    for path in required:
        if not path.exists():
            missing.append(path)

    if missing:
        print("Missing workbench files:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(f"Workbench status: {state.get('status')}")
    print(f"Current stage: {state.get('current_stage_id')}")
    print("Workbench check passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

