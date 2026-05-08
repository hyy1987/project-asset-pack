# check-stage-quality

检查一个阶段是否满足进入人工评审前的质量门禁。

## 用法

```text
/check-stage-quality <project_id> <stage_id>
```

示例：

```text
/check-stage-quality sample-project stage-1
```

## 规则来源

这是 Claude Code 快捷入口。通用规则以 `docs/agent-workflows/` 为准。

执行时必须先读取：

1. `docs/agent-workflows/workbench-overview.md`
2. `docs/agent-workflows/check-stage-quality.md`
