# 人工评审后整理正式资产包

用于把 `outputs/generated/asset-pack/` 下的 AI 初稿，结合人工评审意见，整理为正式项目资产包。

## 输入

1. `docs/agent-workflows/workbench-overview.md`
2. `outputs/generated/asset-pack/`
3. 人工评审意见，默认从 `docs/manual/review-comments/<project_id>.md` 读取
4. `configs/projects/<project_id>.yaml`
5. `configs/security-rules/<rule_set>.md`

## 输出

写入 `outputs/reviewed/asset-pack/`。

## 规则

1. AI 初稿不能直接视为定稿。
2. 人工评审意见优先级最高。
3. 未被人工确认的推断保留“待确认”标记。
4. 不得把敏感原文写入 reviewed 输出。
5. 输出必须适合后续交接、复盘和资产复用评估。
