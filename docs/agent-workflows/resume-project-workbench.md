# 恢复项目工作台上下文

用于新窗口、上下文丢失或中途恢复后继续同一个项目。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `workspace/workbench/state.json`
4. `outputs/reviewed/workbench/`
5. `outputs/generated/workbench/07-lifecycle-plan.md`
6. `outputs/generated/workbench/`
7. 当前阶段的 `stage-plan.md`、`stage-report.md`、`asset-pack-update.md`
8. 当前阶段的 `quality-gate.md` 和 `experience-notes.md`，如果存在
9. `workspace/workbench/project-experience.md`，如果存在
10. `outputs/generated/workbench/00-resume-brief.md`

## 输出

更新或生成：

```text
outputs/generated/workbench/00-resume-brief.md
```

## 规则

1. 如果状态文件存在，不要重新初始化。
2. 优先相信 `outputs/reviewed/workbench/` 中的人工确认和评审记录。
3. `outputs/generated/` 中的内容只视为 AI 初稿。
4. 明确告诉用户当前状态、当前阶段、已有产物、缺口和下一步建议。
5. 如果全周期规划缺失，优先建议生成全周期规划。
6. 如果阶段执行完成但质量门禁缺失，优先建议补做质量门禁。
7. 如果阶段通过评审但经验沉淀缺失，优先建议沉淀阶段经验。
8. 如果阶段通过评审，先建议检查并必要时修订全周期规划，再规划下一阶段或归档。

