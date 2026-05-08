---
name: record-material-intake
description: 将甲方新资料、需求文档、会议纪要或聊天补充接入工作台，生成资料接入记录和影响分析。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# record-material-intake

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/record-material-intake.md`

推荐触发：

```text
/record-material-intake <project_id> <source>
```

或：

```powershell
python scripts\record_material_intake.py --project <project_id> --source <path-or-note>
```
