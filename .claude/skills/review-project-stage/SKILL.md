---
name: review-project-stage
description: 基于阶段报告和人工意见生成阶段评审记录，并决定是否进入下一阶段。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# review-project-stage

用于把阶段开发结果推进到人工评审记录。

## 推荐触发方式

```powershell
python scripts\review_project_stage.py --project <project_id> --stage-id <stage_id> --decision approve
```

## 输入

1. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-plan.md`
2. `outputs/generated/workbench/<project_id>/stages/<stage_id>/stage-report.md`
3. 人工评审意见，默认从 `docs/manual/stage-reviews/<project_id>/<stage_id>.md` 读取
4. `templates/workbench/stage-review.md`

## 输出

写入：

```text
outputs/reviewed/workbench/<project_id>/stages/<stage_id>/stage-review.md
```

## 评审规则

- AI 阶段报告不能直接视为通过。
- 必须记录评审结论：approve、changes-requested 或 blocked。
- approve 后才允许进入下一阶段。
- changes-requested 必须列出返工要求。
- blocked 必须列出阻塞原因和需要谁确认。
- 不得把未确认内容写成已确认事实。

