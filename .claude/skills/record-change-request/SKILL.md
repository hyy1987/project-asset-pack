---
name: record-change-request
description: 记录甲方新增需求、需求变更或范围变化，写入工作台需求变更队列。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# record-change-request

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/record-change-request.md`

推荐触发：

```text
/record-change-request <project_id> <title>
```

或：

```powershell
python scripts\record_change_request.py --project <project_id> --title "<title>"
```
