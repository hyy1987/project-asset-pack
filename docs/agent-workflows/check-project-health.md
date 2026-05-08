# 项目体检

用于对在研项目或维护项目执行定期体检，检查资料沉淀、代码变化、测试缺陷和交付准备状态。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `configs/security-rules/<rule_set>.md`
4. 项目仓库和资料目录
5. 当前生成资产包：`outputs/generated/<project_id>/`
6. 上一次体检报告，如果存在
7. `templates/health-check/health-check.md`

## 输出

写入 `outputs/generated/project-health/<project_id>/`：

- `<period>-health-check.md`
- `latest-health-check.md`

## 规则

1. 检查项目资料沉淀、代码变化、测试缺陷、交付准备和风险。
2. 对资料缺口给出影响和建议补齐方式。
3. 对风险给出证据、影响和建议处理方式。
4. 不输出敏感原文。
