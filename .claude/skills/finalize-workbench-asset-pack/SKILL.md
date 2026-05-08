---
name: finalize-workbench-asset-pack
description: 基于 Agent-First 工作台过程资料和阶段评审结果，生成标准项目资产包初稿。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# finalize-workbench-asset-pack

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时先读取并遵守：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/finalize-workbench-asset-pack.md`

推荐触发：

```text
/finalize-workbench-asset-pack <project_id>
```

或：

```powershell
python scripts\finalize_workbench_asset_pack.py --project <project_id>
```
