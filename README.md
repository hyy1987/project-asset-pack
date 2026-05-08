# Project Asset Pack

支持 Claude Code 和 Codex 的项目资产包生成、评审、增量更新和 Agent-First 软件外包项目工作台。

当前项目已经从“历史项目资产包生成工具”扩展为一个文件化工作台 MVP，用来支持外包项目从前期资料接入、信息对齐、全周期规划、阶段计划、阶段执行、质量门禁、阶段评审、经验沉淀，到结题归档为标准项目资产包初稿的闭环。

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
   - 支持把正在开发或维护中的项目直接接入工作台，不要求先生成资产包或体检报告。

3. **Agent-First 项目工作台**
   - 接入新项目的前期资料。
   - 接入已有在研项目的项目配置、业务仓库、资料目录和可选历史材料。
   - 生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
   - 人工确认项目上下文。
   - 生成项目全周期规划。
   - 基于全周期规划生成阶段计划和阶段目标。
   - 让 Agent 按阶段执行开发任务、自检和测试。
   - 输出阶段报告和资产包更新。
   - 执行阶段质量门禁，检查测试证据、未验证内容和人工必须检查项。
   - 人工评审阶段结果。
   - 沉淀阶段经验，更新项目经验库和长期规则候选。
   - 评审通过后进入下一阶段。
   - 项目结题或阶段性归档时，把工作台过程资料归档为标准项目资产包初稿。
   - 新 Agent 窗口可通过恢复摘要继续工作，避免重复初始化。

## 目录结构

```text
project-asset-pack/
|-- .claude/      Claude Code 配置和 skills 入口
|-- configs/      项目接入配置和安全规则
|-- docs/         通用 Agent 工作流、使用手册、人工补充和评审意见
|-- examples/     可提交的示例项目材料
|-- inputs/       真实项目前期资料输入区，默认不提交
|-- outputs/      AI 初稿、人工评审结果和发布产物，默认不提交
|-- scripts/      自动化脚本
|-- templates/    资产包和工作台输出模板
|-- AGENTS.md     Codex 入口说明
|-- CLAUDE.md     Claude Code 入口说明
`-- workspace/    状态、日志和快照，默认不提交
```

## 快速验证 sample-project

仓库内置了一个可直接测试的示例材料目录：

```text
examples/sample-project/pre-project/
```

`configs/projects/sample-project.yaml` 已经指向这个目录。

如果使用 Claude Code，先复制本地配置示例：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

检查示例配置：

```powershell
python scripts/check_project_config.py --project sample-project
```

`sample-project` 的业务代码仓库路径是占位示例，缺失路径会以 warning 形式提示；这不影响前期资料工作台流程验证。

## 推荐使用方式

`project-asset-pack` 的主要使用场景是在 Claude Code 或 Codex 中由 Agent 读取规则、执行工作流和生成文件。

通用规则统一放在：

```text
docs/agent-workflows/
```

其中：

- `CLAUDE.md` 是 Claude Code 入口说明。
- `.claude/skills/` 是 Claude Code 快捷命令入口。
- `AGENTS.md` 是 Codex 入口说明。
- `docs/agent-workflows/` 是唯一工作流规则源。

推荐顺序是：

1. **自然语言启动**：最适合日常使用，也最符合 Agent-First 工作方式。
2. **快捷命令启动**：适合在 Claude Code 中快速触发固定 skill。
3. **Python 脚本启动**：适合离线验证、自动化、CI 或 Agent 客户端不可用时检查目录和状态。

例如启动一个新项目工作台，可以直接在 Claude Code 或 Codex 里说：

```text
请基于 my-project 的配置和前期资料，启动 Agent-First 项目工作台，完成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
```

如果使用 Claude Code，也可以用快捷命令：

```text
/init-project-workbench my-project
```

脚本方式是底层稳定入口：

```powershell
python scripts/init_project_workbench.py --project my-project
```

Codex 中也可以明确引用通用 workflow：

```text
按 docs/agent-workflows/init-project-workbench.md，启动 my-project 工作台。
```

脚本支持通过 `--agent` 选择 Agent 后端：

```powershell
python scripts/init_project_workbench.py --project my-project --agent claude
python scripts/init_project_workbench.py --project my-project --agent codex
python scripts/init_project_workbench.py --project my-project --agent none
```

默认是 `--agent claude`。`--agent none` 用于只生成目录、模板和状态，不拉起任何 Agent 客户端；`--no-agent` 作为兼容写法，等价于 `--agent none`。

### 离线验证

不调用 Agent 客户端，只验证目录、模板和状态推进。离线模式不会自动补全阶段报告、资产包更新和质量门禁，因此示例用 `changes-requested` 模拟人工发现问题；不要把它当作阶段通过演示。

```powershell
python scripts/init_project_workbench.py --project sample-project --agent none --overwrite
python scripts/confirm_project_context.py --project sample-project --decision confirmed --overwrite
python scripts/plan_project_lifecycle.py --project sample-project --agent none --overwrite
python scripts/plan_project_stage.py --project sample-project --stage-id stage-1 --title "第一阶段" --agent none --overwrite
python scripts/run_project_stage.py --project sample-project --stage-id stage-1 --agent none --overwrite
python scripts/check_stage_quality.py --project sample-project --stage-id stage-1 --agent none --validate --overwrite
python scripts/review_project_stage.py --project sample-project --stage-id stage-1 --decision changes-requested --agent none --overwrite
python scripts/summarize_stage_experience.py --project sample-project --stage-id stage-1 --agent none --overwrite
python scripts/resume_project_workbench.py --project sample-project --agent none --overwrite
python scripts/finalize_workbench_asset_pack.py --project sample-project --agent none --overwrite
python scripts/check_project_workbench.py --project sample-project
```

如果要演示 `approve`，必须先由 Agent 或人工补齐阶段报告、阶段资产包更新和质量门禁，并确保质量门禁明确允许进入人工评审；只有确有人工例外时才使用 `--skip-quality-gate`。

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
请按 docs/agent-workflows/init-project-workbench.md 的规则，基于 configs/projects/sample-project.yaml 和 examples/sample-project/pre-project 生成 sample-project 的工作台初始化输出。
```

### 使用 Codex 验证

从本目录启动 Codex 后，直接用自然语言引用通用 workflow：

```text
按 docs/agent-workflows/init-project-workbench.md，基于 configs/projects/sample-project.yaml 和 examples/sample-project/pre-project 生成 sample-project 的工作台初始化输出。
```

继续阶段工作时同样引用对应 workflow：

```text
按 docs/agent-workflows/resume-project-workbench.md，恢复 sample-project 的工作台上下文。
```

## 新窗口恢复

Agent 客户端的聊天历史不是工作台进度来源。工作台进度记录在：

```text
workspace/workbench/<project_id>/state.json
```

如果新窗口不知道当前进度，先运行：

```text
/resume-project-workbench my-project
```

或直接说：

```text
请恢复 my-project 的工作台上下文，先读取状态文件、人工评审结果、全周期规划和恢复摘要，然后告诉我当前阶段和下一步。
```

底层脚本入口：

```powershell
python scripts/resume_project_workbench.py --project my-project
```

它会生成：

```text
outputs/generated/workbench/my-project/resume-brief.md
```

新窗口中的 Agent 应先读取这份恢复摘要，再继续阶段执行、阶段评审、全周期规划修订、下一阶段规划或归档。只有状态文件不存在，或人类明确要求重建，才重新初始化。

## 在研项目直接接入工作台

如果项目已经在开发或维护中，现在要把后续工作切到 Agent-First 工作台，不需要先补做资产包或项目体检。只要 `configs/projects/my-project.yaml` 已经配置好业务仓库、资料目录和安全规则，就可以直接接入：

自然语言：

```text
请把 my-project 这个在研项目接入 Agent-First 工作台，读取项目配置、业务仓库状态、资料目录，以及可选的已有资产包和体检报告，生成接入摘要、信息对齐稿、风险行动清单和后续规划输入。
```

快捷命令：

```text
/start-active-project-workbench my-project
```

脚本：

```powershell
python scripts/start_active_project_workbench.py --project my-project
```

脚本会优先读取项目配置中的业务仓库和资料目录；如果已有下面这些材料，也会作为可选上下文读取：

```text
outputs/generated/my-project/
outputs/reviewed/my-project/
outputs/generated/project-health/my-project/
```

接入输出包括：

```text
outputs/generated/workbench/my-project/active-project-intake.md
outputs/generated/workbench/my-project/info-alignment.md
outputs/generated/workbench/my-project/risk-action-list.md
workspace/workbench/my-project/state.json
workspace/workbench/my-project/project-experience.md
```

接入后不要直接执行阶段开发。先人工确认 `active-project-intake.md`、`info-alignment.md` 和 `risk-action-list.md`，再生成或修订全周期规划：

```powershell
python scripts/plan_project_lifecycle.py --project my-project --revision-reason "在研项目接入工作台，规划后续开发"
python scripts/plan_project_stage.py --project my-project --stage-id stage-next --title "后续开发阶段"
```

之后再按常规工作台流程执行阶段开发、质量门禁、人工评审和经验沉淀。

## 新资料和需求变更接入

开发过程中，甲方可能随时发送新需求文档、会议纪要、补充说明或直接在聊天里提出新需求。这些内容可以在聊天窗口中触发处理，但必须落到工作台文件中，不能只停留在聊天记录里。

### 1. 接入新资料

建议把甲方新发资料放到：

```text
inputs/project-updates/my-project/
```

然后记录资料接入：

```powershell
python scripts/record_material_intake.py --project my-project --source inputs/project-updates/my-project/2026-05-08-new-prd.md --title "新版本需求文档" --material-type requirement-doc
```

输出到：

```text
outputs/generated/workbench/my-project/material-intake/
|-- MI-2026-001.md
`-- index.md
```

Agent 应在资料接入记录中补充资料摘要、影响范围、待确认问题，并判断是否需要生成需求变更记录。

### 2. 记录需求变更

如果新资料或聊天内容包含新增需求、范围变化或验收标准变化，记录为 CR：

```powershell
python scripts/record_change_request.py --project my-project --title "新增导出功能" --source MI-2026-001 --material-id MI-2026-001 --stage-id stage-1 --request-type new-requirement
```

输出到：

```text
outputs/generated/workbench/my-project/change-requests/
|-- CR-2026-001.md
`-- index.md
```

CR 默认只是进入变更队列，不等于马上开发。人工评审后再决定：

- `accepted-current-stage`：进入当前阶段，必须更新当前阶段计划和质量门禁。
- `accepted-future-stage`：进入后续阶段，必须更新全周期规划或后续阶段计划。
- `needs-clarification`：需要甲方或内部进一步确认。
- `rejected`：不纳入交付范围。
- `done`：已完成并在阶段评审中通过。

### 3. 进入开发流程

需求变更被接受后，再更新规划：

```powershell
python scripts/plan_project_lifecycle.py --project my-project --revision-reason "纳入 CR-2026-001"
python scripts/plan_project_stage.py --project my-project --stage-id stage-1 --title "第一阶段修订"
```

阶段报告必须回写本阶段处理过的 CR 编号、实现结果、测试证据和遗留问题。

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

### 1. 启动项目工作台

自然语言：

```text
请基于 my-project 的配置和前期资料，启动 Agent-First 项目工作台，生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
```

快捷命令：

```text
/init-project-workbench my-project
```

脚本：

```powershell
python scripts/init_project_workbench.py --project my-project
```

### 2. 记录人工确认

自然语言：

```text
我已经确认 my-project 的信息对齐稿，请把当前上下文记录为已确认。
```

脚本：

```powershell
python scripts/confirm_project_context.py --project my-project --decision confirmed
```

### 3. 生成项目全周期规划

自然语言：

```text
请基于 my-project 已确认的上下文，生成项目全周期规划，覆盖交付范围、阶段路线图、里程碑、风险假设和后续调整规则。
```

快捷命令：

```text
/plan-project-lifecycle my-project
```

脚本：

```powershell
python scripts/plan_project_lifecycle.py --project my-project
```

### 4. 生成阶段计划

自然语言：

```text
请基于 my-project 的全周期规划，生成 stage-1 的阶段计划，阶段名称为“第一阶段”。
```

快捷命令：

```text
/plan-project-stage my-project stage-1 第一阶段
```

脚本：

```powershell
python scripts/plan_project_stage.py --project my-project --stage-id stage-1 --title "第一阶段"
```

当前工作台默认推荐一个 Agent 作为阶段开发执行者。多人协作主要在阶段计划确认、阶段报告评审、风险判断和验收授权时进入，不建议多个 Agent 终端同时推进同一阶段开发。

### 5. 执行阶段开发

自然语言：

```text
请按 my-project 的 stage-1 阶段计划执行本阶段工作，完成自检、测试、阶段报告和资产包更新。默认不要修改业务仓库，除非配置和人工授权都允许。
```

快捷命令：

```text
/run-project-stage my-project stage-1
```

脚本：

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

### 6. 检查阶段质量门禁

阶段执行后，先做质量门禁。

自然语言：

```text
请根据 my-project 的 stage-1 阶段计划、阶段报告、测试结果和资产包更新，检查阶段质量门禁，明确是否允许进入人工评审。
```

快捷命令：

```text
/check-stage-quality my-project stage-1
```

脚本：

```powershell
python scripts/check_stage_quality.py --project my-project --stage-id stage-1 --run-commands
```

如果只想做机器校验，不调用 Agent：

```powershell
python scripts/check_stage_quality.py --project my-project --stage-id stage-1 --agent none --run-commands --validate --strict
```

脚本会检查阶段报告、阶段资产包更新和质量门禁是否仍有“待补充 / 待确认 / 待检查 / 待 Agent”等占位内容。质量门禁没有明确写成 `pass` 或 `warning`，且没有明确允许进入人工评审时，不能通过校验。

如果项目配置了 `quality.commands`、`quality.runtime` 或 `quality.smoke`，脚本会实际执行构建、测试、检查、启动服务和冒烟请求，并把结果写入：

```text
outputs/generated/workbench/my-project/stages/stage-1/quality-command-results.md
```

命令、启动检查或冒烟检查失败时，严格模式会阻止进入通过评审。

配置示例：

```yaml
quality:
  commands:
    - name: frontend build
      cwd: ../my-project/frontend
      run: npm run build
      timeout_seconds: 300
  runtime:
    - name: backend service
      cwd: ../my-project/backend
      start: npm run dev
      healthcheck: http://127.0.0.1:8000/health
      expect_status: 200
      timeout_seconds: 60
  smoke:
    - name: api health
      url: http://127.0.0.1:8000/health
      expect_status: 200
      timeout_seconds: 20
```

### 7. 评审阶段结果

自然语言：

```text
请根据 my-project 的 stage-1 阶段报告和人工评审意见，生成阶段评审记录。评审通过后，不要直接进入下一阶段，先提醒我检查全周期规划是否需要调整。
```

快捷命令：

```text
/review-project-stage my-project stage-1 approve
```

脚本：

```powershell
python scripts/review_project_stage.py --project my-project --stage-id stage-1 --decision approve
```

`approve` 前会强制检查质量门禁。若确实需要人工例外，可以显式使用：

```powershell
python scripts/review_project_stage.py --project my-project --stage-id stage-1 --decision approve --skip-quality-gate
```

评审后沉淀阶段经验：

```powershell
python scripts/summarize_stage_experience.py --project my-project --stage-id stage-1
```

阶段经验会写入：

```text
outputs/generated/workbench/my-project/stages/stage-1/experience-notes.md
workspace/workbench/my-project/project-experience.md
outputs/generated/workbench/my-project/rule-candidates.md
```

阶段通过后，不要直接凭聊天继续做下一期。先检查全周期规划是否需要调整：

自然语言：

```text
stage-1 已通过评审，请基于阶段结果检查并修订 my-project 的全周期规划，再给出后续阶段建议。
```

快捷命令：

```text
/plan-project-lifecycle my-project
```

脚本：

```powershell
python scripts/plan_project_lifecycle.py --project my-project --revision-reason "stage-1 评审后调整后续路线"
```

然后再基于最新全周期规划生成下一阶段计划：

```powershell
python scripts/plan_project_stage.py --project my-project --stage-id stage-2 --title "第二阶段"
```

### 8. 结题或阶段性归档

自然语言：

```text
请把 my-project 的工作台过程资料归档为标准项目资产包初稿，保留待人工评审标记。
```

快捷命令：

```text
/finalize-workbench-asset-pack my-project
```

脚本：

```powershell
python scripts/finalize_workbench_asset_pack.py --project my-project
```

归档后继续走已有人工评审定稿流程：

```powershell
python scripts/review_asset_pack.py --project my-project
```

检查工作台状态仍建议用脚本：

```powershell
python scripts/check_project_workbench.py --project my-project
```

## 项目资产包流程

历史项目或已有项目可以直接走资产包流程。

### 初始化资产包

自然语言：

```text
请基于 my-project 的配置、代码仓库和资料目录，生成项目资产包初稿，包括现状审查报告、资产包初稿、资料缺口、风险清单和可复用资产候选。
```

快捷命令：

```text
/init-asset-pack my-project
```

### 保存远程仓库基线

保存远程仓库基线：

```powershell
python scripts/save_remote_baseline.py --project my-project
```

### 增量更新资产包

自然语言：

```text
请检查 my-project 的代码仓库相对上次基线是否有变化，并根据变化范围增量更新项目资产包初稿。
```

快捷命令：

```text
/update-asset-pack my-project
```

脚本：

```powershell
python scripts/update_asset_pack.py --project my-project
```

### 人工评审后定稿

自然语言：

```text
请基于 my-project 的 AI 资产包初稿和人工评审意见，整理正式项目资产包并输出到 reviewed 目录。
```

快捷命令：

```text
/review-asset-pack my-project
```

脚本：

```powershell
python scripts/review_asset_pack.py --project my-project
```

### 在研项目或维护项目体检

自然语言：

```text
请对 my-project 做一次 weekly 项目体检，检查资料沉淀、代码变化、测试缺陷、风险和交付准备状态。
```

快捷命令：

```text
/check-project-health my-project weekly
```

脚本：

```powershell
python scripts/check_project_health.py --project my-project --period weekly
```

## Agent 入口和工作流规则

通用工作流规则：

```text
docs/agent-workflows/
```

Claude Code 入口：

```text
CLAUDE.md
.claude/skills/
```

Codex 入口：

```text
AGENTS.md
```

Claude Code 快捷命令：

资产包相关：

- `/init-asset-pack`
- `/update-asset-pack`
- `/review-asset-pack`
- `/check-project-health`

工作台相关：

- `/start-active-project-workbench`
- `/init-project-workbench`
- `/resume-project-workbench`
- `/record-material-intake`
- `/record-change-request`
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
|-- active-project-intake.md
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
