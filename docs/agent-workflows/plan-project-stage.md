# 生成阶段计划

用于基于已确认上下文和全周期规划生成阶段计划。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `outputs/generated/workbench/02-info-alignment.md`
4. `outputs/generated/workbench/03-project-kickoff-checklist.md`
5. `outputs/generated/workbench/07-lifecycle-plan.md`
6. `outputs/reviewed/workbench/human-confirmation.md`，如果存在
7. `outputs/generated/workbench/material-intake/index.md`，如果存在
8. `outputs/generated/workbench/change-requests/index.md`，如果存在
9. `workspace/workbench/project-experience.md`，如果存在
10. `templates/workbench/stage-plan.md`

## 输出

写入：

```text
outputs/generated/workbench/stages/<stage_id>/stage-plan.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 阶段计划必须服从 `07-lifecycle-plan.md`。
2. 说明本阶段在全周期规划中的位置。
3. 阶段目标必须可评审。
4. 阶段边界必须写清“做”和“不做”。
5. 列出执行前需要人类确认的问题。
6. 列出 Agent 执行步骤、自检与测试要求、阶段交付物。
7. 默认不允许直接修改业务仓库，除非项目配置和人工确认明确允许。
8. 如果全周期规划缺失或过期，先要求生成或修订全周期规划。
9. 如果项目经验库存在，必须把相关经验转成本阶段质量要求、测试要求和禁止重复的问题。
10. 只有人工确认进入本阶段的 CR 才能纳入阶段计划；未确认 CR 只能列为待评审或后续候选。
11. 阶段计划必须列出本阶段纳入的 CR 编号；如果没有，明确写“无已确认纳入本阶段的 CR”。
12. 如果存在 `new`、`triaged`、`needs-clarification` 状态的 CR，不得默认为本阶段任务，只能列入待确认问题或后续候选。
