---
name: 异步模式
version: 1.0.0
author: Shadeling 策展
summary: async 三坑：忘 await、堵循环、不管取消
description: 写 Python 并发 IO、异步服务时使用：同步异步选型、gather 并发、超时取消、阻塞事件循环等典型坑的对治。
category: 开发
tags: Python, 异步, 并发
license: MIT
trigger: 写异步 / asyncio / 并发请求 / async 用法
---

# 异步模式

异步只解决一类问题：**高并发 IO 等待**。CPU 密集、低并发脚本，同步更简单好调。

## 选型速查

| 场景 | 选择 |
|---|---|
| 大量并发网络/DB 调用 | asyncio |
| CPU 密集计算 | multiprocessing |
| IO + CPU 混合 | 异步为主，CPU 活 `to_thread()` 甩出去 |
| 简单脚本、几个连接 | 同步（好写好调） |

**铁律：一条调用链上，要么全同步要么全异步。** 混用是隐藏阻塞与复杂度的根源。

## 核心三件

- **协程**：`async def` 定义、`await` 驱动——await 的不是函数调用，是「让出控制权等结果」。
- **任务**：`asyncio.create_task()` 把协程排进事件循环立刻开跑，拿句柄管理（取消、查状态）。
- **gather**：并发跑一批协程收全部结果——

```python
async def fetch_all(user_ids: list[int]) -> list[dict]:
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)   # 并发而非串行
```

## 超时与取消

- 超时：`asyncio.wait_for(coro, timeout=5)`——每个外呼都要有（同韧性模式铁律）。
- 取消：任务可能随时被取消（超时、关机、上层放弃）。`except asyncio.CancelledError:` 里做清理，**清理完必须重新 raise**——吞掉取消 = 任务杀不死。
- 优雅关停：gather 的任务们逐个 cancel + gather(return_exceptions=True) 等齐收尾。

## 四大坑（全部高频）

1. **忘 await**：`result = async_fn()` 拿到的是协程对象，函数根本没执行——返回异常或警告盯着点。
2. **堵事件循环**：协程里写 `time.sleep(1)` / 重 CPU 计算 / 同步 IO——整个循环卡死，所有并发全停。阻塞活交给 `to_thread()` 或用 `asyncio.sleep`。
3. **不处理取消**：CancelledError 不接或接了不抛——任务成僵尸。
4. **同步里硬调异步**：`asyncio.run()` 只用在程序入口；嵌套 run 会炸。

## 测试

`pytest-asyncio` 的 `@pytest.mark.asyncio` 直接写异步测试；超时行为用 `wait_for` + `pytest.raises(TimeoutError)` 验证；取消路径必须测（触发取消，断言清理跑了且任务真停了）。

## 收尾清单

选型先问 IO 还是 CPU / 调用链不混搭 / 并发用 gather / 外呼全带超时 / 取消路径会清理 / 无事件循环阻塞。
