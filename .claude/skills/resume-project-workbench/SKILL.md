---
name: resume-project-workbench
description: 在新的 Agent 会话中恢复 Agent-First 工作台上下文，读取状态、已评审材料、阶段输出和建议下一步，避免重复初始化。
allowed-tools: Read, Write, Edit, Glob, Grep, LS
---

# resume-project-workbench

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/resume-project-workbench.md`

推荐触发：

```text
/resume-project-workbench <project_id>
```

或：

```powershell
python scripts\resume_project_workbench.py --project <project_id>
```
