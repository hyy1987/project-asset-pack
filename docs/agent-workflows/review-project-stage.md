# 评审阶段结果

用于把阶段开发结果推进到人工评审记录，并决定是否允许继续推进后续规划。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`
3. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-plan.md`
4. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-report.md`
5. 人工评审意见，默认从 `docs/manual/stage-reviews/<project_id>/<stage_id>.md` 读取
6. `templates/workbench/stage-review.md`

## 输出

写入：

```text
outputs/reviewed/workbench/<project_id>/stages/<stage_id>/stage-review.md
```

更新 `workspace/workbench/<project_id>/state.json`。

## 规则

1. AI 阶段报告不能直接视为通过。
2. 必须记录评审结论：`approve`、`changes-requested` 或 `blocked`。
3. `approve` 后不直接进入下一阶段，必须先检查全周期规划是否需要调整。
4. 后续阶段计划必须基于最新 `lifecycle-plan.md` 生成。
5. `changes-requested` 必须列出返工要求。
6. `blocked` 必须列出阻塞原因和需要谁确认。
7. 不得把未确认内容写成已确认事实。
