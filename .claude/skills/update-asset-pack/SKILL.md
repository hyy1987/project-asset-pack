---
name: update-asset-pack
description: 对比已记录的远程仓库基线和当前同步后的项目仓库版本，按变化范围增量更新项目资产包。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash(git:*), Bash(python:*)
---

# update-asset-pack

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/update-asset-pack.md`

推荐通过脚本触发，因为脚本负责远程检查、快进同步、变更对比和基线更新：

```powershell
python scripts\update_asset_pack.py --project <project_id>
```
