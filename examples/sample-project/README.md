# sample-project 测试材料

这是一个用于验证 Agent-First 工作台流程的示例项目材料。

当前示例重点验证新项目启动阶段：

- 前期资料读取
- 信息对齐稿生成
- 项目启动清单生成
- 责任视角问题清单生成
- 资产包骨架生成
- 风险与行动清单生成

示例不会包含真实客户数据、账号、密钥、合同金额或生产环境信息。

## 使用方式

`configs/projects/sample-project.yaml` 已经把前期资料目录指向：

```text
examples/sample-project/pre-project
```

可以直接运行：

```powershell
python scripts/init_project_workbench.py --project sample-project
```

离线验证：

```powershell
python scripts/init_project_workbench.py --project sample-project --agent none --overwrite
```

## 在 VS Code 中使用 Agent 客户端

1. 用 VS Code 打开 `project-asset-pack` 目录。

2. 如果使用 Claude Code，确认本地配置文件存在：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

如果已经存在 `.claude/settings.local.json`，不要覆盖，按需确认里面包含：

```json
{
  "additionalDirectories": [
    "../sample-project/backend",
    "../sample-project/frontend",
    "../sample-project/database",
    "../sample-project/docs",
    "examples/sample-project/pre-project"
  ]
}
```

3. 在 VS Code 终端进入工作台根目录：

```powershell
cd project-asset-pack
```

4. 先做配置检查：

```powershell
python scripts/check_project_config.py --project sample-project
```

`sample-project` 使用占位代码仓库路径，缺失路径会以 warning 形式提示；这不影响前期资料工作台流程验证。

5. 启动 Agent 客户端。

Claude Code：

```powershell
claude
```

Codex：

```powershell
codex
```

6. 在 Claude Code 或 Codex 会话中执行新项目工作台初始化：

```text
请按 docs/agent-workflows/init-project-workbench.md 的规则，基于 configs/projects/sample-project.yaml 和 examples/sample-project/pre-project 生成 sample-project 的工作台初始化输出。
```

如果使用 Claude Code，也可以使用快捷命令：

```text
/init-project-workbench sample-project
```

7. 查看输出目录：

```text
outputs/generated/workbench/sample-project/
```

重点检查：

- `info-alignment.md`
- `project-kickoff-checklist.md`
- `responsibility-questions.md`
- `asset-pack-skeleton.md`
- `risk-action-list.md`

8. 人工确认项目信息：

```powershell
python scripts/confirm_project_context.py --project sample-project --decision confirmed
```

9. 生成全周期规划：

```powershell
python scripts/plan_project_lifecycle.py --project sample-project
```

或在 Agent 会话中输入：

```text
请按 docs/agent-workflows/plan-project-lifecycle.md 的规则，为 sample-project 生成全周期规划。
```

10. 生成第一阶段计划：

```powershell
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段"
```

或在 Agent 会话中输入：

```text
请按 docs/agent-workflows/plan-project-stage.md 的规则，为 sample-project 生成 stage-1 阶段计划，阶段标题为“第一阶段”。
```

11. 离线检查工作台状态：

```powershell
python scripts/check_project_workbench.py --project sample-project
```

## 离线验证命令

如果只是验证目录、模板和状态推进，不需要调用 Agent 客户端，可以直接运行：

```powershell
python scripts/init_project_workbench.py --project sample-project --agent none --overwrite
python scripts/confirm_project_context.py --project sample-project --decision confirmed --overwrite
python scripts/plan_project_lifecycle.py --project sample-project --agent none --overwrite
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段" --agent none --overwrite
python scripts/run_project_stage.py --project sample-project --stage-id stage-1 --agent none --overwrite
python scripts/check_stage_quality.py --project sample-project --stage-id stage-1 --agent none --overwrite
python scripts/review_project_stage.py --project sample-project --stage-id stage-1 --decision approve --agent none --overwrite
python scripts/summarize_stage_experience.py --project sample-project --stage-id stage-1 --agent none --overwrite
python scripts/finalize_workbench_asset_pack.py --project sample-project --agent none --overwrite
python scripts/check_project_workbench.py --project sample-project
```
