---
name: review-asset-pack
description: 基于 AI 初稿和人工评审意见，整理正式项目资产包并输出到 outputs/reviewed。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# review-asset-pack

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/review-asset-pack.md`

推荐触发：

```text
/review-asset-pack <project_id>
```

或：

```powershell
python scripts\review_asset_pack.py --project <project_id>
```
