---
name: plan-project-lifecycle
description: 基于已确认项目上下文生成项目全周期规划，作为后续阶段计划和阶段执行的上位指引。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# plan-project-lifecycle

用于在信息对齐和人工确认之后，生成项目全周期规划。

## 推荐触发方式

```powershell
python scripts\plan_project_lifecycle.py --project <project_id>
```

如果某个阶段评审后需要调整后续整体规划，可运行：

```powershell
python scripts\plan_project_lifecycle.py --project <project_id> --revision-reason "stage-1 评审后调整后续路线"
```

## 输入

1. `configs/projects/<project_id>.yaml`
2. `outputs/generated/workbench/<project_id>/info-alignment.md`
3. `outputs/generated/workbench/<project_id>/project-kickoff-checklist.md`
4. `outputs/generated/workbench/<project_id>/risk-action-list.md`
5. `outputs/reviewed/workbench/<project_id>/human-confirmation.md`，如果存在
6. 已有 `outputs/generated/workbench/<project_id>/lifecycle-plan.md`，如果是修订
7. 已有阶段报告和阶段评审记录，如果是阶段后修订
8. `templates/workbench/lifecycle-plan.md`

## 输出

写入或更新：

```text
outputs/generated/workbench/<project_id>/lifecycle-plan.md
```

## 规划要求

1. 先给出项目全周期目标、交付范围、非交付范围和关键假设。
2. 必须规划完整阶段路线图，不只规划第一期。
3. 每个阶段都要写清阶段目标、主要产物、人工评审点和进入下一阶段条件。
4. 阶段可以保持粗粒度，但必须能指导后续阶段计划。
5. 不得把未知事项写成已确认；未知内容标注“待人工确认”。
6. 不得绕过人工评审把后续阶段直接视为已授权。
7. 如果是修订规划，必须说明修订原因、影响范围和后续阶段变化。
8. 阶段计划必须服从最新全周期规划。
