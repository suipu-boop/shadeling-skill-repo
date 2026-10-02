---
name: Go 并发
version: 1.0.0
author: Shadeling 策展
summary: 用通信共享内存、context 传递取消、goroutine 必有出口
description: 写 Go 并发代码、做 worker 池/管道、排查数据竞争时使用：channel/選择器心法、context 取消传播、泄漏防范、竞争检测。
category: 开发
tags: Go, 并发, 编程语言
license: MIT
trigger: Go 并发 / goroutine / channel / 数据竞争
---

# Go 并发

Go 并发心法一句：**不要通过共享内存来通信，而要通过通信来共享内存**——数据归 channel 管，锁是最后手段。

## 原语分工

| 原语 | 用途 |
|---|---|
| `goroutine` | 轻量并发执行（go 关键字即起） |
| `channel` | goroutine 间传数据/信号 |
| `select` | 多路复用（同时等多个 channel/取消） |
| `sync.WaitGroup` | 等一组完成 |
| `sync.Mutex` | 保护真绕不开的共享状态 |
| `context.Context` | 取消信号与超时的标准载体 |

## Worker 池骨架（背下来）

```
ctx 带超时 → N 个 worker go 起来（select 监听 ctx.Done() 与任务）
→ sync.WaitGroup 等全部退出 → close(结果 channel)（由发送方关）
→ 主 goroutine range 收结果
```

要点：**channel 由发送方关闭**（接收方关闭 = panic）；知道数量时给结果 channel 建缓冲。

## context 纪律

- context 是 Go 并发的**取消总线**：超时/取消从入口一路传下去，每层 select 检查 `ctx.Done()`。
- 不接 context 的长任务 = 无法取消的任务 = 关服时挂不掉的任务。**所有阻塞操作都要能被 context 打断**。

## 泄漏防范（goroutine 泄漏 = 内存泄漏）

- **每个 goroutine 必有出口**：启动前想好「它怎么退出」——监听 ctx、监听退出 channel、或任务天然有限。
- `time.Sleep` 做同步是味道：等什么就 select 什么，别赌时间。
- 无界 goroutine（每请求一个不限流）= 雪崩预备队——用带缓冲 channel 或信号量限并发。
- 数据竞争防不住就上工具：`go build -race`（竞争检测器）进 CI，race 报告零容忍。

## errgroup 组合

并发子任务带错误传播用 `errgroup`：一个失败全组取消、Wait 返回首个错误——手写 error channel + WaitGroup 的现代替代。

## 收尾清单

通信优先于锁 / channel 发送方关 / context 全链贯通 / goroutine 有出口 / 并发有限流 / -race 进 CI。
