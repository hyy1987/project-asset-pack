# Agent-First 工作台运行手册

本手册描述 `project-asset-pack` 升级后的最小闭环。

## 目录约定

- 前期资料：`inputs/pre-project/<project_id>/`
- 示例前期资料：`examples/sample-project/pre-project/`
- AI 工作台输出：`outputs/generated/workbench/<project_id>/`
- 人工评审输出：`outputs/reviewed/workbench/<project_id>/`
- 工作台状态：`workspace/workbench/<project_id>/state.json`
- 全周期规划：`outputs/generated/workbench/<project_id>/lifecycle-plan.md`
- 新窗口恢复摘要：`outputs/generated/workbench/<project_id>/resume-brief.md`

## 新窗口恢复

Agent 客户端的聊天窗口历史可能会丢失，但工作台进度不应该依赖聊天记录。

如果重新打开 Claude Code、Codex，或者换了一个新窗口，不要直接重新初始化。先运行：

```powershell
python scripts/resume_project_workbench.py --project <project_id>
```

这个命令会读取：

- `workspace/workbench/<project_id>/state.json`
- `outputs/reviewed/workbench/<project_id>/`
- `outputs/generated/workbench/<project_id>/`
- 当前阶段的计划、报告、资产包更新和评审记录

并生成：

```text
outputs/generated/workbench/<project_id>/resume-brief.md
```

新窗口中的 Agent 应先阅读 `resume-brief.md`，再决定继续阶段执行、进入阶段评审、修订全周期规划、规划下一阶段，还是进行阶段性归档。只有状态文件不存在，或人类明确要求重建，才重新初始化工作台。

## 最小流程

1. 放入前期资料。
2. 运行 `python scripts/init_project_workbench.py --project <project_id>`。
3. 人工确认 `info-alignment.md` 和 `project-kickoff-checklist.md`。
4. 运行 `python scripts/confirm_project_context.py --project <project_id> --decision confirmed`。
5. 运行 `python scripts/plan_project_lifecycle.py --project <project_id>`，生成项目全周期规划。
6. 运行 `python scripts/plan_project_stage.py --project <project_id> --stage-id stage-1 --title "第一阶段"`。
7. 人工确认阶段目标。
8. 运行 `python scripts/run_project_stage.py --project <project_id> --stage-id stage-1`。
9. 运行 `python scripts/check_stage_quality.py --project <project_id> --stage-id stage-1 --run-commands --validate --strict`，执行构建、测试、冒烟检查并检查质量门禁。
10. 人工评审阶段报告和质量门禁。
11. 运行 `python scripts/review_project_stage.py --project <project_id> --stage-id stage-1 --decision approve`。
12. 运行 `python scripts/summarize_stage_experience.py --project <project_id> --stage-id stage-1`，沉淀阶段经验。
13. 阶段通过后，检查并必要时修订全周期规划。
14. 基于最新全周期规划和项目经验库生成下一阶段计划。
15. 项目结题或阶段性归档时，运行 `python scripts/finalize_workbench_asset_pack.py --project <project_id>`。
16. 运行 `python scripts/review_asset_pack.py --project <project_id>` 进行正式资产包评审定稿。

默认工作方式是一个 Agent 作为阶段开发执行者。多人合作主要进入阶段计划确认、阶段评审和验收授权，不建议多个 Agent 终端同时推进同一阶段开发。

任意一步中断后，都可以先运行：

```powershell
python scripts/resume_project_workbench.py --project <project_id>
```

再继续后续步骤。

## 安全默认值

默认不修改业务项目仓库。需要 Agent 执行代码改动时，必须在项目配置中设置：

```yaml
workbench:
  allow_code_changes: true
```

同时阶段计划和人工授权必须明确允许本阶段修改代码。

## 离线验证

如果当前机器没有 Agent 客户端，或只想离线验证，先使用 `--agent none` 验证目录、模板和状态推进。离线模式不会自动补全阶段报告、资产包更新和质量门禁，因此示例用 `changes-requested` 模拟人工发现问题；不要把它当作阶段通过演示。

```powershell
python scripts/check_project_config.py --project sample-project
python scripts/init_project_workbench.py --project sample-project --agent none
python scripts/confirm_project_context.py --project sample-project --decision confirmed
python scripts/plan_project_lifecycle.py --project sample-project --agent none
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段" --agent none
python scripts/run_project_stage.py --project sample-project --stage-id stage-1 --agent none
python scripts/check_stage_quality.py --project sample-project --stage-id stage-1 --agent none --validate
python scripts/review_project_stage.py --project sample-project --stage-id stage-1 --decision changes-requested --agent none
python scripts/summarize_stage_experience.py --project sample-project --stage-id stage-1 --agent none
python scripts/resume_project_workbench.py --project sample-project --agent none --overwrite
python scripts/finalize_workbench_asset_pack.py --project sample-project --agent none
python scripts/check_project_workbench.py --project sample-project
```

如果要离线演示 `approve`，必须先人工补齐阶段报告、阶段资产包更新和质量门禁，并确保质量门禁明确允许进入人工评审；只有确有人工例外时才使用 `--skip-quality-gate`。
