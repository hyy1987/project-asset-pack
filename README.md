# Project Asset Pack

基于 Claude Code 的项目资产包生成、评审和增量更新工作区。

本目录不放业务代码，只负责：

- Claude Code 配置
- 项目接入配置
- 项目资产包模板
- 安全边界规则
- `/init-asset-pack`、`/update-asset-pack`、`/review-asset-pack`、`/check-project-health` skills
- AI 生成结果、人工评审结果和项目体检报告

## MVP 目标

第一版只跑通一个闭环：

1. 接入一个历史项目的代码仓库和资料目录。
2. 使用 Claude Code 执行 `/init-asset-pack`。
3. 生成项目现状审查报告、资产包初稿、资料缺口清单、风险清单和可复用资产候选。
4. 保存当前远程仓库基线。
5. 后续检测远程仓库更新，安全同步本地仓库，并增量更新资产包初稿。
6. 由人工评审后，输出正式资产包。
7. 对在研项目或维护项目执行定期体检。

## 快速开始

1. 复制本地配置示例：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

2. 按实际项目修改：

- `.claude/settings.local.json`
- `configs/projects/sample-project.yaml`

`sample-project` 只是占位示例。第一次使用前，建议复制一份项目配置并改成真实项目 ID：

```powershell
Copy-Item configs/projects/sample-project.yaml configs/projects/my-project.yaml
```

下文以 `my-project` 作为真实项目 ID 示例。

3. 从本目录启动 Claude Code：

```powershell
cd project-asset-pack
claude
```

4. 在 Claude Code 会话中执行：

```text
/init-asset-pack my-project
```

如果 skill 尚未被 Claude Code 识别，可以直接输入：

```text
请按 .claude/skills/init-asset-pack/SKILL.md 的规则，基于 configs/projects/my-project.yaml 生成项目资产包 MVP 输出。
```

5. 初次生成通过后，保存远程仓库基线：

```powershell
python scripts/save_remote_baseline.py --project my-project
```

如果当前网络不可用，可先用本地已获取的 upstream 引用验证流程：

```powershell
python scripts/save_remote_baseline.py --project my-project --no-fetch
```

6. 后续更新资产包：

```powershell
python scripts/update_asset_pack.py --project my-project
```

只检查是否有更新，不调用 Claude Code：

```powershell
python scripts/update_asset_pack.py --project my-project --check-only
```

7. 人工评审后定稿：

```powershell
python scripts/review_asset_pack.py --project my-project
```

8. 在研项目或维护项目体检：

```powershell
python scripts/check_project_health.py --project my-project --period weekly
```

## MVP 输出

默认输出到：

```text
outputs/generated/my-project/
├── review-report.md
├── asset-pack-draft.md
├── missing-materials.md
├── risk-list.md
└── reusable-assets.md
```

远程仓库基线保存到：

```text
workspace/snapshots/my-project-repo-baseline.json
```

人工评审输出到：

```text
outputs/reviewed/my-project/
├── asset-pack.md
├── review-record.md
├── approved-reusable-assets.md
└── follow-up-actions.md
```

项目体检输出到：

```text
outputs/generated/project-health/my-project/
├── weekly-health-check.md
└── latest-health-check.md
```

## 安全原则

- 不读取生产数据库备份。
- 不输出账号、密码、Token、密钥、证书。
- 不输出客户真实业务数据。
- 不把未经人工确认的可复用资产放入公司级资产库。
- AI 输出只能作为初稿，必须人工评审后才能定版。
