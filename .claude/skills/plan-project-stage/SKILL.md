---
name: plan-project-stage
description: 基于已确认项目上下文和全周期规划生成可评审、可执行、可回滚的阶段计划。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# plan-project-stage

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/plan-project-stage.md`

推荐触发：

```text
/plan-project-stage <project_id> <stage_id> <stage_title>
```

或：

```powershell
python scripts\plan_project_stage.py --project <project_id> --stage-id <stage_id> --title "<stage_title>"
```
