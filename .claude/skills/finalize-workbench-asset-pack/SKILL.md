---
name: finalize-workbench-asset-pack
description: 基于 Agent-First 工作台过程资料和阶段评审结果，生成标准项目资产包初稿。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# finalize-workbench-asset-pack

用于项目结题或阶段性归档时，把工作台过程资料汇总成标准项目资产包初稿。

## 推荐触发方式

```powershell
python scripts\finalize_workbench_asset_pack.py --project <project_id>
```

## 输入

1. 项目配置：`configs/projects/<project_id>.yaml`
2. 安全规则：`configs/security-rules/<rule_set>.md`
3. 工作台 AI 输出：`outputs/generated/workbench/<project_id>/`
4. 工作台人工确认和阶段评审：`outputs/reviewed/workbench/<project_id>/`
5. 工作台状态：`workspace/workbench/<project_id>/state.json`
6. 标准资产包模板：
   - `templates/asset-pack/asset-pack-draft.md`
   - `templates/review-report/review-report.md`
   - `templates/missing-materials/missing-materials.md`
   - `templates/risk-list/risk-list.md`
   - `templates/reusable-assets/reusable-assets.md`

## 输出

写入 `outputs/generated/<project_id>/`：

- `review-report.md`
- `asset-pack-draft.md`
- `missing-materials.md`
- `risk-list.md`
- `reusable-assets.md`
- `workbench-archive-summary.md`

这些文件仍是 AI 初稿，后续必须执行 `/review-asset-pack` 或 `python scripts/review_asset_pack.py --project <project_id>` 进入人工评审定稿。

## 归档规则

1. 以人工确认和阶段评审结果为最高优先级。
2. AI 阶段报告只能作为证据和素材，不能直接写成已确认事实。
3. 已通过人工评审的阶段内容，可以作为“已确认过程记录”引用。
4. 未评审或评审未通过的阶段，必须标记为“待确认”。
5. 风险、资料缺口、测试结果、部署交接、可复用资产必须从阶段报告、资产包更新、人工评审记录中归纳。
6. 不得输出敏感原文。
7. 不得编造未在工作台过程资料中出现的内容。

## 字段映射

- `info-alignment.md` -> 项目概况、业务背景与目标、需求摘要
- `project-kickoff-checklist.md` -> 需求摘要、资料缺口摘要、补全建议
- `asset-pack-skeleton.md` -> 项目资产包主结构
- `risk-action-list.md` -> 风险清单、补全建议
- `stages/*/stage-plan.md` -> 阶段目标、范围和验收线索
- `stages/*/stage-report.md` -> 代码地图、核心模块、测试与缺陷、部署交接
- `stages/*/asset-pack-update.md` -> 资产包增量内容
- `outputs/reviewed/workbench/**/stage-review.md` -> 人工评审记录、已确认内容、待确认事项

## 输出质量要求

正式进入人工评审前，生成的资产包初稿必须能回答：

- 项目做了什么，为什么做。
- 交付范围是什么，哪些内容仍待确认。
- 代码结构、核心模块、接口、数据、部署和测试资料是否足够交接。
- 项目过程中有哪些关键决策、风险和遗留问题。
- 哪些内容可以沉淀为可复用资产，哪些只能项目内参考。
