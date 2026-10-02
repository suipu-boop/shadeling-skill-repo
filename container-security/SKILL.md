---
name: 容器安全
version: 1.0.0
author: Shadeling 策展
summary: 纵深防御：Pod 标准、网络默认拒绝、RBAC 最小权限
description: 加固容器/K8s 集群安全、做多租户隔离时使用：Pod 安全三档标准、网络策略默认拒绝、RBAC 最小权限、准入控制。
category: 安全
tags: 安全, 容器, K8s
license: MIT
trigger: 容器安全 / K8s 加固 / 网络隔离 / pod 安全
---

# 容器安全

容器安全四层纵深：**Pod 规范 → 网络隔离 → 权限控制 → 准入把关**——每层独立设防，单层失守不塌方。

## 第一层：Pod 安全三档标准

| 档位 | 语义 | 适用 |
|---|---|---|
| Privileged | 全放开 | 仅系统组件 |
| Baseline | 防已知提权 | 默认档 |
| **Restricted** | 最严（非 root、只读根文件系统、丢全部能力） | 生产工作负载目标档 |

推进策略：命名空间打标签逐档收严（enforce 强制 + audit 审计 + warn 警告三轨并行），新命名空间直接 Restricted，老 namespace 灰度迁移。Restricted Pod 关键项：`runAsNonRoot: true`、`readOnlyRootFilesystem: true`、`allowPrivilegeEscalation: false`、`capabilities.drop: ALL`。

## 第二层：网络策略（默认拒绝）

- **起点一律 default-deny-all**（进向 + 出向全拒），再按调用关系白名单放行——「先全通再堵」永远堵不完。
- 必放白名单：DNS（出向 53 → kube-system）、授权调用方 → 授权端口（如 frontend → backend:8080）。
- 网络策略是**加法叠加**：命中任意一条即放行——写策略时按「谁调谁」的依赖图来，别凭感觉。

## 第三层：RBAC 最小权限

- 命名空间内用 Role，全集群才用 ClusterRole——**能用小就不用大**。
- 动词最小化：只读就 `get, watch, list`，别图省事给 `*`。
- ServiceAccount 一服务一个（不共享 default SA），人按组授权不按个人。
- 定期审：`kubectl auth can-i --list` 逐 SA 核对——权限漂移（图省事的临时授权忘了收）是常态。

## 第四层：准入控制

- 策略即代码（OPA/Gatekeeper 类）：镜像必须来自可信仓库、必须带标签、资源限额必须设置——**在准入时拦住**，不等运行时发现。
- 审计模式先跑（只报不拦）→ 观察误报 → 切强制——一把切强制是自断流水线。

## 镜像供应链

- 可信基础镜像（distroless/最小化）+ 漏洞扫描进 CI（高危阻断）。
- 镜像签名与校验；标签不可变（用 digest 引用生产镜像，别用 latest）。

## 收尾清单

生产 namespace 到 Restricted / default-deny 起步白名单放行 / SA 独立且权限最小 / 准入策略审计先行 / 镜像扫描签名 / 定期权限审计。
