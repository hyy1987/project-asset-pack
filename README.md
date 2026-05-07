# Project Asset Pack

基于 Claude Code 的项目资产包生成、评审、增量更新和 Agent-First 软件外包项目工作台。

当前项目已经从“历史项目资产包生成工具”扩展为一个文件化工作台 MVP，用来支持外包项目从前期资料接入、信息对齐、全周期规划、阶段计划、阶段执行、阶段评审，到结题归档为标准项目资产包初稿的闭环。

本仓库不放业务代码，只作为工作台模板和控制面使用。

## 当前状态

已实现三条能力线：

1. **历史项目资产包**
   - 接入已有项目代码仓库和资料目录。
   - 生成项目现状审查报告、资产包初稿、资料缺口、风险清单和可复用资产候选。
   - 支持人工评审后输出正式资产包。

2. **在研项目增量更新和体检**
   - 保存代码仓库远程基线。
   - 检测仓库更新并增量更新资产包初稿。
   - 对在研项目或维护项目执行项目体检。

3. **Agent-First 项目工作台**
   - 接入新项目的前期资料。
   - 生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
   - 人工确认项目上下文。
   - 生成项目全周期规划。
   - 基于全周期规划生成阶段计划和阶段目标。
   - 让 Agent 按阶段执行开发任务、自检和测试。
   - 输出阶段报告和资产包更新。
   - 人工评审阶段结果。
   - 评审通过后进入下一阶段。
   - 项目结题或阶段性归档时，把工作台过程资料归档为标准项目资产包初稿。
   - 新 Claude Code 窗口可通过恢复摘要继续工作，避免重复初始化。

## 目录结构

```text
project-asset-pack/
|-- .claude/      Claude Code 配置和 skills
|-- configs/      项目接入配置和安全规则
|-- docs/         使用手册、人工补充和评审意见
|-- examples/     可提交的示例项目材料
|-- inputs/       真实项目前期资料输入区，默认不提交
|-- outputs/      AI 初稿、人工评审结果和发布产物，默认不提交
|-- scripts/      自动化脚本
|-- templates/    资产包和工作台输出模板
`-- workspace/    状态、日志和快照，默认不提交
```

## 快速验证 sample-project

仓库内置了一个可直接测试的示例材料目录：

```text
examples/sample-project/pre-project/
```

`configs/projects/sample-project.yaml` 已经指向这个目录。

先复制 Claude Code 本地配置示例：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

检查示例配置：

```powershell
python scripts/check_project_config.py --project sample-project
```

`sample-project` 的业务代码仓库路径是占位示例，缺失路径会以 warning 形式提示；这不影响前期资料工作台流程验证。

### 离线验证

不调用 Claude Code，只验证目录、模板和状态推进：

```powershell
python scripts/init_project_workbench.py --project sample-project --no-claude --overwrite
python scripts/confirm_project_context.py --project sample-project --decision confirmed --overwrite
python scripts/plan_project_lifecycle.py --project sample-project --no-claude --overwrite
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段" --no-claude --overwrite
python scripts/run_project_stage.py --project sample-project --stage-id stage-1 --no-claude --overwrite
python scripts/review_project_stage.py --project sample-project --stage-id stage-1 --decision approve --no-claude --overwrite
python scripts/resume_project_workbench.py --project sample-project --no-claude --overwrite
python scripts/finalize_workbench_asset_pack.py --project sample-project --no-claude --overwrite
python scripts/check_project_workbench.py --project sample-project
```

### 使用 Claude Code 验证

从本目录启动 Claude Code：

```powershell
cd project-asset-pack
claude
```

在 Claude Code 会话中执行：

```text
/init-project-workbench sample-project
```

如果 slash command 没有识别，可以直接输入：

```text
请按 .claude/skills/init-project-workbench/SKILL.md 的规则，基于 configs/projects/sample-project.yaml 和 examples/sample-project/pre-project 生成 sample-project 的工作台初始化输出。
```

## 新窗口恢复

Claude Code 的聊天历史不是工作台进度来源。工作台进度记录在：

```text
workspace/workbench/<project_id>/state.json
```

如果 Claude Code 新窗口不知道当前进度，先运行：

```powershell
python scripts/resume_project_workbench.py --project my-project
```

它会生成：

```text
outputs/generated/workbench/my-project/resume-brief.md
```

新窗口中的 Claude Code 应先读取这份恢复摘要，再继续阶段执行、阶段评审、全周期规划修订、下一阶段规划或归档。只有状态文件不存在，或人类明确要求重建，才重新初始化。

## Agent-First 工作台流程

真实项目建议复制一份项目配置：

```powershell
Copy-Item configs/projects/sample-project.yaml configs/projects/my-project.yaml
```

把允许进入项目工作区的前期资料放到：

```text
inputs/pre-project/my-project/
```

并在 `configs/projects/my-project.yaml` 中配置：

```yaml
workbench:
  pre_project_materials: inputs/pre-project/my-project
  allow_code_changes: false
```

启动项目工作台：

```powershell
python scripts/init_project_workbench.py --project my-project
```

人工确认信息对齐结果：

```powershell
python scripts/confirm_project_context.py --project my-project --decision confirmed
```

生成项目全周期规划：

```powershell
python scripts/plan_project_lifecycle.py --project my-project
```

生成第一阶段计划：

```powershell
python scripts/plan_project_stage.py --project my-project --stage-id stage-1 --title "第一阶段"
```

执行第一阶段：

```powershell
python scripts/run_project_stage.py --project my-project --stage-id stage-1
```

当前工作台默认推荐一个 Agent 作为阶段开发执行者。多人协作主要在阶段计划确认、阶段报告评审、风险判断和验收授权时进入，不建议多个 Agent 终端同时推进同一阶段开发。

默认不修改业务项目仓库。需要 Agent 修改业务项目时，必须同时满足：

- `configs/projects/my-project.yaml` 中 `workbench.allow_code_changes: true`
- 阶段计划明确允许修改代码
- 运行时加入人工授权参数

```powershell
python scripts/run_project_stage.py --project my-project --stage-id stage-1 --allow-code-changes
```

人工评审阶段结果：

```powershell
python scripts/review_project_stage.py --project my-project --stage-id stage-1 --decision approve
```

阶段通过后，不要直接凭聊天继续做下一期。先检查全周期规划是否需要调整：

```powershell
python scripts/plan_project_lifecycle.py --project my-project --revision-reason "stage-1 评审后调整后续路线"
```

然后再基于最新全周期规划生成下一阶段计划：

```powershell
python scripts/plan_project_stage.py --project my-project --stage-id stage-2 --title "第二阶段"
```

项目结题或阶段性归档时，生成标准资产包初稿：

```powershell
python scripts/finalize_workbench_asset_pack.py --project my-project
```

归档后继续走已有人工评审定稿流程：

```powershell
python scripts/review_asset_pack.py --project my-project
```

检查工作台状态：

```powershell
python scripts/check_project_workbench.py --project my-project
```

## 项目资产包流程

历史项目或已有项目可以直接走资产包流程。

初始化资产包：

```text
/init-asset-pack my-project
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

## Claude Code Skills

资产包相关：

- `/init-asset-pack`
- `/update-asset-pack`
- `/review-asset-pack`
- `/check-project-health`

工作台相关：

- `/init-project-workbench`
- `/resume-project-workbench`
- `/plan-project-lifecycle`
- `/plan-project-stage`
- `/run-project-stage`
- `/review-project-stage`
- `/finalize-workbench-asset-pack`
- `/ask-project-info`

## 工作台输出

项目启动输出到：

```text
outputs/generated/workbench/my-project/
|-- info-alignment.md
|-- project-kickoff-checklist.md
|-- responsibility-questions.md
|-- asset-pack-skeleton.md
|-- risk-action-list.md
|-- lifecycle-plan.md
`-- resume-brief.md
```

阶段输出到：

```text
outputs/generated/workbench/my-project/stages/stage-1/
|-- stage-plan.md
|-- stage-report.md
`-- asset-pack-update.md
```

人工确认和阶段评审输出到：

```text
outputs/reviewed/workbench/my-project/
|-- human-confirmation.md
`-- stages/stage-1/stage-review.md
```

工作台状态保存到：

```text
workspace/workbench/my-project/state.json
```

工作台结题归档会复用标准资产包输出目录：

```text
outputs/generated/my-project/
|-- review-report.md
|-- asset-pack-draft.md
|-- missing-materials.md
|-- risk-list.md
|-- reusable-assets.md
`-- workbench-archive-summary.md
```

这些仍是 AI 初稿，必须经过 `review_asset_pack.py` 人工评审后才能进入 `outputs/reviewed/my-project/`。

## 多项目和多团队使用方式

当前结构支持一个工作台管理多个项目。

`project-asset-pack` 更适合作为工作台模板和控制面，不建议把所有真实客户资料集中提交到同一个 Git 仓库。是否使用单工作台、多团队工作台或单项目工作台，应根据公司内部权限边界选择。

小公司、小团队或一人公司，可以直接在同一个工作台中维护多个项目：

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

如果公司内有多个工作组，或者不同项目之间存在明显权限边界，建议按团队或按项目 fork 多个工作台：

```text
project-asset-pack-team-a/
project-asset-pack-team-b/
```

或：

```text
project-asset-pack-project-a/
project-asset-pack-project-b/
```

建议原则：

- 小团队：一个工作台管理多个项目。
- 多团队：一个团队一个工作台。
- 强隔离项目：一个项目一个工作台。
- 通用脚本、skills、模板和安全规则进 Git。
- 真实客户资料、AI 初稿、人工评审结果和运行状态默认不进 Git。

## 安全原则

- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书。
- 不输出客户真实业务数据。
- 不把未经人工确认的可复用资产放入公司级资产库。
- AI 输出只能作为初稿，必须人工评审后才能定版。
- 默认不修改业务项目仓库。
- 不越过人工确认改变交付范围。
- 不绕过阶段评审进入下一阶段。
