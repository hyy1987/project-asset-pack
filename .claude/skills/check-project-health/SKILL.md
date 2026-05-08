---
name: check-project-health
description: 对正在开发或维护中的项目执行定期体检，检查项目资料沉淀、代码变化、测试缺陷和交付准备状态。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash(git:*)
---

# check-project-health

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/check-project-health.md`

推荐触发：

```text
/check-project-health <project_id> <period>
```

或：

```powershell
python scripts\check_project_health.py --project <project_id> --period weekly
```
