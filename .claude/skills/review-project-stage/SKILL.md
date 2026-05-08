---
name: review-project-stage
description: 基于阶段报告和人工意见生成阶段评审记录，并决定是否允许继续推进后续规划。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# review-project-stage

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/review-project-stage.md`

推荐触发：

```text
/review-project-stage <project_id> <stage_id> <decision>
```

或：

```powershell
python scripts\review_project_stage.py --project <project_id> --stage-id <stage_id> --decision approve
```
