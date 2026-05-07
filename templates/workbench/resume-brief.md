# 工作台恢复摘要

项目 ID：{{project_id}}

生成时间：{{generated_at}}

## 当前状态

- 工作台状态：{{status}}
- 当前阶段：{{current_stage_id}}
- 最近通过阶段：{{last_approved_stage_id}}
- 状态文件：{{state_file}}

## 前期资料

- 前期资料目录：{{pre_project_materials}}
- 已识别资料：

{{material_list}}

## 已确认资料

{{reviewed_outputs}}

## AI 初稿资料

{{generated_outputs}}

## 阶段记录

{{stage_summary}}

## 建议下一步

{{next_action}}

## 新窗口继续规则

1. 如果状态文件存在，不要重新初始化工作台。
2. 先读取本恢复摘要、状态文件、人工评审输出，再读取 AI 初稿输出。
3. 当前阶段已经有计划时，继续阶段执行或阶段评审。
4. 当前阶段已经通过评审时，规划下一阶段。
5. 只有状态文件不存在，或人类明确要求重建时，才重新运行初始化流程。
