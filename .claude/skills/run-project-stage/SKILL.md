---
name: run-project-stage
description: 按阶段计划执行单 Agent 阶段开发、自检、测试、资产包更新，并生成阶段报告。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash
---

# run-project-stage

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/run-project-stage.md`

推荐触发：

```text
/run-project-stage <project_id> <stage_id>
```

或：

```powershell
python scripts\run_project_stage.py --project <project_id> --stage-id <stage_id>
```
