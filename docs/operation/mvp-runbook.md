# MVP 运行手册

## 1. 准备项目配置

复制 `configs/projects/sample-project.yaml`，改成实际项目 ID。`sample-project` 只是占位示例，不代表仓库中自带可运行的业务项目。

```powershell
Copy-Item configs/projects/sample-project.yaml configs/projects/my-project.yaml
```

下文以 `my-project` 作为真实项目 ID 示例。

重点填写：

- `repositories`
- `documents`
- `security.rule_set`
- `output.generated`

## 2. 准备 Claude Code 本地配置

复制：

```powershell
Copy-Item .claude/settings.local.example.json .claude/settings.local.json
```

把项目仓库和资料目录加入 `additionalDirectories`。

## 3. 配置检查

执行：

```powershell
python scripts/check_project_config.py --project my-project
```

这个脚本只检查配置和路径，不生成资产包。

## 4. 启动 Claude Code

```powershell
cd project-asset-pack
claude
```

## 5. 生成资产包初稿

在 Claude Code 会话中执行：

```text
/init-asset-pack my-project
```

或使用自然语言：

```text
请按 .claude/skills/init-asset-pack/SKILL.md 的规则，基于 configs/projects/my-project.yaml 生成项目资产包 MVP 输出。
```

## 6. 人工评审

评审角色：

- 项目负责人：确认业务背景、项目目标、客户约束。
- 技术负责人：确认架构、代码地图、接口和数据库摘要。
- 测试负责人：确认测试、缺陷和质量风险。
- 项目骨干：补充隐性经验。

AI 初稿不能直接作为正式资产包。

## 7. 保存远程仓库基线

初次资产包生成完成后，保存当前远程仓库基线：

```powershell
python scripts\save_remote_baseline.py --project my-project
```

这个脚本会：

- 检查项目配置中的 git 仓库。
- 要求本地工作区干净。
- 执行 `git fetch --prune`。
- 如果本地落后远程，只执行 `git merge --ff-only @{u}`。
- 保存当前同步后的 HEAD 到 `workspace/snapshots/my-project-repo-baseline.json`。

如果只是离线验证脚本流程，可以使用：

```powershell
python scripts\save_remote_baseline.py --project my-project --no-fetch
```

## 8. 检测远程更新

只检测是否存在需要更新资产包的远程提交：

```powershell
python scripts\update_asset_pack.py --project my-project --check-only
```

这个命令会同步远程引用并在安全时快进本地仓库，但不会调用 Claude Code 更新资产包，也不会更新基线。

## 9. 更新资产包

当检测到远程仓库相对基线有新提交时，执行：

```powershell
python scripts\update_asset_pack.py --project my-project
```

脚本会：

1. 读取 `workspace/snapshots/my-project-repo-baseline.json`。
2. 获取并同步远程最新提交。
3. 计算基线 HEAD 到当前 HEAD 的提交和文件变化。
4. 调用 `.claude/skills/update-asset-pack/SKILL.md`。
5. 要求 Claude Code 只更新受影响的资产包章节。
6. 更新成功后记录新的仓库基线。

如果没有检测到新提交，脚本会直接跳过，不重写资产包。

## 10. 强制更新

如果模板、规则或人工修订要求变化，即使远程仓库没有新提交，也可以强制触发：

```powershell
python scripts\update_asset_pack.py --project my-project --force
```

强制更新适合修正文档结构，不适合作为日常默认流程。

## 11. 人工评审后定稿

先补充人工评审意见：

```text
docs/manual/review-comments/my-project.md
```

然后执行：

```powershell
python scripts\review_asset_pack.py --project my-project
```

如果评审意见文件放在其他位置：

```powershell
python scripts\review_asset_pack.py --project my-project --comments docs\manual\review-comments\my-project.md
```

输出目录：

```text
outputs/reviewed/my-project/
├── asset-pack.md
├── review-record.md
├── approved-reusable-assets.md
└── follow-up-actions.md
```

## 12. 项目体检

对在研项目或维护项目执行每周体检：

```powershell
python scripts\check_project_health.py --project my-project --period weekly
```

支持的周期：

- `daily`
- `weekly`
- `milestone`
- `release`
- `handover`

输出目录：

```text
outputs/generated/project-health/my-project/
├── weekly-health-check.md
└── latest-health-check.md
```

体检报告用于发现过程缺口，不替代正式资产包评审。
