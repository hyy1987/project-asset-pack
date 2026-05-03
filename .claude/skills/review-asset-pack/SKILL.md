---
name: review-asset-pack
description: 基于 AI 初稿和人工评审意见，整理正式项目资产包并输出到 outputs/reviewed。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# review-asset-pack

用于把 `outputs/generated/<project_id>/` 下的 AI 初稿，结合人工评审意见，整理为正式项目资产包。

## 使用场景

- `/init-asset-pack` 已经生成资产包初稿。
- 项目负责人、技术负责人、测试负责人或项目骨干已经给出评审意见。
- 需要把 AI 初稿从“待评审”状态推进到“已评审资产包”状态。

## 推荐触发方式

优先通过脚本触发：

```powershell
python scripts\review_asset_pack.py --project <project_id>
```

如果已有人工评审意见文件：

```powershell
python scripts\review_asset_pack.py --project <project_id> --comments docs\manual\review-comments\<project_id>.md
```

## 输入

- 项目配置：`configs/projects/<project_id>.yaml`
- 安全规则：`configs/security-rules/<rule_set>.md`
- AI 初稿目录：`outputs/generated/<project_id>/`
- 人工评审意见：默认从 `docs/manual/review-comments/<project_id>.md` 读取；如果不存在，则标记为“尚未提供人工意见”
- 正式资产包模板：`templates/reviewed-asset-pack/reviewed-asset-pack.md`
- 评审记录模板：`templates/review-record/review-record.md`

## 输出

输出到 `outputs/reviewed/<project_id>/`：

- `asset-pack.md`
- `review-record.md`
- `approved-reusable-assets.md`
- `follow-up-actions.md`

## 评审规则

- AI 初稿不能直接原样定稿。
- 对已有人工意见必须逐条吸收或说明未采纳原因。
- 对仍缺少人工确认的信息，保留 `待确认` 标记。
- 不得把 AI 推测内容写成已确认事实。
- 不得把未确认的可复用资产写成“已批准复用”。
- 不得输出敏感原文。
- 不修改 `outputs/generated/` 中的初稿，正式结果只写入 `outputs/reviewed/`。

## 人工角色分工

- 项目负责人：确认业务背景、项目目标、客户约束、交付边界。
- 技术负责人：确认系统结构、代码地图、核心模块、接口和数据库摘要。
- 测试负责人：确认测试覆盖、缺陷总结、质量风险。
- 项目骨干：补充资料中无法体现的隐性经验和维护注意事项。

## 执行流程

1. 读取项目配置和安全规则。
2. 读取 `outputs/generated/<project_id>/` 下的全部初稿。
3. 读取人工评审意见文件；如果不存在，继续生成评审记录，但明确标记“未收到人工评审意见”。
4. 生成正式 `asset-pack.md`。
5. 生成 `review-record.md`，说明：
   - 评审来源
   - 已确认内容
   - 待确认内容
   - 已采纳意见
   - 未采纳意见及原因
6. 生成 `approved-reusable-assets.md`。
7. 生成 `follow-up-actions.md`。

## 输出质量要求

正式资产包必须能回答：

- 非原项目成员是否能理解项目基本情况。
- 新人是否能根据资产包找到关键代码、接口、数据库和运行资料。
- 项目风险是否被清楚标注。
- 哪些经验可以复用，哪些只能参考。
- 哪些资料仍需补齐。

