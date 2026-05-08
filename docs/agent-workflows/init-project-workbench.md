# 启动项目工作台

用于接入新外包任务前期资料，生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `configs/security-rules/<rule_set>.md`
4. `inputs/pre-project/<project_id>/` 或配置中声明的前期资料目录
5. `templates/workbench/info-alignment.md`
6. `templates/workbench/project-kickoff-checklist.md`
7. `templates/workbench/responsibility-questions.md`
8. `templates/workbench/asset-pack-skeleton.md`
9. `templates/workbench/risk-action-list.md`

## 输出

写入 `outputs/generated/workbench/<project_id>/`：

- `info-alignment.md`
- `project-kickoff-checklist.md`
- `responsibility-questions.md`
- `asset-pack-skeleton.md`
- `risk-action-list.md`

更新 `workspace/workbench/<project_id>/state.json`。

## 规则

1. 只盘点允许进入工作区的前期资料，不复制敏感原文。
2. 从资料中抽取已知事实、待确认问题、风险假设和下一步行动。
3. 无法确认的内容标注“待人工确认”。
4. 初始化只做信息对齐和启动资料整理，不生成全周期规划。
5. 生成后提醒人类确认上下文，再进入全周期规划。
