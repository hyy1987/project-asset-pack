---
name: start-active-project-workbench
description: 将正在进行中的项目直接接入 Agent-First 工作台，用于后续阶段规划、开发执行和质量评审；不要求已有资产包。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# start-active-project-workbench

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/start-active-project-workbench.md`

推荐触发：

```text
/start-active-project-workbench <project_id>
```

或：

```powershell
python scripts\start_active_project_workbench.py --project <project_id>
```
