# 记录需求变更

用于把甲方新增需求、需求变更、范围变化、验收标准变化或从新资料中识别出的需求项纳入工作台变更队列。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `workspace/workbench/state.json`，如果存在
4. 需求来源：资料接入记录、会议纪要、聊天补充或甲方说明
5. `templates/workbench/change-request.md`
6. 已有变更队列：`outputs/generated/workbench/change-requests/index.md`，如果存在
7. 当前全周期规划和阶段计划，如果存在

## 输出

写入：

```text
outputs/generated/workbench/change-requests/<request_id>.md
outputs/generated/workbench/change-requests/index.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 每个新增需求或需求变更必须独立编号，不能只留在聊天记录里。
2. 新记录默认状态为 `new`，不得直接进入开发。
3. 进入当前阶段必须人工确认状态为 `accepted-current-stage`，并更新当前阶段计划和质量门禁检查项。
4. 进入后续阶段必须人工确认状态为 `accepted-future-stage`，并更新全周期规划或后续阶段计划。
5. 需要甲方澄清时标记为 `needs-clarification`，并列出待问问题。
6. 拒绝或暂不纳入时标记为 `rejected`，并记录原因。
7. 完成后标记为 `done`，阶段报告必须引用 CR 编号和测试证据。
