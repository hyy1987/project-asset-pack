# 执行阶段开发

用于让一个 Agent 按阶段计划推进开发、自检、测试、资产包更新，并生成阶段报告。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. 项目配置和安全规则
3. 已确认的项目信息或人工确认记录
4. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`
5. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-plan.md`
6. 已接入的业务项目仓库和资料目录
7. `templates/workbench/stage-report.md`

## 输出

写入：

```text
outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-report.md
outputs/generated/workbench/<project_id>/stages/<stage_id>/asset-pack-update.md
```

必要时更新业务项目仓库中的代码，但必须遵守授权条件。

## 规则

1. 默认由一个 Agent 会话推进本阶段开发。
2. 读取全周期规划、阶段计划和已确认上下文。
3. 检查是否存在阻塞性待确认问题。
4. 未获授权修改代码时，只生成执行建议和待确认问题，不改业务仓库。
5. 获授权后，按阶段计划拆解执行步骤并实施。
6. 运行可用的自检、测试、类型检查或构建命令；无法运行时说明原因。
7. 更新阶段资产包摘要。
8. 生成阶段报告，列出变更、测试结果、风险、待评审事项和下一步建议。
9. 不得绕过人工评审进入下一阶段。
10. 不建议多个 Agent 终端同时推进同一阶段开发；多人主要在计划确认和阶段评审时进入。
