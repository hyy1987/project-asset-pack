# 接入在研项目工作台

用于把正在进行中的项目直接接入 Agent-First 工作台。项目可以已经有资产包，也可以只有项目配置、业务仓库和资料目录。

## 适用场景

1. 项目已经在开发或维护中，后续希望用工作台管理阶段计划、开发执行、质量门禁和评审。
2. 项目可能尚未生成资产包，不要求先补做。
3. 项目可能已有 `outputs/generated/asset-pack/` 或 `outputs/reviewed/asset-pack/`，这些只作为可选上下文。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `configs/security-rules/<rule_set>.md`
4. 业务项目仓库和资料目录，以项目配置为准
5. 前期资料目录：`inputs/pre-project/` 或配置中声明的目录，如果存在
6. 已有 AI 资产包初稿：`outputs/generated/asset-pack/`，如果存在
7. 已有人工评审资产包：`outputs/reviewed/asset-pack/`，如果存在
8. `templates/workbench/active-project-intake.md`
9. `templates/workbench/info-alignment.md`
10. `templates/workbench/project-kickoff-checklist.md`
11. `templates/workbench/responsibility-questions.md`
12. `templates/workbench/asset-pack-skeleton.md`
13. `templates/workbench/risk-action-list.md`

## 输出

写入 `outputs/generated/workbench/`：

- `01-active-project-intake.md`
- `02-info-alignment.md`
- `03-project-kickoff-checklist.md`
- `04-responsibility-questions.md`
- `05-asset-pack-skeleton.md`
- `06-risk-action-list.md`

必要时写入或更新：

```text
workspace/workbench/project-experience.md
workspace/workbench/state.json
```

## 规则

1. 不要求先生成资产包；已有资产包只是辅助上下文。
2. 对业务仓库只做状态盘点，不默认修改代码。
3. 不把历史资料、AI 初稿或仓库推断直接写成已确认事实；必须标注“已确认”“待人工确认”“可能已过期”。
4. 接入完成后，先人工确认接入摘要、信息对齐稿和风险行动清单。
5. 进入开发前必须生成或修订全周期规划，再生成下一阶段计划。
6. 如果已有工作台状态，不得删除已有阶段记录和人工评审结果，只能追加接入来源和新的工作台输出。
7. 修改业务项目仓库仍必须同时满足：项目配置允许、阶段计划允许、人类明确授权。

