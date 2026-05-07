---
name: ask-project-info
description: 根据项目工作台缺口，向人类生成下一轮需要确认的问题清单。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# ask-project-info

用于在信息对齐、阶段计划或阶段执行中发现缺口后，生成面向人类的问题清单。

## 输出

写入：

```text
outputs/generated/workbench/<project_id>/human-questions.md
```

## 要求

- 问题必须按责任视角归类。
- 每个问题说明为什么需要确认。
- 每个问题标注会影响的阶段或交付物。
- 不问已经能从资料中确认的问题。
