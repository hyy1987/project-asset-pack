# 工作台归档为资产包初稿

用于项目结题或阶段性归档时，把工作台过程资料汇总成标准项目资产包初稿。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. 项目配置：`configs/projects/<project_id>.yaml`
3. 安全规则：`configs/security-rules/<rule_set>.md`
4. 工作台 AI 输出：`outputs/generated/workbench/`
5. 全周期规划：`outputs/generated/workbench/07-lifecycle-plan.md`
6. 工作台人工确认和阶段评审：`outputs/reviewed/workbench/`
7. 工作台状态：`workspace/workbench/state.json`
8. 标准资产包模板

## 输出

写入 `outputs/generated/asset-pack/`：

- `review-report.md`
- `asset-pack-draft.md`
- `missing-materials.md`
- `risk-list.md`
- `reusable-assets.md`
- `workbench-archive-summary.md`

## 规则

1. 以人工确认和阶段评审结果为最高优先级。
2. AI 阶段报告只能作为证据和素材，不能直接写成已确认事实。
3. 已通过人工评审的阶段内容，可以作为“已确认过程记录”引用。
4. 未评审或评审未通过的阶段，必须标记为“待确认”。
5. 风险、资料缺口、测试结果、部署交接、可复用资产必须从阶段报告、资产包更新、人工评审记录中归纳。
6. 必须把全周期规划作为交付范围、阶段路线和里程碑的上位依据。
7. 不得输出敏感原文。
8. 不得编造未在工作台过程资料中出现的内容。
9. 归档结果仍是 AI 初稿，必须经过人工资产包评审后才能定稿。

