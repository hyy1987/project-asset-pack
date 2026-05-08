---
name: init-project-workbench
description: 接入新外包任务前期资料，生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# init-project-workbench

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/init-project-workbench.md`

推荐触发：

```text
/init-project-workbench <project_id>
```

或：

```powershell
python scripts\init_project_workbench.py --project <project_id>
```
