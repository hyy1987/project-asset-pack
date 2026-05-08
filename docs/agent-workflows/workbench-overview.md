# Agent 工作台通用规则

本目录是 `project-asset-pack` 的 Agent 无关工作流规则源。

Claude Code、Codex 或其他 Agent 客户端都应读取这里的规则。`.claude/skills/` 和 `AGENTS.md` 只是不同 Agent 的入口适配层，不应维护另一套流程规则。

## 共同目标

`project-asset-pack` 支持三类使用路径：

1. 历史项目资产包：生成项目现状审查、资产包初稿、资料缺口、风险清单和可复用资产候选。
2. Agent-First 项目工作台：提供两个并列入口，新项目从前期资料启动，在研项目从项目配置、业务仓库、资料目录和可选历史材料接入；接入后汇入同一套规划、阶段执行、质量门禁、人工评审、经验沉淀和归档流程。
3. 未接入工作台的在研项目辅助流程：资产包增量更新和项目体检。

同一个项目不要同时用工作台和非工作台辅助流程并行管理。项目已经接入工作台后，应以工作台为主；暂不采用 Agent-First 模式的项目，才使用资产包增量更新和项目体检。

## 工作台主线

```text
新项目入口：前期资料接入
在研项目入口：项目配置 + 业务仓库 + 资料目录接入
  -> 信息对齐
  -> 人工确认上下文
  -> 全周期规划
  -> 阶段计划
  -> 单 Agent 阶段执行
  -> 阶段报告和资产包更新
  -> 阶段质量门禁
  -> 人工评审
  -> 阶段经验沉淀
  -> 检查/修订全周期规划
  -> 下一阶段或结题归档
```

正在进行中的项目可以从“在研项目接入工作台”开始，先生成接入摘要和工作台上下文，再进入全周期规划和下一阶段计划。这个入口不要求项目已有资产包。

新资料和新需求进入项目时，必须先记录到工作台文件：资料进入 `material-intake/`，需求变化进入 `change-requests/`。聊天窗口可以触发流程，但不能作为唯一留痕。

默认一个 Agent 作为阶段开发执行者。多人合作主要进入阶段计划确认、阶段评审和验收授权，不建议多个 Agent 终端同时推进同一阶段开发。

## 读取顺序

执行任何项目工作前，按顺序读取：

1. `configs/projects/<project_id>.yaml`
2. `workspace/workbench/<project_id>/state.json`，如果存在
3. `outputs/generated/workbench/<project_id>/resume-brief.md`，如果存在
4. `configs/security-rules/<rule_set>.md`
5. `inputs/pre-project/<project_id>/` 或配置中声明的前期资料目录
6. `outputs/reviewed/workbench/<project_id>/` 中已经人工确认的信息
7. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`，如果存在
8. `workspace/workbench/<project_id>/project-experience.md`，如果存在
9. `outputs/generated/workbench/<project_id>/` 中的 AI 初稿和阶段输出
10. `outputs/reviewed/<project_id>/` 中已有的正式资产包，如果存在
11. `outputs/generated/<project_id>/` 中已有的资产包初稿，如果存在
12. 对应任务的 `docs/agent-workflows/*.md`
13. `templates/**`
14. 已通过 Agent 客户端接入的业务仓库和资料目录
15. 用户在当前会话中补充的说明

## 输出约定

- AI 初稿：`outputs/generated/`
- 人工评审结果：`outputs/reviewed/`
- 工作台状态：`workspace/workbench/<project_id>/state.json`
- 项目经验库：`workspace/workbench/<project_id>/project-experience.md`
- 新窗口恢复摘要：`outputs/generated/workbench/<project_id>/resume-brief.md`
- 新资料接入：`outputs/generated/workbench/<project_id>/material-intake/`
- 需求变更队列：`outputs/generated/workbench/<project_id>/change-requests/`

AI 输出只能作为初稿。正式材料必须经过人工评审后进入 `outputs/reviewed/`。

## 安全边界

- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书、生产连接串。
- 不输出客户真实业务数据、合同金额、报价和商业策略。
- 不把未脱敏的客户材料复制到输出目录。
- 对无法确认的内容必须标记为“待人工确认”，不能编造。
- 默认不修改业务项目仓库。
- 修改业务项目必须同时满足：项目配置允许、阶段计划允许、人类明确授权。
- 不绕过人工评审进入下一阶段。
