# 执行阶段开发

用于让一个 Agent 按阶段计划推进开发、自检、测试、资产包更新，并生成阶段报告。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. 项目配置和安全规则
3. 已确认的项目信息或人工确认记录
4. `outputs/generated/workbench/07-lifecycle-plan.md`
5. `outputs/generated/workbench/stages/<stage_id>/stage-plan.md`
6. `outputs/generated/workbench/material-intake/index.md`，如果存在
7. `outputs/generated/workbench/change-requests/index.md`，如果存在
8. `workspace/workbench/project-experience.md`，如果存在
9. 已接入的业务项目仓库和资料目录
10. `templates/workbench/stage-report.md`
11. `templates/workbench/quality-gate.md`

## 输出

写入：

```text
outputs/generated/workbench/stages/<stage_id>/stage-report.md
outputs/generated/workbench/stages/<stage_id>/asset-pack-update.md
outputs/generated/workbench/stages/<stage_id>/quality-gate.md
```

必要时更新业务项目仓库中的代码，但必须遵守授权条件。

## 规则

1. 默认由一个 Agent 会话推进本阶段开发。
2. 读取全周期规划、阶段计划和已确认上下文。
3. 读取项目经验库，检查本阶段是否存在禁止重复的问题。
4. 检查是否存在阻塞性待确认问题。
5. 未获授权修改代码时，只生成执行建议和待确认问题，不改业务仓库。
6. 获授权后，按阶段计划拆解执行步骤并实施。
7. 运行可用的自检、测试、类型检查或构建命令；无法运行时说明原因。
8. 更新阶段资产包摘要。
9. 生成阶段报告，列出变更、测试结果、风险、待评审事项和下一步建议。
10. 同步生成或更新阶段质量门禁，明确测试证据、未验证内容和人工必须检查项。
11. 不得绕过质量门禁和人工评审进入下一阶段。
12. 不建议多个 Agent 终端同时推进同一阶段开发；多人主要在计划确认和阶段评审时进入。
13. 不得实现未纳入阶段计划的 CR；如执行中出现新需求，先记录 CR，再等待人工确认是否调整阶段计划。
14. 阶段执行中如果用户直接提出“顺便加一个”“这里改成”“验收时还要”等新要求，先暂停对应实现，按 `record-change-request.md` 记录 CR。
15. 只有 CR 状态为 `accepted-current-stage`，并且阶段计划、质量门禁检查项已经同步更新后，才能在本阶段实现。
