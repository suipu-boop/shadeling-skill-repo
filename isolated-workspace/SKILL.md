---
name: 隔离工作区
version: 1.0.0
author: Shadeling 策展
summary: 开工前先建隔离工作区，别在主检出上动土
description: 开始需要与当前工作区隔离的功能开发之前、或执行实施计划之前使用：建 git worktree 隔离工作区，验证干净基线。
category: 开发
tags: git, worktree, 隔离, 工作区
license: MIT
trigger: 建个工作区 / 隔离开发 / 别污染主分支 / 新开分支干活
source: third_party
upstream: https://github.com/obra/superpowers
upstream_commit: 8ca22dba9a94
converted_at: 2026-10-01
converted_by: Shadeling 策展（设计意图参考 obra/superpowers/using-git-worktrees，MIT）
---

## 概述

确保工作发生在隔离的工作区里。

**核心原则：** 先检测已有隔离 → 再用平台原生工具 → 最后 git worktree 兜底。绝不跟运行环境较劲。

## 第 0 步：检测已有隔离

**创建任何东西之前，先检查你是不是已经在一个隔离工作区里。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模块守卫：** 在 git 子模块里 `GIT_DIR != GIT_COMMON` 同样为真。下结论「已在 worktree」之前，先确认不是在子模块里：

```bash
# 有输出 = 你在子模块里，不是 worktree——按普通仓库处理
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（且不是子模块）：** 你已经在链接的 worktree 里。跳到第 2 步（项目设置），**不要**再建一个。

**如果 `GIT_DIR == GIT_COMMON`（或在子模块里）：** 你在普通仓库检出里。

用户的指令里没写工作区偏好的，先征得同意再建：「要不要我建一个隔离的 worktree？可以保护你当前分支不被改动。」已有声明的偏好直接照办，不再问。用户拒绝就在原地工作，跳到第 2 步。

## 第 1 步：建隔离工作区

### 1a. 原生 worktree 工具（优先）

用户已同意建隔离工作区。你手里有建 worktree 的原生工具或命令吗（名字类似 EnterWorktree / WorktreeCreate、`/worktree` 命令、`--worktree` 参数）？有就用它，跳到第 2 步。

原生工具自动处理目录摆放、分支创建和清理。有原生工具还手动 `git worktree add`，会造出运行环境看不见也管不了的幻影状态。

### 1b. git worktree 兜底

**只在 1a 不适用时用**——没有原生 worktree 工具才手动建。

**目录选择**（按优先级，用户明示的偏好永远压过文件系统现状）：

1. 指令文件里声明过的 worktree 目录偏好——有就直接用，不问。
2. 项目里已有的 worktree 目录：
   ```bash
   ls -d .worktrees 2>/dev/null     # 首选（隐藏）
   ls -d worktrees 2>/dev/null      # 备选
   ```
   两个都存在时 `.worktrees` 赢。
3. 都没有，默认项目根的 `.worktrees/`。

**安全校验（仅项目内目录）——建之前必须确认目录已被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**没被忽略：** 先加进 .gitignore，提交，再继续。

**为什么关键：** 防止把 worktree 的整个内容误提交进仓库。

**创建：**

```bash
path="$LOCATION/$BRANCH_NAME"
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**沙箱兜底：** `git worktree add` 因权限错误失败（沙箱拒绝），就告诉用户沙箱挡了 worktree 创建，改在当前目录工作，原地跑设置和基线测试。

## 第 2 步：项目设置

自动探测并跑合适的安装：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi
# Rust
if [ -f Cargo.toml ]; then cargo build; fi
# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
# Go
if [ -f go.mod ]; then go mod download; fi
```

## 第 3 步：验证干净基线

跑测试，确保工作区起点是干净的：

**测试挂了：** 报告失败，问用户是继续还是先查。

**测试过了：** 报告就绪。

```
Worktree ready at <完整路径>
Tests passing (<N> 个测试，0 失败)
Ready to implement <功能名>
```

## 速查表

| 情况 | 动作 |
|---|---|
| 已在链接 worktree | 跳过创建（第 0 步） |
| 在子模块里 | 按普通仓库处理（第 0 步守卫） |
| 有原生 worktree 工具 | 用它（第 1a 步） |
| 没有原生工具 | git worktree 兜底（第 1b 步） |
| `.worktrees/` 存在 | 用它（校验已忽略） |
| `worktrees/` 存在 | 用它（校验已忽略） |
| 都存在 | 用 `.worktrees/` |
| 都不存在 | 查指令文件，再默认 `.worktrees/` |
| 目录没被忽略 | 加 .gitignore + 提交 |
| 创建时权限报错 | 沙箱兜底，原地工作 |
| 基线测试挂 | 报告失败 + 问 |

## 常见借口

| 借口 | 现实 |
|---|---|
| 「我显然不在 worktree 里，不用查」 | 跑第 0 步。环境建的隔离和子模块都会骗过肉眼；检测命令说了算。 |
| 「直接 git worktree add 比找原生工具快」 | 原生工具管着摆放、建分支和清理。绕过它第一大错——幻影状态你的环境看不见也管不了。 |
| 「worktree 目录肯定已经被忽略了」 | 跑 `git check-ignore`。没被忽略的 worktree 目录会把整棵树提交进仓库。 |
| 「随便什么目录名都行」 | 明示指令 > 已有项目内目录 > `.worktrees/` 默认。 |
| 「工作区是新的，基线测试回头跑」 | 脏基线让之后每个失败都说不清。现在就跑；要不要带病前进由用户定。 |
