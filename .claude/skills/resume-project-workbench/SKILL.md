---
name: resume-project-workbench
description: 在新的 Claude Code 会话中恢复 Agent-First 工作台上下文，读取状态、已评审材料、阶段输出和建议下一步，避免重复初始化。
allowed-tools: Read, Write, Edit, Glob, Grep, LS
---

# resume-project-workbench

用于在 Claude Code 新窗口或聊天历史丢失后继续同一个项目。

## 推荐触发方式

```powershell
python scripts\resume_project_workbench.py --project <project_id>
```

## 输入

按顺序读取：

1. `configs/projects/<project_id>.yaml`
2. `workspace/workbench/<project_id>/state.json`
3. `outputs/reviewed/workbench/<project_id>/`
4. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`
5. `outputs/generated/workbench/<project_id>/`
6. 当前阶段的 `stage-plan.md`、`stage-report.md`、`asset-pack-update.md`
7. `outputs/generated/workbench/<project_id>/resume-brief.md`

## 输出

更新或生成：

```text
outputs/generated/workbench/<project_id>/resume-brief.md
```

不得覆盖 `outputs/reviewed/` 中的人工确认和评审记录。

## 执行规则

1. 如果 `workspace/workbench/<project_id>/state.json` 存在，禁止提示用户重新初始化。
2. 优先相信 `outputs/reviewed/workbench/<project_id>/` 中的人工确认和评审记录。
3. `outputs/generated/workbench/<project_id>/` 中的内容只视为 AI 初稿。
4. 根据状态文件判断项目处于初始化、信息确认、阶段计划、阶段执行、阶段评审、阶段通过或资产包归档中的哪一步。
5. 明确告诉用户当前状态、当前阶段、已有产物、缺口和下一步建议。
6. 如果全周期规划缺失，优先建议生成全周期规划，不要直接继续下一阶段开发。
7. 如果当前阶段已有计划但没有报告，建议继续运行阶段执行。
8. 如果当前阶段已有报告但没有人工评审，建议进入阶段评审。
9. 如果当前阶段已通过评审，先建议检查并必要时修订全周期规划，再规划下一阶段或进行阶段性归档。
10. 只有状态文件不存在，或用户明确说“重新初始化/重建工作台”，才建议执行初始化。
