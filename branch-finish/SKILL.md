---
name: 分支收尾
version: 1.0.0
author: Shadeling 策展
summary: 全绿后给选项，等用户拍板收尾
description: 实现完成、测试全绿、需要决定怎么整合工作时使用：验证测试 → 检测环境 → 给选项 → 执行选择 → 清理。
category: 开发
tags: git, 分支, 合并, 收尾
license: MIT
trigger: 干完了怎么交 / 合并还是建请求 / 这个分支怎么办 / 活干完了
source: third_party
upstream: https://github.com/obra/superpowers
upstream_commit: 8ca22dba9a94
converted_at: 2026-10-01
converted_by: Shadeling 策展（设计意图参考 obra/superpowers/finishing-a-development-branch，MIT）
---

## 概述

**核心原则：** 验证测试 → 检测环境 → 给出选项 → 执行选择 → 清理。

## 第 1 步：验证测试

跑项目全量测试套件。

**测试挂了：** 报告失败并停下——全绿之后才谈选项：

```
测试挂了（<N> 个失败）。必须先修完才能收尾：
[展示失败]
```

**测试过了：** 进第 2 步。

## 第 2 步：检测环境

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# 趁还在工作区里先记下——第 6 步清理要在换目录之后用
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

| 状态 | 菜单 | 清理 |
|---|---|---|
| `GIT_DIR == GIT_COMMON`（普通仓库） | 标准 3 项 | 无 worktree 可清 |
| `GIT_DIR != GIT_COMMON`，具名分支 | 标准 3 项 | 按来源清（第 6 步） |
| `GIT_DIR != GIT_COMMON`，游离 HEAD | 缩减 2 项（无合并） | 外部代管——原地保留 |

## 第 3 步：确定基线分支

基线分支 = 这个分支当初从哪分出来的——通常在计划、对话或分支的 upstream 里有名字。不确定就问：「这个分支是从〈你的最佳猜测〉分出来的，对吗？」**合并前确认**：合错基线代价很高。

## 第 4 步：给选项

**普通仓库和具名分支 worktree——原样给这 3 项：**

```
实现完成。接下来怎么处理？

1. 本地合并回 <基线分支>
2. 推送并建 Pull Request
3. 分支原样保留（我回头处理）

选哪个？
```

**游离 HEAD——原样给这 2 项：**

```
实现完成。你在游离 HEAD 上（外部代管的工作区）。

1. 推为新分支并建 Pull Request
2. 原样保留（我回头处理）

选哪个？
```

菜单**原样呈现**，逐字来自上面的列表。等用户答复——**整合决策是用户的**。丢弃工作只在用户明确要求时发生（见下）。

## 第 5 步：执行选择

### 选项 1：本地合并

```bash
# 拿主仓库根，保证 CWD 安全
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# 先合并——确认成功再删任何东西
git checkout <基线分支>
git pull
git merge <功能分支>

# 在合并结果上再跑一遍测试
<测试命令>
```

合并结果测试挂了：停下，worktree 和分支原地保留，排查——没推送过，合并在本地，可回退。

合并结果全绿：清理 worktree（第 6 步），然后删分支：

```bash
git branch -d <功能分支>
```

### 选项 2：推送并建 PR

```bash
git push -u origin <功能分支>
# 游离 HEAD 上，给远端分支起名：
# git push origin HEAD:refs/heads/<新分支名>
```

然后按基线分支建 PR/MR——用平台的 CLI 或推送后打印的创建链接，遵循仓库的 PR 模板惯例，把 URL 报给用户。

**保留 worktree**——用户要在里面迭代 PR 反馈。

### 选项 3：原样保留

报告：「保留分支〈名字〉。Worktree 保留在〈路径〉。」

### 用户明确要求丢弃时

这条路**只**在用户明确说扔掉时存在。先确认：

```
这将永久删除：
- 分支 <名字>
- 全部提交：<提交清单>
- <路径> 的 worktree

输入 discard 确认。
```

等到**逐字**的确认后：回主仓库根，清理 worktree（第 6 步），强删分支：

```bash
git branch -D <功能分支>
```

## 第 6 步：清理工作区

**只在选项 1 和已确认的丢弃后运行。** 选项 2、3 永远保留 worktree。两种情况都已切到主仓库根——worktree 的移除必须从外面执行——用的是第 2 步换目录**之前**记下的 `GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH`。

- `GIT_DIR == GIT_COMMON`：普通仓库，没有 worktree。完事。
- `WORKTREE_PATH` 在 `.worktrees/` 或 `worktrees/` 下：本技能建的，自己清：
  ```bash
  git worktree remove "$WORKTREE_PATH"
  git worktree prune   # 自愈：清掉失效登记
  ```

**移除被拒**（`contains modified or untracked files`）：worktree 里有别处没有的文件——没提交的计划、笔记、草稿。**绝不擅自 `--force`**。展示利害，问用户：提交到分支 / 挪回主仓库根 / 删掉（不可恢复）。执行选择后再移除。

**其余情况：** 宿主环境代管的工作区——原地保留。平台有工作区退出工具就用它。

## 速查表

| 选项 | 合并 | 推送 | 留 worktree | 清分支 |
|---|---|---|---|---|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 建 PR | - | ✓ | ✓ | - |
| 3. 原样保留 | - | - | ✓ | - |
| 丢弃（仅明确要求） | - | - | - | ✓（强删） |

## 常见借口

| 借口 | 现实 |
|---|---|
| 「测试这个会话里早就过了」 | 在**即将整合的这棵树**上跑。绿只证明它跑过的那棵树。 |
| 「他们肯定想合并」 | 整合是用户的决策。给菜单，等答复。 |
| 「这功能他们应该用完了，我提议删掉吧」 | 菜单按原文给全。丢弃只在用户亲口要求时发生。 |
| 「『行，删了吧』算确认吧」 | 只有逐字输入 `discard` 才授权删除。 |
| 「PR 都提了，worktree 现在是累赘」 | PR 反馈就在那个 worktree 里改。工作落地前它一直在。 |
