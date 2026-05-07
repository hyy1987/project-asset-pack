# CLAUDE.md

你正在 `project-asset-pack` 中运行 Claude Code。本目录是项目资产包智能体和 Agent-First 软件外包项目工作台的控制面。

## 工作目标

针对已配置项目，完成两类工作。

历史项目或已有项目资产包：

- 项目现状审查报告
- 项目资产包初稿
- 资料缺口清单
- 风险清单
- 可复用资产候选

新外包任务 Agent-First 工作台：

- 接入项目前期资料
- 生成人类和 Agent 的信息对齐稿
- 生成项目启动清单和责任视角问题清单
- 生成项目全周期规划
- 基于全周期规划生成阶段计划和阶段目标
- 按阶段执行开发、自检、测试和资产包更新
- 输出阶段报告并等待人工评审
- 项目结题或阶段性归档时，汇总工作台过程资料生成标准资产包初稿

## 新窗口恢复规则

Claude Code 的聊天历史不是工作台状态来源。新窗口、上下文丢失或中途恢复时，必须先检查工作台状态。

如果 `workspace/workbench/<project_id>/state.json` 存在：

1. 不要提示用户重新初始化。
2. 先运行或建议运行 `python scripts/resume_project_workbench.py --project <project_id>`。
3. 读取 `outputs/generated/workbench/<project_id>/resume-brief.md`。
4. 优先读取 `outputs/reviewed/workbench/<project_id>/` 中的人工确认和评审结果。
5. 读取 `outputs/generated/workbench/<project_id>/lifecycle-plan.md`。
6. 再读取 `outputs/generated/workbench/<project_id>/` 中的 AI 初稿和阶段输出。
7. 根据当前状态继续阶段执行、阶段评审、全周期规划修订、下一阶段规划或归档。

只有状态文件不存在，或人类明确要求“重新初始化/重建工作台”，才运行初始化流程。

## 关键约束

- 默认不修改业务项目仓库；只有项目配置、阶段计划和人类授权都明确允许时，才能执行阶段开发改动。
- 不把 Claude Code 配置写入业务项目仓库。
- 不生成或保留客户敏感原文。
- 不输出账号、密码、Token、密钥、证书、生产连接串。
- 不读取生产数据库备份、客户真实业务数据、合同金额、报价和商业策略。
- 对无法确认的内容必须标记为“待人工确认”，不能编造。
- AI 输出全部视为初稿，正式资产包必须经过人工评审。
- 不绕过人工评审直接进入下一阶段。

## 输入优先级

执行任务时按以下顺序读取上下文：

1. `configs/projects/<project_id>.yaml`
2. `workspace/workbench/<project_id>/state.json`
3. `outputs/generated/workbench/<project_id>/resume-brief.md`
4. `configs/security-rules/<rule_set>.md`
5. `inputs/pre-project/<project_id>/` 或配置中声明的前期资料目录
6. `outputs/reviewed/workbench/<project_id>/` 中已经人工确认的信息
7. `outputs/generated/workbench/<project_id>/lifecycle-plan.md`
8. `outputs/generated/workbench/<project_id>/` 中的 AI 初稿和阶段输出
9. `templates/**`
10. 已通过 `additionalDirectories` 接入的项目仓库和资料目录
11. 用户在当前会话中补充的说明

## 输出要求

资产包默认输出到 `outputs/generated/<project_id>/`。

工作台默认输出到：

- AI 初稿：`outputs/generated/workbench/<project_id>/`
- 人工评审结果：`outputs/reviewed/workbench/<project_id>/`
- 工作台状态：`workspace/workbench/<project_id>/state.json`

所有 Markdown 输出必须：

- 使用清晰标题层级。
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
