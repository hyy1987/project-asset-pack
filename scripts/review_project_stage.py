#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from _common import (
    add_agent_argument,
    invoke_agent_skill,
    load_workbench_state,
    parse_quality_config,
    repo_relative,
    reviewed_workbench_dir,
    rule_candidates_path,
    save_workbench_state,
    selected_agent,
    stage_generated_dir,
    stage_reviewed_dir,
    utc_now,
    validate_quality_gate_file,
    validate_quality_command_results,
    validate_required_markdown,
    write_rendered_template,
)


VALID_DECISIONS = {"approve", "changes-requested", "blocked"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human review for an Agent-First project stage.")
    parser.add_argument("--project", required=True, help="Project id, for example sample-project")
    parser.add_argument("--stage-id", required=True, help="Stage id, for example stage-1")
    parser.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    parser.add_argument("--title", default="", help="Stage title; defaults to title recorded in workbench state.")
    add_agent_argument(parser)
    parser.add_argument("--skip-quality-gate", action="store_true", help="Allow approval without a completed quality gate. Use only with explicit human exception.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite reviewed scaffold files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = load_workbench_state(args.project)
    stage = state.get("stages", {}).get(args.stage_id, {})
    title = args.title or stage.get("title") or args.stage_id
    quality_gate_path = stage_generated_dir(args.project, args.stage_id) / "quality-gate.md"
    if args.decision == "approve" and not args.skip_quality_gate:
        stage_dir = stage_generated_dir(args.project, args.stage_id)
        quality_issues = []
        quality_issues.extend(validate_required_markdown(stage_dir / "stage-report.md", "Stage report"))
        quality_issues.extend(validate_required_markdown(stage_dir / "asset-pack-update.md", "Asset pack update"))
        quality_issues.extend(validate_quality_gate_file(quality_gate_path))
        quality_config = parse_quality_config(args.project)
        quality_results_required = bool(
            quality_config.get("commands")
            or quality_config.get("runtime")
            or quality_config.get("smoke")
        )
        quality_results_path = stage_dir / "quality-command-results.md"
        quality_issues.extend(validate_quality_command_results(quality_results_path, required=quality_results_required))
        if quality_issues:
            print("Cannot approve stage because quality gate is incomplete:")
            for issue in quality_issues:
                print(f"- {issue}")
            print("Fix quality gate, use decision changes-requested/blocked, or rerun with --skip-quality-gate for an explicit human exception.")
            return 1

    out_dir = stage_reviewed_dir(args.project, args.stage_id)
    values = {
        "project_id": args.project,
        "stage_id": args.stage_id,
        "stage_title": title,
        "generated_at": utc_now(),
        "decision": args.decision,
    }
    review_path = write_rendered_template("stage-review.md", out_dir / "stage-review.md", values, overwrite=args.overwrite)
    experience_path = write_rendered_template(
        "experience-notes.md",
        stage_generated_dir(args.project, args.stage_id) / "experience-notes.md",
        values,
        overwrite=args.overwrite,
    )

    state["status"] = "stage-approved" if args.decision == "approve" else "stage-review-required"
    state["current_stage_id"] = args.stage_id
    state.setdefault("stages", {}).setdefault(args.stage_id, {})
    state["stages"][args.stage_id].update(
        {
            "stage_id": args.stage_id,
            "title": title,
            "status": args.decision,
            "review": repo_relative(review_path),
            "experience_notes": repo_relative(experience_path),
            "reviewed_at": utc_now(),
        }
    )
    state["rule_candidates"] = repo_relative(rule_candidates_path(args.project))
    if args.decision == "approve":
        state["last_approved_stage_id"] = args.stage_id
        state["lifecycle_review_required"] = True
        state["lifecycle_review_reason"] = f"Stage {args.stage_id} approved; check whether later lifecycle stages need adjustment."
    save_workbench_state(args.project, state)

    reviewed_workbench_dir(args.project).mkdir(parents=True, exist_ok=True)
    print(f"Created stage review record: {review_path}")
    print(f"Created stage experience scaffold: {experience_path}")
    print(f"Decision: {args.decision}")

    agent = selected_agent(args)
    if agent == "none":
        return 0

    return invoke_agent_skill(
        agent,
        ".claude/skills/review-project-stage/SKILL.md",
        [
            f"Project id: {args.project}",
            f"Stage id: {args.stage_id}",
            f"Stage title: {title}",
            f"Human review decision: {args.decision}",
            f"Stage review output: {repo_relative(review_path)}",
            f"Stage experience output: {repo_relative(experience_path)}",
            "If the human review introduces new requirements, scope changes, or acceptance-criteria changes, record them as CRs instead of treating them as normal stage fixes.",
            "Stage approval covers the planned stage scope only; newly raised CRs still need triage and planning.",
        ],
        label=f"Review stage {args.stage_id} for {args.project}",
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
