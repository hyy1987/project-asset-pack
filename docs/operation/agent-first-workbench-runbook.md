# Agent-First 工作台运行手册

本手册描述 `project-asset-pack` 升级后的最小闭环。

## 目录约定

- 前期资料：`inputs/pre-project/<project_id>/`
- 示例前期资料：`examples/sample-project/pre-project/`
- AI 工作台输出：`outputs/generated/workbench/<project_id>/`
- 人工评审输出：`outputs/reviewed/workbench/<project_id>/`
- 工作台状态：`workspace/workbench/<project_id>/state.json`

## 最小流程

1. 放入前期资料。
2. 运行 `python scripts/init_project_workbench.py --project <project_id>`。
3. 人工确认 `info-alignment.md` 和 `project-kickoff-checklist.md`。
4. 运行 `python scripts/confirm_project_context.py --project <project_id> --decision confirmed`。
5. 运行 `python scripts/plan_project_stage.py --project <project_id> --stage-id stage-1 --title "第一阶段"`。
6. 人工确认阶段目标。
7. 运行 `python scripts/run_project_stage.py --project <project_id> --stage-id stage-1`。
8. 人工评审阶段报告。
9. 运行 `python scripts/review_project_stage.py --project <project_id> --stage-id stage-1 --decision approve`。
10. 项目结题或阶段性归档时，运行 `python scripts/finalize_workbench_asset_pack.py --project <project_id>`。
11. 运行 `python scripts/review_asset_pack.py --project <project_id>` 进行正式资产包评审定稿。

## 安全默认值

默认不修改业务项目仓库。需要 Agent 执行代码改动时，必须在项目配置中设置：

```yaml
workbench:
  allow_code_changes: true
```

同时阶段计划和人工授权必须明确允许本阶段修改代码。

## 离线验证

如果当前机器没有 Claude Code，先使用 `--no-claude` 验证目录、模板和状态推进：

```powershell
python scripts/check_project_config.py --project sample-project
python scripts/init_project_workbench.py --project sample-project --no-claude
python scripts/confirm_project_context.py --project sample-project --decision confirmed
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段" --no-claude
python scripts/run_project_stage.py --project sample-project --stage-id stage-1 --no-claude
python scripts/review_project_stage.py --project sample-project --stage-id stage-1 --decision approve --no-claude
python scripts/finalize_workbench_asset_pack.py --project sample-project --no-claude
python scripts/check_project_workbench.py --project sample-project
```
