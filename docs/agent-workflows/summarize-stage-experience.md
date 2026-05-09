# 沉淀阶段经验

用于在阶段评审后，把阶段报告、质量门禁、人工评审意见和聊天修正提炼为可复用的项目经验。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `outputs/generated/workbench/stages/<stage_id>/stage-report.md`
3. `outputs/generated/workbench/stages/<stage_id>/quality-gate.md`
4. `outputs/reviewed/workbench/stages/<stage_id>/stage-review.md`
5. `workspace/workbench/project-experience.md`，如果存在
6. `outputs/generated/workbench/rule-candidates.md`，如果存在
7. `templates/workbench/experience-notes.md`

## 输出

写入或更新：

```text
outputs/generated/workbench/stages/<stage_id>/experience-notes.md
workspace/workbench/project-experience.md
outputs/generated/workbench/rule-candidates.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 不总结聊天流水账，只提炼可复用经验。
2. 优先记录三类内容：人类反复提醒的质量要求、Agent 本阶段实际遗漏的问题、后续阶段必须遵守的项目约束。
3. 每条经验必须说明来源阶段、触发背景、Agent 遗漏点、后续规则和适用范围。
4. 项目经验库用于后续阶段计划和阶段执行，必须短、具体、可执行。
5. 适合跨项目复用的经验进入 `rule-candidates.md`，等待人工确认后再进入通用 workflow。
6. 不得把未经人工确认的推断写成长期规则。
7. 如果阶段评审为 `changes-requested` 或 `blocked`，必须把返工原因沉淀为经验候选。
