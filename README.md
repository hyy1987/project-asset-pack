# Project Asset Pack

基于 Claude Code 的项目资产包生成、评审、增量更新和 Agent-First 软件外包项目工作台。

本目录不放业务代码，只负责：

- Claude Code 配置
- 项目接入配置
- 项目资产包模板
- 安全边界规则
- `/init-asset-pack`、`/update-asset-pack`、`/review-asset-pack`、`/check-project-health` skills
- `/init-project-workbench`、`/plan-project-stage`、`/run-project-stage`、`/review-project-stage`、`/finalize-workbench-asset-pack`、`/ask-project-info` skills
- AI 生成结果、人工评审结果、项目体检报告和阶段评审记录

## MVP 目标：项目资产包

资产包第一版跑通一个闭环：

1. 接入一个历史项目的代码仓库和资料目录。
2. 使用 Claude Code 执行 `/init-asset-pack`。
3. 生成项目现状审查报告、资产包初稿、资料缺口清单、风险清单和可复用资产候选。
4. 保存当前远程仓库基线。
5. 后续检测远程仓库更新，安全同步本地仓库，并增量更新资产包初稿。
6. 由人工评审后，输出正式资产包。
7. 对在研项目或维护项目执行定期体检。

## MVP 目标：Agent-First 项目工作台

工作台第一版跑通一个闭环：

1. 接入新项目的前期资料。
2. 生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
3. 人工确认项目上下文。
4. 生成阶段计划和第一阶段目标。
5. Agent 按阶段执行开发任务、自检和测试。
6. 输出阶段报告和资产包更新。
7. 人工评审代码结果、测试结果、风险和资产包更新。
8. 评审通过后进入下一阶段。
9. 项目结题时，把工作台过程资料归档为标准项目资产包初稿。

## 快速开始

1. 复制本地配置示例：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

2. 按实际项目修改：

- `.claude/settings.local.json`
- `configs/projects/sample-project.yaml`

`sample-project` 只是占位示例。第一次使用前，建议复制一份项目配置并改成真实项目 ID：

```powershell
Copy-Item configs/projects/sample-project.yaml configs/projects/my-project.yaml
```

下文以 `my-project` 作为真实项目 ID 示例。

3. 从本目录启动 Claude Code：

```powershell
cd project-asset-pack
claude
```

## 项目资产包流程

初始化资产包：

```text
/init-asset-pack my-project
```

如果 skill 尚未被 Claude Code 识别，可以直接输入：

```text
请按 .claude/skills/init-asset-pack/SKILL.md 的规则，基于 configs/projects/my-project.yaml 生成项目资产包 MVP 输出。
```

保存远程仓库基线：

```powershell
python scripts/save_remote_baseline.py --project my-project
```

后续更新资产包：

```powershell
python scripts/update_asset_pack.py --project my-project
```

人工评审后定稿：

```powershell
python scripts/review_asset_pack.py --project my-project
```

在研项目或维护项目体检：

```powershell
python scripts/check_project_health.py --project my-project --period weekly
```

## Agent-First 工作台流程

1. 把允许进入项目工作区的前期资料放到：

```text
inputs/pre-project/my-project/
```

2. 启动项目工作台：

```powershell
python scripts/init_project_workbench.py --project my-project
```

只离线验证目录和模板，不调用 Claude Code：

```powershell
python scripts/init_project_workbench.py --project my-project --no-claude
```

3. 人工确认信息对齐结果：

```powershell
python scripts/confirm_project_context.py --project my-project --decision confirmed
```

4. 生成第一阶段计划：

```powershell
python scripts/plan_project_stage.py --project my-project --stage-id stage-1 --title "第一阶段"
```

5. 执行第一阶段：

```powershell
python scripts/run_project_stage.py --project my-project --stage-id stage-1
```

默认不修改业务项目仓库。需要 Agent 修改业务项目时，必须同时满足：

- `configs/projects/my-project.yaml` 中 `workbench.allow_code_changes: true`
- 阶段计划明确允许修改代码
- 运行时加入人工授权参数

```powershell
python scripts/run_project_stage.py --project my-project --stage-id stage-1 --allow-code-changes
```

6. 人工评审阶段结果：

```powershell
python scripts/review_project_stage.py --project my-project --stage-id stage-1 --decision approve
```

7. 检查工作台状态：

```powershell
python scripts/check_project_workbench.py --project my-project
```

8. 项目结题或阶段性归档时，生成标准资产包初稿：

```powershell
python scripts/finalize_workbench_asset_pack.py --project my-project
```

只离线生成资产包初稿占位文件，不调用 Claude Code：

```powershell
python scripts/finalize_workbench_asset_pack.py --project my-project --no-claude
```

归档后继续走已有人工评审定稿流程：

```powershell
python scripts/review_asset_pack.py --project my-project
```

## 多项目和多团队使用方式

当前结构支持一个工作台管理多个项目。

`project-asset-pack` 更适合作为工作台模板和控制面，不建议把所有真实客户资料集中提交到同一个 Git 仓库。是否使用单工作台、多团队工作台或单项目工作台，应根据公司内部权限边界选择。

对于小公司、小团队或一人公司，可以直接在同一个工作台中维护多个项目：

```text
configs/projects/project-a.yaml
configs/projects/project-b.yaml
inputs/pre-project/project-a/
inputs/pre-project/project-b/
outputs/generated/workbench/project-a/
outputs/generated/workbench/project-b/
outputs/reviewed/workbench/project-a/
outputs/reviewed/workbench/project-b/
workspace/workbench/project-a/
workspace/workbench/project-b/
```

这种方式适合团队成员少、项目权限边界简单、由同一批人负责全部项目的场景。

如果公司内有多个工作组，或者不同项目之间存在明显权限边界，建议不要把所有项目都放进同一个工作台实例。更稳妥的方式是按团队或按项目 fork 多个工作台：

```text
project-asset-pack-team-a/
project-asset-pack-team-b/
```

或：

```text
project-asset-pack-project-a/
project-asset-pack-project-b/
```

这样可以降低误改其他项目配置、误读其他项目资料、混提交不同项目变更的风险。

建议原则：

- 小团队：一个工作台管理多个项目。
- 多团队：一个团队一个工作台。
- 强隔离项目：一个项目一个工作台。
- 通用脚本、skills、模板和安全规则进 Git。
- 真实客户资料、AI 初稿、人工评审结果和运行状态默认不进 Git。

## 项目资产包输出

默认输出到：

```text
outputs/generated/my-project/
├── review-report.md
├── asset-pack-draft.md
├── missing-materials.md
├── risk-list.md
└── reusable-assets.md
```

人工评审输出到：

```text
outputs/reviewed/my-project/
├── asset-pack.md
├── review-record.md
├── approved-reusable-assets.md
└── follow-up-actions.md
```

项目体检输出到：

```text
outputs/generated/project-health/my-project/
├── weekly-health-check.md
└── latest-health-check.md
```

## 工作台输出

项目启动输出到：

```text
outputs/generated/workbench/my-project/
├── info-alignment.md
├── project-kickoff-checklist.md
├── responsibility-questions.md
├── asset-pack-skeleton.md
└── risk-action-list.md
```

阶段输出到：

```text
outputs/generated/workbench/my-project/stages/stage-1/
├── stage-plan.md
├── stage-report.md
└── asset-pack-update.md
```

人工确认和阶段评审输出到：

```text
outputs/reviewed/workbench/my-project/
├── human-confirmation.md
└── stages/stage-1/stage-review.md
```

工作台状态保存到：

```text
workspace/workbench/my-project/state.json
```

工作台结题归档会复用标准资产包输出目录：

```text
outputs/generated/my-project/
├── review-report.md
├── asset-pack-draft.md
├── missing-materials.md
├── risk-list.md
├── reusable-assets.md
└── workbench-archive-summary.md
```

这些仍是 AI 初稿，必须经过 `review_asset_pack.py` 人工评审后才能进入 `outputs/reviewed/my-project/`。

## 安全原则

- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书。
- 不输出客户真实业务数据。
- 不把未经人工确认的可复用资产放入公司级资产库。
- AI 输出只能作为初稿，必须人工评审后才能定版。
- 默认不修改业务项目仓库。
- 不越过人工确认改变交付范围。
- 不绕过阶段评审进入下一阶段。
