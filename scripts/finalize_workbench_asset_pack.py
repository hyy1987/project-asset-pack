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
    workbench_state_path,
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
                f"- 闃舵 ID锛歿stage_id}",
                f"  - 鍚嶇О锛歿stage.get('title', '寰呯‘璁?)}",
                f"  - 鐘舵€侊細{stage.get('status', '寰呯‘璁?)}",
                f"  - 璁″垝锛歿stage.get('plan', '寰呯‘璁?)}",
                f"  - 鎶ュ憡锛歿stage.get('report', '寰呯‘璁?)}",
                f"  - 璐ㄩ噺闂ㄧ锛歿stage.get('quality_gate', '寰呯‘璁?)}",
                f"  - 璇勫锛歿stage.get('review', '寰呯‘璁?)}",
                f"  - 闃舵缁忛獙锛歿stage.get('experience_notes', '寰呯‘璁?)}",
            ]
        )
    archive_summary = f"""# 宸ヤ綔鍙扮粨棰樺綊妗ｆ憳瑕?

椤圭洰锛歿project_name}

椤圭洰 ID锛歿args.project}

鐢熸垚鏃堕棿锛歿utc_now()}

## 宸ヤ綔鍙扮姸鎬?

- 褰撳墠鐘舵€侊細{state.get('status', '寰呯‘璁?)}
- 褰撳墠闃舵锛歿state.get('current_stage_id', '寰呯‘璁?)}
- 鏈€杩戦€氳繃闃舵锛歿state.get('last_approved_stage_id', '寰呯‘璁?)}
- 鍏ㄥ懆鏈熻鍒掞細{state.get('lifecycle_plan', '寰呯‘璁?)}
- 椤圭洰缁忛獙搴擄細{state.get('project_experience', '寰呯‘璁?)}
- 闀挎湡瑙勫垯鍊欓€夛細{state.get('rule_candidates', '寰呯‘璁?)}

## 鍓嶆湡璧勬枡

{chr(10).join(f'- {item}' for item in list_material_files(args.project)) or '- 鏈彂鐜板墠鏈熻祫鏂欍€?}

## 宸ヤ綔鍙拌緭鍏ヨ緭鍑?

- 宸ヤ綔鍙?AI 杈撳嚭锛歿repo_relative(workbench_generated)}
- 宸ヤ綔鍙颁汉宸ョ‘璁や笌璇勫锛歿repo_relative(workbench_reviewed)}
- 宸ヤ綔鍙扮姸鎬佹枃浠讹細{repo_relative(workbench_state_path(args.project))}
- 鍏ㄥ懆鏈熻鍒掓枃浠讹細{state.get('lifecycle_plan', '寰呯‘璁?)}
- 椤圭洰缁忛獙搴擄細{state.get('project_experience', '寰呯‘璁?)}
- 闀挎湡瑙勫垯鍊欓€夛細{state.get('rule_candidates', '寰呯‘璁?)}

## 闃舵璁板綍

{chr(10).join(stage_lines) if stage_lines else '- 鏈彂鐜伴樁娈佃褰曘€?}

## 褰掓。璇存槑

鏈憳瑕佺敤浜庢妸宸ヤ綔鍙拌繃绋嬭祫鏂欐眹鎬讳负鏍囧噯椤圭洰璧勪骇鍖呭垵绋裤€傚綊妗ｇ粨鏋滀粛涓?AI 鍒濈锛屽繀椤荤粡杩囦汉宸ヨ瘎瀹″悗鎵嶈兘瀹氱銆?
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
