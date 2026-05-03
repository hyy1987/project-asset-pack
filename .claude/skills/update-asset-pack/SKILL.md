---
name: update-asset-pack
description: 对比已记录的远程仓库基线和当前同步后的项目仓库版本，按变化范围增量更新项目资产包。
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash(git:*), Bash(python:*)
---

# update-asset-pack

用于基于 Claude Code 增量更新单个项目的项目资产包。

## 使用场景

- 项目仓库在上一次资产包生成后可能有远程更新。
- 团队希望先同步本地仓库到远程最新版本，再判断是否需要更新资产包。
- 项目已经有初始资产包草稿，不需要重新执行完整初始化。

## 仓库上下文

- 控制目录是 `asset_pack_docs/`。
- 项目配置文件是 `configs/projects/<project_id>.yaml`。
- 远程仓库基线文件是 `workspace/snapshots/<project_id>-repo-baseline.json`。
- 生成资产包目录是 `outputs/generated/<project_id>/`。
- 业务仓库通过项目配置中的 `repositories` 声明，并通过 Claude Code `additionalDirectories` 接入。

## 推荐触发方式

优先通过脚本触发：

```powershell
python scripts\update_asset_pack.py --project <project_id>
```

只检查远程更新，不调用 Claude Code：

```powershell
python scripts\update_asset_pack.py --project <project_id> --check-only
```

如果模板、规则或人工修订要求变化，即使业务仓库没有新提交，也可以强制更新：

```powershell
python scripts\update_asset_pack.py --project <project_id> --force
```

如果用户直接在 Claude Code 中调用本 skill，应先提醒用户：常规更新建议使用 `scripts/update_asset_pack.py`，因为脚本会负责远程检查、快进同步、变更对比和基线更新。

## 脚本已完成的前置工作

当本 skill 由 `scripts/update_asset_pack.py` 调用时，脚本已经完成：

1. 读取 `workspace/snapshots/<project_id>-repo-baseline.json` 中的上次资产包基线。
2. 对项目配置中的每个 git 仓库执行 `git fetch --prune`。
3. 检查业务仓库工作区是否干净。
4. 在安全时执行 `git merge --ff-only @{u}`，将本地仓库快进到远程最新版本。
5. 对比上次基线 HEAD 和当前同步后的 HEAD。
6. 整理变更仓库、提交记录、变更文件和同步决策。

因此，本 skill 的职责不是同步仓库，而是根据脚本提供的变更上下文更新资产包。

## 更新规则

- 如果没有检测到相对基线的新提交，不要重写资产包文件。
- 如果只有一个仓库变化，只更新该仓库影响到的资产包章节。
- 对已有文件优先使用 `Edit` 或 `MultiEdit`，不要整篇重写。
- 编辑已有文件前，必须重新读取目标文件当前内容。
- 保留已有的有效人工修订，不要无差别覆盖。
- 不编辑 `outputs/reviewed/`，除非用户明确要求。
- 不修改任何业务项目仓库。
- 不输出账号、密码、Token、密钥、证书、生产连接串或客户原始数据。
- 对无法确认的信息标记为 `待确认`，不要猜测。

## 默认更新范围

默认只更新这些文件：

- `outputs/generated/<project_id>/review-report.md`
- `outputs/generated/<project_id>/asset-pack-draft.md`
- `outputs/generated/<project_id>/missing-materials.md`
- `outputs/generated/<project_id>/risk-list.md`
- `outputs/generated/<project_id>/reusable-assets.md`

如果文件不存在，可以创建；如果文件已存在，只做必要的局部更新。

## 变更映射规则

根据变更文件判断需要更新的资产包章节：

- 代码结构变化：更新代码地图、核心模块说明、技术维护风险、可复用代码候选。
- 接口相关变化：更新接口摘要、接口理解风险、接口资料缺口。
- 数据库相关变化：更新数据库摘要、数据模型风险、数据库资料缺口。
- 测试相关变化：更新测试与缺陷总结、质量风险、可复用测试资产。
- 缺陷或 issue 资料变化：更新缺陷总结、重复问题、质量风险。
- 交付或交接资料变化：更新部署与运行摘要、交接风险、资料缺口。
- 安全相关变化：更新安全与合规风险，但不得输出敏感原值。

无法明确归类时，写入审查报告的“待人工确认事项”。

## 执行流程

1. 读取 `configs/projects/<project_id>.yaml`。
2. 读取项目对应的安全规则文件。
3. 读取脚本传入的变更报告。
4. 读取当前 `outputs/generated/<project_id>/` 下的资产包文件。
5. 判断哪些资产包章节受影响。
6. 局部更新受影响的章节。
7. 在相关文件中增加更新说明，至少包含：
   - 更新时间
   - 变化仓库
   - 上次基线 HEAD
   - 当前同步 HEAD
   - 本次更新章节
   - 是否需要人工复核
8. 对仍无法确认的内容，保留或新增 `待确认` 标记。

## 输出质量要求

每次更新后，应能看清：

- 哪些仓库发生了变化。
- 哪些资产包章节被刷新。
- 哪些风险是新增的。
- 哪些风险仍然存在。
- 哪些资料缺口已经补齐。
- 哪些资料缺口仍待补充。
- 是否需要项目负责人、技术负责人或测试负责人复核。

## 禁止事项

- 禁止因为有远程更新就整篇重写所有资产包文件。
- 禁止把 `outputs/reviewed/` 当成自动更新目标。
- 禁止修改业务仓库代码、配置或资料。
- 禁止输出敏感原文。
- 禁止把未人工确认的可复用资产写成“已批准复用”。
