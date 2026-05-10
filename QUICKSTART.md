# Project Asset Pack 快速开始

这份文档只保留日常最常用的自然语言使用方法。完整脚本参数、快捷命令、离线验证和输出目录见 [USAGE.md](USAGE.md)。

## 基本原则

优先在 Claude Code 或 Codex 里用自然语言说明目标，让 Agent 读取 `docs/agent-workflows/` 中的规则并生成文件。自然语言入口比直接记脚本更适合日常工作，因为它能同时携带项目背景、人工判断和当前阶段目标。

常用项目名示例统一写成 `my-project`，实际使用时替换为 `configs/projects/<project_id>.yaml` 中的项目 ID。

## 新项目启动工作台

适用于项目刚开始、有前期资料需要整理和对齐的场景。

```text
请基于 my-project 的配置和前期资料，启动 Agent-First 项目工作台，完成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
```

生成后先人工检查信息对齐稿、风险行动清单和待确认问题，不要直接进入开发。

## 在研项目接入工作台

适用于项目已经在开发或维护中，现在希望把后续工作纳入 Agent-First 工作台管理的场景。

```text
请把 my-project 这个在研项目接入 Agent-First 工作台，读取项目配置、业务仓库状态、资料目录，以及可选的已有资产包，生成接入摘要、信息对齐稿、风险行动清单和后续规划输入。
```

接入后先人工确认 `01-active-project-intake.md`、`02-info-alignment.md` 和 `06-risk-action-list.md`，再生成或修订全周期规划。

## 恢复工作台上下文

适用于新开 Agent 窗口、聊天历史丢失、或需要确认当前进度的场景。

```text
请恢复 my-project 的工作台上下文，先读取状态文件、人工评审结果、全周期规划和恢复摘要，然后告诉我当前阶段和下一步。
```

只有状态文件不存在，或人工明确要求重建，才重新初始化工作台。

## 生成项目全周期规划

项目信息对齐并人工确认后，用这条指令生成或修订整体路线图。

```text
请基于 my-project 已确认的上下文，生成项目全周期规划，覆盖交付范围、阶段路线图、里程碑、风险假设和后续调整规则。
```

阶段通过评审后，也先回到全周期规划检查是否需要调整：

```text
stage-1 已通过评审，请基于阶段结果检查并修订 my-project 的全周期规划，再给出后续阶段建议。
```

## 生成阶段计划

全周期规划确认后，为具体阶段生成阶段计划。

```text
请基于 my-project 的全周期规划，生成 stage-1 的阶段计划，阶段名称为“第一阶段”。
```

阶段计划应明确目标、范围、验收标准、允许修改的仓库、测试要求和人工检查点。

## 执行阶段工作

阶段计划确认后，再让 Agent 执行阶段工作。

```text
请按 my-project 的 stage-1 阶段计划执行本阶段工作，完成自检、测试、阶段报告和资产包更新。默认不要修改业务仓库，除非配置和人工授权都允许。
```

默认不修改业务项目仓库。需要修改代码时，必须同时满足项目配置允许、阶段计划允许、人工明确授权。

## 检查阶段质量门禁

阶段执行完成后，先做质量门禁，再进入人工评审。

```text
请根据 my-project 的 stage-1 阶段计划、阶段报告、测试结果和资产包更新，检查阶段质量门禁，明确是否允许进入人工评审。
```

质量门禁应检查测试证据、未验证内容、占位内容、风险和必须人工检查项。

## 评审阶段结果

人工评审阶段报告和质量门禁后，让 Agent 生成阶段评审记录。

```text
请根据 my-project 的 stage-1 阶段报告和人工评审意见，生成阶段评审记录。评审通过后，不要直接进入下一阶段，先提醒我检查全周期规划是否需要调整。
```

评审通过后，继续沉淀阶段经验：

```text
请总结 my-project 的 stage-1 阶段经验，更新项目经验库和长期规则候选。
```

## 接入新资料或需求变更

开发过程中收到新需求文档、会议纪要、补充说明或聊天里的需求变化时，先落到工作台文件，不要只停留在聊天记录。

```text
请把这份新资料接入 my-project 工作台，生成资料接入记录，摘要主要内容、影响范围、待确认问题，并判断是否需要生成需求变更记录。
```

如果确认为新增需求、范围变化或验收标准变化，再说：

```text
请为 my-project 记录一条需求变更，标题是“新增导出功能”，来源是刚才的资料接入记录，先进入变更队列，等待人工确认是否纳入当前阶段。
```

需求变更被接受后，再修订全周期规划或阶段计划，不要直接开发。

## 结题或阶段性归档

项目结题或需要阶段性沉淀时，把工作台过程资料归档为标准项目资产包初稿。

```text
请把 my-project 的工作台过程资料归档为标准项目资产包初稿，保留待人工评审标记。
```

归档结果仍是 AI 初稿，必须经过人工评审后才能进入 reviewed 目录。

## 历史项目生成资产包

适用于交接项目、历史项目、或暂不接入工作台的项目。

```text
请基于 my-project 的配置、代码仓库和资料目录，生成项目资产包初稿，包括现状审查报告、资产包初稿、资料缺口、风险清单和可复用资产候选。
```

人工评审后定稿：

```text
请基于 my-project 的 AI 资产包初稿和人工评审意见，整理正式项目资产包并输出到 reviewed 目录。
```

## 未接入工作台项目体检

仅用于暂不接入工作台的在研或维护项目。已经接入工作台的项目，应通过阶段质量门禁、风险行动清单、CR 队列和阶段评审完成健康检查。

```text
请对 my-project 做一次 weekly 项目体检，检查资料沉淀、代码变化、测试缺陷、风险和交付准备状态。
```

## 常用快捷命令对照

Claude Code 中可以用 slash command 快速触发固定流程：

- `/init-project-workbench my-project`
- `/start-active-project-workbench my-project`
- `/resume-project-workbench my-project`
- `/plan-project-lifecycle my-project`
- `/plan-project-stage my-project stage-1 第一阶段`
- `/run-project-stage my-project stage-1`
- `/check-stage-quality my-project stage-1`
- `/review-project-stage my-project stage-1 approve`
- `/finalize-workbench-asset-pack my-project`
- `/init-asset-pack my-project`
- `/update-asset-pack my-project`
- `/review-asset-pack my-project`
- `/check-project-health my-project weekly`
