---
name: plan-project-lifecycle
description: 基于已确认项目上下文生成或修订项目全周期规划，作为后续阶段计划和阶段执行的上位指引。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# plan-project-lifecycle

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/plan-project-lifecycle.md`

推荐触发：

```text
/plan-project-lifecycle <project_id>
```

或：

```powershell
python scripts\plan_project_lifecycle.py --project <project_id>
```
