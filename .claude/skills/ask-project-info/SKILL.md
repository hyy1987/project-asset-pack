---
name: ask-project-info
description: 根据项目工作台缺口，向人类生成下一轮需要确认的问题清单。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# ask-project-info

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/ask-project-info.md`

输出到：

```text
outputs/generated/workbench/<project_id>/human-questions.md
```
