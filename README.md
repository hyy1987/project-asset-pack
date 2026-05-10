# Project Asset Pack

支持 Claude Code 和 Codex 的项目资产包生成、评审、在研项目辅助检查和 Agent-First 软件外包项目工作台。

当前项目已经从“历史项目资产包生成工具”扩展为一个文件化工作台 MVP，用来支持外包项目从前期资料接入、信息对齐、全周期规划、阶段计划、阶段执行、质量门禁、阶段评审、经验沉淀，到结题归档为标准项目资产包初稿的闭环。

本仓库不放业务代码，只作为工作台模板和控制面使用。

## 文档入口

- [QUICKSTART.md](QUICKSTART.md)：快速开始，优先介绍日常使用时最关键的自然语言指令。
- [USAGE.md](USAGE.md)：完整使用说明，保留脚本、快捷命令、工作台流程、资产包流程、输出目录和安全规则等全量细节。
- [AGENTS.md](AGENTS.md)：Codex 入口说明。
- [CLAUDE.md](CLAUDE.md)：Claude Code 入口说明。

## 当前状态

已实现三类使用路径：

1. **历史项目资产包**
   - 接入已有项目代码仓库和资料目录。
   - 生成项目现状审查报告、资产包初稿、资料缺口、风险清单和可复用资产候选。
   - 支持人工评审后输出正式资产包。

2. **Agent-First 项目工作台**
   - 支持两个并列入口：新项目从前期资料启动，在研项目从项目配置、业务仓库、资料目录和可选历史材料接入。
   - 两个入口接入后，汇入同一套信息对齐、规划、阶段执行、质量门禁和评审流程。
   - 支持项目上下文确认、全周期规划、阶段计划、阶段执行、阶段质量门禁、阶段评审、经验沉淀和结题归档。
   - 新 Agent 窗口可通过恢复摘要继续工作，避免重复初始化。

3. **未接入工作台的在研项目辅助流程**
   - 对暂不采用 Agent-First 工作台的在研或维护项目，保留资产包增量更新和项目体检。
   - 这条路径不与工作台并行管理同一个项目；如果项目已经接入工作台，后续应以工作台为主。

推荐原则：能接入工作台的在研项目走工作台；暂不采用 Agent-First 模式的在研项目，才使用资产包增量更新和体检作为轻量辅助。

## 目录结构

```text
project-asset-pack/
|-- .claude/      Claude Code 配置和 skills 入口
|-- configs/      项目接入配置和安全规则
|-- docs/         通用 Agent 工作流、使用手册、人工补充和评审意见
|-- examples/     可提交的示例项目材料
|-- scripts/      自动化脚本
|-- templates/    资产包和工作台输出模板
|-- AGENTS.md     Codex 入口说明
|-- CLAUDE.md     Claude Code 入口说明
|-- QUICKSTART.md 快速开始
`-- USAGE.md      完整使用说明
```

`project-asset-pack` 是工具仓库，只保存模板、脚本、通用规则和项目接入配置。真实项目的默认工作区放在它的同级目录：

```text
my-project/
|-- my-project-docs/
|   |-- inputs/
|   |   |-- pre-project/
|   |   `-- project-updates/
|   |-- outputs/
|   |   |-- generated/
|   |   `-- reviewed/
|   `-- workspace/
|       |-- workbench/
|       `-- snapshots/
|-- frontend/
|-- backend/
`-- database/
```

默认规则是：业务代码仓库、数据库仓库和项目资料仓库跟 `project-asset-pack` 平级，项目过程材料进入 `<project_id>/<project_id>-docs/`。如果某个项目已有自己的目录规范，可以在 `configs/projects/<project_id>.yaml` 中覆盖 `workbench.project_docs_root`、`workbench.pre_project_materials`、`repositories.path`、`output.generated` 和 `output.reviewed`。

## 使用建议

日常优先用自然语言让 Claude Code 或 Codex 读取 `docs/agent-workflows/` 下的规则并执行工作流。固定流程也可以使用 Claude Code 的 slash command，或直接运行 `scripts/` 下的 Python 脚本。

先读 [QUICKSTART.md](QUICKSTART.md) 跑通自然语言入口；需要完整命令、脚本参数、离线验证、质量门禁或多项目使用方式时，再读 [USAGE.md](USAGE.md)。
