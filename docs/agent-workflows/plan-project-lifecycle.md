# 生成或修订项目全周期规划

用于在信息对齐和人工确认之后，生成或修订项目全周期规划。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `outputs/generated/workbench/info-alignment.md`
4. `outputs/generated/workbench/project-kickoff-checklist.md`
5. `outputs/generated/workbench/risk-action-list.md`
6. `outputs/reviewed/workbench/human-confirmation.md`，如果存在
7. 已有 `outputs/generated/workbench/lifecycle-plan.md`，如果是修订
8. `outputs/generated/workbench/material-intake/index.md`，如果存在
9. `outputs/generated/workbench/change-requests/index.md`，如果存在
10. 已有阶段报告和阶段评审记录，如果是阶段后修订
11. `templates/workbench/lifecycle-plan.md`

## 输出

写入或更新：

```text
outputs/generated/workbench/lifecycle-plan.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 给出项目全周期目标、交付范围、非交付范围和关键假设。
2. 必须规划完整阶段路线图，不只规划第一期。
3. 每个阶段写清阶段目标、主要产物、人工评审点和进入下一阶段条件。
4. 未知内容标注“待人工确认”。
5. 不得绕过人工评审把后续阶段视为已授权。
6. 如果是修订规划，说明修订原因、影响范围和后续阶段变化。
7. 后续阶段计划必须服从最新全周期规划。
8. 已人工确认进入后续阶段的 CR 必须进入全周期规划；未确认 CR 只能作为待评审候选。
