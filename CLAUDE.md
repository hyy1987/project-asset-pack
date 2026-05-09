# CLAUDE.md

你正在 `project-asset-pack` 中运行 Claude Code。本仓库是项目资产包智能体和 Agent-First 软件外包项目工作台的控制面。

本文件是 Claude Code 的入口说明。通用工作流规则不写在本文件里，而是统一放在：

```text
docs/agent-workflows/
```

默认项目空间在 `project-asset-pack` 同级的 `../<project_id>/<project_id>-docs/`。除非项目配置显式覆盖，`inputs/`、`outputs/` 和 `workspace/` 都指这个项目资料目录下的路径，不再默认写入工具仓库内部。

`.claude/skills/` 只是 Claude Code 的快捷入口。执行任何任务时，应先读取：

1. `docs/agent-workflows/workbench-overview.md`
2. 对应任务的 `docs/agent-workflows/<task>.md`
3. `configs/projects/<project_id>.yaml`
4. `workspace/workbench/state.json`，如果存在
5. `outputs/reviewed/` 中已经人工确认或评审的内容
6. `outputs/generated/` 中的 AI 初稿和阶段输出

## Claude Code 使用方式

可以使用自然语言：

```text
请按 docs/agent-workflows/init-project-workbench.md，启动 my-project 工作台。
```

已有在研项目可以直接接入工作台，不要求先生成资产包：

```text
请按 docs/agent-workflows/start-active-project-workbench.md，把 my-project 这个在研项目接入工作台。
```

也可以使用 `.claude/skills/` 提供的快捷命令：

```text
/init-project-workbench my-project
/start-active-project-workbench my-project
/record-material-intake my-project inputs/project-updates/my-project/new-prd.md
/record-change-request my-project 新增导出功能
```

新窗口、上下文丢失或中途恢复时，如果 `workspace/workbench/state.json` 存在，不要提示用户重新初始化。先读取：

```text
docs/agent-workflows/resume-project-workbench.md
```

并恢复工作台上下文。

## 关键约束

- `docs/agent-workflows/` 是唯一工作流规则源。
- 不维护 Claude Code 专属的另一套流程规则。
- 默认不修改业务项目仓库。
- 修改业务项目必须同时满足：项目配置允许、阶段计划允许、人类明确授权。
- AI 输出进入 `outputs/generated/`，正式结果必须经过人工评审后进入 `outputs/reviewed/`。
- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书、生产连接串、客户真实业务数据、合同金额、报价和商业策略。
- 不绕过人工评审进入下一阶段。

## 输出要求

- 使用清晰 Markdown 标题层级。
- 对不确定信息标注“待确认”。
- 对敏感内容只描述类型，不写原值。
- 每个风险项给出影响、证据、建议处理方式。
- 每个资料缺口给出缺口说明、影响、建议补充人。
- 每个可复用资产候选标注复用等级：可直接复用、可改造复用、仅供参考、不跨客户复用。

## 禁止事项

- 禁止执行破坏性 git 操作。
- 禁止删除或覆盖人工评审后的 `outputs/reviewed/` 内容。
- 禁止把 AI 初稿直接写成“已定稿”。
- 禁止把未脱敏的客户材料复制到输出目录。
- 禁止绕过人工评审直接进入下一阶段。
