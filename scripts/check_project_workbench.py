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

    missing = []
    for path in [
        generated_dir / "info-alignment.md",
        generated_dir / "project-kickoff-checklist.md",
        generated_dir / "responsibility-questions.md",
        generated_dir / "asset-pack-skeleton.md",
        generated_dir / "risk-action-list.md",
        generated_dir / "lifecycle-plan.md",
        state_path,
    ]:
        if not path.exists():
            missing.append(path)

    if missing:
        print("Missing workbench files:")
        for path in missing:
            print(f"- {path}")
        return 1

    state = load_workbench_state(args.project)
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
