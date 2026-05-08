# 增量更新项目资产包

用于未接入 Agent-First 工作台的在研项目或维护项目，基于远程仓库基线和当前项目仓库变化，增量更新项目资产包初稿。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `workspace/snapshots/<project_id>-repo-baseline.json`
4. 脚本提供的仓库变更摘要
5. 当前生成资产包：`outputs/generated/<project_id>/`

## 输出

更新 `outputs/generated/<project_id>/` 中受影响的资产包文件。

## 规则

1. 只用于未接入工作台的项目；已接入工作台的在研项目应通过阶段报告、资料接入、CR 队列和归档更新资产包。
2. 常规更新建议由 `scripts/update_asset_pack.py` 触发，因为脚本负责远程检查、快进同步、变更对比和基线更新。
3. 只更新受影响章节，避免重写无关内容。
4. 对无法确认的变化标注“待人工确认”。
5. 不输出敏感原文。
