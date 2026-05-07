---
name: plan-project-stage
description: 基于已确认项目上下文生成可评审、可执行、可回滚的阶段计划。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# plan-project-stage

用于在信息对齐后生成阶段计划。

## 推荐触发方式

```powershell
python scripts\plan_project_stage.py --project <project_id> --stage-id <stage_id> --title "<stage_title>"
```

## 输入

1. `configs/projects/<project_id>.yaml`
2. `outputs/generated/workbench/<project_id>/info-alignment.md`
3. `outputs/generated/workbench/<project_id>/project-kickoff-checklist.md`
4. `outputs/reviewed/workbench/<project_id>/human-confirmation.md`，如果存在
5. `templates/workbench/stage-plan.md`

## 输出

写入：

```text
outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-plan.md
```

## 计划要求

- 阶段目标必须可评审。
- 阶段边界必须写清楚“做”和“不做”。
- 必须列出执行前需要人类确认的问题。
- 必须列出 Agent 执行任务、自检与测试要求、阶段交付物。
- 不得把待确认内容写成已确认。
- 默认不允许直接修改业务仓库，除非项目配置和人工确认明确允许。

