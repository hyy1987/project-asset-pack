# AGENTS.md

你正在 `project-asset-pack` 中工作。本仓库是项目资产包智能体和 Agent-First 软件外包项目工作台的控制面。

本文件是 Codex 的项目入口说明。通用工作流规则不写在本文件里，而是统一放在：

```text
docs/agent-workflows/
```

执行任何工作台或资产包任务前，先读取：

1. `docs/agent-workflows/workbench-overview.md`
2. 对应任务的 `docs/agent-workflows/<task>.md`
3. `configs/projects/<project_id>.yaml`
4. `workspace/workbench/<project_id>/state.json`，如果存在
5. `outputs/reviewed/` 中已经人工确认或评审的内容
6. `outputs/generated/` 中的 AI 初稿和阶段输出

## Codex 使用方式

Codex 没有 Claude Code 的 slash command 时，使用自然语言引用 workflow：

```text
按 docs/agent-workflows/init-project-workbench.md，启动 my-project 工作台。
```

```text
按 docs/agent-workflows/start-active-project-workbench.md，把 my-project 这个在研项目直接接入工作台。
```

```text
按 docs/agent-workflows/run-project-stage.md，执行 my-project 的 stage-1。
```

```text
按 docs/agent-workflows/resume-project-workbench.md，恢复 my-project 的工作台上下文。
```

## 关键约束

- `docs/agent-workflows/` 是唯一工作流规则源。
- 不维护 Codex 专属的另一套流程规则。
- 默认不修改业务项目仓库。
- 修改业务项目必须同时满足：项目配置允许、阶段计划允许、人类明确授权。
- AI 输出进入 `outputs/generated/`，正式结果必须经过人工评审后进入 `outputs/reviewed/`。
- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书、生产连接串、客户真实业务数据、合同金额、报价和商业策略。
- 不绕过人工评审进入下一阶段。

## 文件编辑要求

- 不删除或覆盖 `outputs/reviewed/` 中的人工评审结果。
- 不把未脱敏客户材料复制到输出目录。
- 不把无法确认的推断写成已确认事实。
- 对缺口、风险和待确认事项保持显式标记。
