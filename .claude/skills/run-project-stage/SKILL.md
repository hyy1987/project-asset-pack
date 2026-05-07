---
name: run-project-stage
description: 按阶段计划执行 Agent 阶段开发、自检、测试、资产包更新，并生成阶段报告。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash
---

# run-project-stage

用于让 Agent 按阶段推进开发过程。

## 推荐触发方式

```powershell
python scripts\run_project_stage.py --project <project_id> --stage-id <stage_id>
```

如果需要修改业务项目仓库，必须同时满足：

1. `configs/projects/<project_id>.yaml` 中 `workbench.allow_code_changes: true`。
2. 阶段计划中明确允许本阶段修改代码。
3. 人类在当前会话或评审记录中明确授权。

## 输入

1. 项目配置和安全规则。
2. 已确认的项目信息或人工确认记录。
3. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`
4. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-plan.md`
5. 已接入的业务项目仓库和资料目录。
6. `templates/workbench/stage-report.md`

## 输出

写入：

```text
outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-report.md
outputs/generated/workbench/<project_id>/stages/<stage_id>/asset-pack-update.md
```

必要时更新业务项目仓库中的代码，但必须遵守授权条件。

## 执行流程

1. 读取阶段计划和已确认上下文。
2. 检查是否存在阻塞性待确认问题。
3. 如未获授权修改代码，只生成执行建议和待确认问题，不改业务仓库。
4. 如已获授权，按阶段计划拆解执行步骤并实施；默认由一个 Agent 会话推进本阶段开发。
5. 运行可用的自检、测试、类型检查或构建命令；无法运行时说明原因。
6. 更新阶段资产包摘要。
7. 生成阶段报告，列出变更、测试结果、风险、待评审事项和下一步建议。
8. 不得绕过人工评审进入下一阶段。
9. 不建议多个 Agent 终端同时推进同一阶段开发；多人主要在计划确认和阶段评审时进入。

