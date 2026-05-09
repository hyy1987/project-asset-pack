# 生成历史项目资产包初稿

用于基于已有项目代码仓库和资料目录生成项目资产包初稿。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `configs/projects/<project_id>.yaml`
3. `configs/security-rules/<rule_set>.md`
4. 已接入的项目仓库和资料目录
5. 标准资产包模板

## 输出

写入 `outputs/generated/asset-pack/`：

- `review-report.md`
- `asset-pack-draft.md`
- `missing-materials.md`
- `risk-list.md`
- `reusable-assets.md`

## 规则

1. 只读使用业务仓库和资料目录，不修改原项目。
2. 识别代码、需求、设计、接口、数据库、测试、缺陷和交付资料。
3. 对文档缺失或落后于代码的内容，根据代码和资料反推初稿，并标注“待人工确认”。
4. 输出资料缺口、风险和可复用资产候选。
5. 不输出敏感原文。
