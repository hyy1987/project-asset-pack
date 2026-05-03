# init-asset-pack

用于基于 Claude Code 生成单个项目的项目资产包 MVP 初稿。

## 触发方式

```text
/init-asset-pack <project_id>
```

示例：

```text
/init-asset-pack sample-project
```

## 执行前检查

1. 读取 `configs/projects/<project_id>.yaml`。
2. 确认 `security.rule_set` 对应的安全规则存在。
3. 确认输出目录为 `outputs/generated/<project_id>/`。
4. 确认业务仓库和资料目录只读使用，不修改原项目。
5. 如果发现疑似密钥、账号、生产连接串或客户真实数据，只记录风险类型，不复制原文。

## 输入

- 项目配置：`configs/projects/<project_id>.yaml`
- 安全规则：`configs/security-rules/<rule_set>.md`
- 模板：
  - `templates/review-report/review-report.md`
  - `templates/asset-pack/asset-pack-draft.md`
  - `templates/missing-materials/missing-materials.md`
  - `templates/risk-list/risk-list.md`
  - `templates/reusable-assets/reusable-assets.md`
- 通过 `additionalDirectories` 接入的项目仓库和资料目录

## 输出

输出到 `outputs/generated/<project_id>/`：

- `review-report.md`
- `asset-pack-draft.md`
- `missing-materials.md`
- `risk-list.md`
- `reusable-assets.md`

## 工作步骤

### 1. 项目资料盘点

盘点配置中声明的仓库和资料目录，识别：

- 代码仓库
- 需求资料
- 设计资料
- 接口资料
- 数据库资料
- 测试资料
- 缺陷资料
- 交付资料
- 复盘或交接资料

缺失内容写入 `missing-materials.md`。

### 2. 代码结构分析

只做结构化摘要，不做大规模重构建议。输出：

- 仓库用途
- 主要目录
- 主要入口
- 核心模块
- 关键依赖
- 可维护性风险

### 3. 接口和数据库摘要

如果能找到接口定义、路由、OpenAPI、控制器或服务入口，生成接口摘要。

如果能找到数据库迁移、DDL、schema、ORM model 或表结构说明，生成数据库摘要。

无法确认时标注“待确认”，不要猜测。

### 4. 测试与缺陷分析

检查测试用例、测试报告、缺陷记录、已知问题和交付记录。

重点输出：

- 测试资料是否完整
- 是否存在高频缺陷区域
- 是否存在重复问题
- 是否存在验收或交付风险

### 5. 风险识别

风险至少按以下类型归类：

- 资料缺失风险
- 技术维护风险
- 接口理解风险
- 数据库理解风险
- 测试覆盖风险
- 交付交接风险
- 安全与合规风险

每个风险项必须包含证据、影响和建议。

### 6. 可复用资产候选

识别可复用资产候选，包括：

- 通用模块
- 技术方案
- 接口设计
- 数据模型
- 测试用例
- 部署脚本
- 交付文档
- 经验总结

必须标注复用等级：

- 可直接复用
- 可改造复用
- 仅供参考
- 不可跨客户复用

## 质量要求

- 所有结论必须能追溯到代码、资料或明确的“待确认”。
- 不要输出敏感原值。
- 不要把模板留空；没有资料时写明“未发现相关资料”。
- 输出应适合项目负责人、技术负责人、测试负责人共同评审。
