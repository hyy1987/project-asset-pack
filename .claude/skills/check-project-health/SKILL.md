---
name: check-project-health
description: 对正在开发或维护中的项目执行定期体检，检查项目资料沉淀、代码变化、测试缺陷和交付准备状态。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash(git:*)
---

# check-project-health

用于基于 Claude Code 对在研项目或维护项目进行定期体检。

## 使用场景

- 每周项目例会前。
- 版本提测前。
- 验收前。
- 项目结题前。
- 维护项目发生一轮较大变更后。

## 推荐触发方式

```powershell
python scripts\check_project_health.py --project <project_id> --period weekly
```

可选周期：

- `daily`
- `weekly`
- `milestone`
- `release`
- `handover`

## 输入

- 项目配置：`configs/projects/<project_id>.yaml`
- 安全规则：`configs/security-rules/<rule_set>.md`
- 项目仓库和资料目录
- 当前生成资产包：`outputs/generated/<project_id>/`
- 上一次体检报告：`outputs/generated/project-health/<project_id>/latest-health-check.md`
- 体检模板：`templates/health-check/health-check.md`

## 输出

输出到 `outputs/generated/project-health/<project_id>/`：

- `<period>-health-check.md`
- `latest-health-check.md`

## 体检范围

必须覆盖：

- 需求变更是否有记录。
- 技术决策是否有沉淀。
- 接口变化是否同步更新。
- 数据库变化是否同步更新。
- 测试用例是否覆盖关键风险。
- 缺陷是否暴露重复问题。
- 交付资料是否持续补齐。
- 当前资产包是否还能支持交接、维护和复用。

## 体检规则

- 体检不是重新生成完整资产包。
- 优先发现过程缺口和风险。
- 输出必须可转化为项目待办事项。
- 不修改业务项目仓库。
- 不输出敏感原文。
- 对无法确认的内容标记为 `待确认`。

## 执行流程

1. 读取项目配置和安全规则。
2. 读取当前资产包初稿或已评审资产包。
3. 检查仓库当前状态和最近变化摘要。
4. 对照体检范围逐项检查。
5. 输出健康评分、主要风险、资料缺口、建议动作和责任角色。
6. 更新 `latest-health-check.md`。

## 输出质量要求

体检报告必须能回答：

- 当前项目是否适合继续推进到下一阶段。
- 哪些资料沉淀不足。
- 哪些技术或质量风险需要立即处理。
- 哪些问题需要项目负责人、技术负责人或测试负责人确认。
- 下一次体检前应该完成哪些动作。

