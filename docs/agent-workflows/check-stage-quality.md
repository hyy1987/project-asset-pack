# 检查阶段质量门禁

用于在阶段执行完成后、人工评审前，检查阶段结果是否具备进入人工评审的最低质量。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `workspace/workbench/project-experience.md`，如果存在
4. `outputs/generated/workbench/lifecycle-plan.md`
5. `outputs/generated/workbench/stages/<stage_id>/stage-plan.md`
6. `outputs/generated/workbench/stages/<stage_id>/stage-report.md`
7. `outputs/generated/workbench/stages/<stage_id>/asset-pack-update.md`
8. `templates/workbench/quality-gate.md`
9. `outputs/generated/workbench/stages/<stage_id>/quality-command-results.md`，如果已执行质量命令

## 输出

写入：

```text
outputs/generated/workbench/stages/<stage_id>/quality-gate.md
outputs/generated/workbench/stages/<stage_id>/quality-command-results.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 质量门禁必须在人工评审前完成。
2. 没有阶段报告时，不允许通过门禁。
3. 没有测试或验证证据时，默认不允许通过门禁，除非明确说明无法测试的原因和人工补偿检查方式。
4. 必须检查核心路径、失败路径、边界输入、权限约束、数据影响、前端状态、日志和错误提示。
5. 必须读取项目经验库，检查本阶段是否重复出现已记录问题。
6. 必须列出未验证内容，不得把未验证结果写成已完成。
7. 如果业务仓库发生代码变更，必须列出已执行的测试、构建或类型检查命令。
8. 必须检查阶段资产包更新是否同步需求、方案、接口、数据模型、测试结果和风险变化。
9. 门禁结论只能是：`pass`、`warning` 或 `block`。
10. `block` 时不得建议进入人工通过评审，只能建议返工或补充验证。
11. 如果配置了 `quality.commands`、`quality.runtime` 或 `quality.smoke`，必须读取命令执行结果；命令、启动检查或冒烟检查失败时门禁不得为 `pass`。
