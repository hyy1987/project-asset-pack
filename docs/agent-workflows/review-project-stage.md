# 评审阶段结果

用于把阶段开发结果推进到人工评审记录，并决定是否允许继续推进后续规划。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `outputs/generated/workbench/07-lifecycle-plan.md`
3. `outputs/generated/workbench/stages/<stage_id>/stage-plan.md`
4. `outputs/generated/workbench/stages/<stage_id>/stage-report.md`
5. `outputs/generated/workbench/stages/<stage_id>/quality-gate.md`
6. 人工评审意见，默认从 `docs/manual/stage-reviews/<project_id>/<stage_id>.md` 读取
7. `templates/workbench/stage-review.md`
8. `templates/workbench/experience-notes.md`

## 输出

写入：

```text
outputs/reviewed/workbench/stages/<stage_id>/stage-review.md
outputs/generated/workbench/stages/<stage_id>/experience-notes.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. AI 阶段报告不能直接视为通过。
2. 必须记录评审结论：`approve`、`changes-requested` 或 `blocked`。
3. 评审前必须读取质量门禁；如果门禁为 `block`，不得建议通过。
4. `approve` 后不直接进入下一阶段，必须先沉淀阶段经验，并检查全周期规划是否需要调整。
5. 后续阶段计划必须基于最新 `07-lifecycle-plan.md` 和项目经验库生成。
6. `changes-requested` 必须列出返工要求，并沉淀为经验候选。
7. `blocked` 必须列出阻塞原因和需要谁确认，并沉淀为经验候选。
8. 不得把未确认内容写成已确认事实。
9. 如果人工评审意见包含超出原阶段计划的新需求、范围变化或验收标准变化，先记录 CR；评审记录只说明该 CR 的处理建议，不得直接把它当成本阶段已确认返工项。
10. `approve` 只代表原阶段目标通过，不代表评审中新增的 CR 自动通过。
