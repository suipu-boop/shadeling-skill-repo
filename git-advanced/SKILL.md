---
name: Git 高级操作
version: 1.0.0
author: Shadeling 策展
summary: 改历史、摘提交、二分找回，reflog 是安全网
description: 要整理提交历史、跨分支摘取改动、定位坏提交或抢救误删时使用：交互式 rebase、cherry-pick、bisect、worktree、reflog。
category: 开发
tags: Git, 版本控制, 工作流
license: MIT
trigger: 整理提交 / git 高级 / 摘提交 / 找回误删
---

# Git 高级操作

五件兵器：rebase 改历史、cherry-pick 摘提交、bisect 定位坏点、worktree 多线并行、reflog 兜底救场。

## 交互式 rebase：历史编辑瑞士军刀

`git rebase -i HEAD~5`（或 `-i $(git merge-base HEAD main)` 整条分支）：

- **pick** 原样保留 / **reword** 改提交信息 / **edit** 改提交内容
- **squash** 并入上一条且保留信息 / **fixup** 并入但丢弃信息 / **drop** 删掉

用途：合并「改错字」碎提交、拆分大提交、写干净的历史。**铁律：已推送的共享分支不动历史**，只整自己未推送的。

## cherry-pick：跨分支摘提交

```bash
git cherry-pick abc123        # 单个
git cherry-pick abc123..def456  # 区间（前开后闭）
git cherry-pick -n abc123     # 只暂存不提交
```

hotfix 带回主线、把某个修复复制到多个发布分支，都用它。冲突处理与普通合并相同。

## bisect：二分定位坏提交

```bash
git bisect start
git bisect bad            # 当前是坏的
git bisect good v1.0.0    # 这个版本是好的 → 自动检出中间提交
# 测试：好 → git bisect good；坏 → git bisect bad
git bisect reset          # 结束
```

与调试功夫的二分思路同源：每步排除一半历史，百个提交七八步锁定。

## worktree：多分支并行检出

```bash
git worktree add ../project-hotfix -b hotfix/urgent main
git worktree list / remove / prune
```

不用 stash、不用切分支，主目录跑长任务、旁边目录修急件，两边互不干扰。适合「写到一半来了 hotfix」。

## reflog：误删后悔药

reflog 记录所有引用移动——**被删的提交也在**：

```bash
git reflog                          # 找到想要的那个 hash
git branch recovered abc123         # 从任意历史点建分支救回
```

reset --hard 之后、rebase 出错之后、分支删了之后——先看 reflog，九成能救。

## 常见坑

- 对已推送分支 rebase = 强推 = 队友地狱；真要强推用 `--force-with-lease`。
- rebase 中途冲突解决错了会连环错；每步确认再 `git rebase --continue`。
- bisect 用的测试命令必须是**自动可判定的**（退出码说话），手点的不行。

## 抢救速查

误删分支 → reflog | reset 过头 → reflog | rebase 乱了 → `git reflog` 找 rebase 前的 HEAD | 提交错分支 → cherry-pick 走人。
