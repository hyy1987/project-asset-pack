---
name: init-project-workbench
description: 接入新外包任务前期资料，生成信息对齐稿、项目启动清单、责任视角问题清单、资产包骨架和风险行动清单。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS
---

# init-project-workbench

用于启动 Agent-First 软件外包项目工作台。

## 触发方式

```text
/init-project-workbench <project_id>
```

推荐通过脚本触发：

```powershell
python scripts\init_project_workbench.py --project <project_id>
```

## 输入

按顺序读取：

1. `configs/projects/<project_id>.yaml`
2. `configs/security-rules/<rule_set>.md`
3. `inputs/pre-project/<project_id>/` 或配置中声明的前期资料目录
4. `templates/workbench/*.md`
5. 用户在会话中补充的说明

## 输出

写入 `outputs/generated/workbench/<project_id>/`：

- `info-alignment.md`
- `project-kickoff-checklist.md`
- `responsibility-questions.md`
- `asset-pack-skeleton.md`
- `risk-action-list.md`

同时不得修改业务项目仓库。

## 执行规则

1. 先盘点前期资料，只列文件名、资料类型和用途，不复制敏感原文。
2. 从资料中抽取已知事实、待确认问题、风险假设和下一步行动。
3. 对无法确认的内容标注“待人工确认”，不得编造。
4. 输出必须让人类可以直接评审和修正。
5. 如果发现账号、密码、Token、密钥、证书、生产连接串、客户真实业务数据、合同金额或报价策略，只记录敏感类型和资料类别，不写原值。
6. 生成后提醒人类把确认意见写入 `docs/manual/workbench-confirmations/<project_id>.md`，或直接在会话中补充。

