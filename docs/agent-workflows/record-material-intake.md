# 记录新资料接入

用于把甲方新发文档、会议纪要、接口说明、原型、测试说明或聊天补充资料接入工作台。资料接入本身不等于需求变更通过。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `workspace/workbench/state.json`，如果存在
4. 新资料来源：文件、目录、链接或聊天补充说明
5. `templates/workbench/material-intake.md`
6. 已有资料接入索引：`outputs/generated/workbench/material-intake/index.md`，如果存在
7. 已有需求变更队列：`outputs/generated/workbench/change-requests/index.md`，如果存在

## 输出

写入：

```text
outputs/generated/workbench/material-intake/<material_id>.md
outputs/generated/workbench/material-intake/index.md
```

更新 `workspace/workbench/state.json`。

## 规则

1. 资料接入只记录来源、摘要、影响和待确认问题，不直接改变交付范围。
2. 如果资料中包含新增需求、范围变化或验收标准变化，应建议生成一条或多条需求变更记录。
3. 不复制未脱敏原文到输出目录，只引用来源路径或说明。
4. 如果资料影响当前阶段，必须标记需要人工确认是否调整阶段计划。
5. 如果资料影响后续阶段，必须标记需要人工确认是否更新全周期规划。
6. 无法确认的内容必须保留“待确认”。
