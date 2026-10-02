---
name: Python 可观测性
version: 1.0.0
author: Shadeling 策展
summary: 结构化日志加关联 ID 加四金信号，出事不靠猜
description: 要让 Python 服务出问题能快速定位时使用：结构化日志字段统一、关联 ID 全链路穿透、语义分级、四大黄金信号埋点。
category: 开发
tags: Python, 可观测性, 日志
license: MIT
trigger: 加日志 / 排障埋点 / 可观测性 / 结构化日志
---

# Python 可观测性

目标：出事时**不部署新代码就能回答「什么坏了、坏在哪、为什么」**。三件套：结构化日志、关联 ID、黄金信号。

## 结构化日志

日志是数据不是散文——一行一条 JSON，字段统一可过滤：

```python
logger.info("Request completed",
            correlation_id=cid, method="POST",
            path="/orders", status_code=200, duration_ms=45)
```

- 启动时配置一次（structlog JSON 渲染），全应用共享。
- **字段表**：每类事件固定字段集（correlation_id、method、path、user_id、duration_ms、error_type），别每处自造。
- 消息写「发生了什么」，细节进字段——`"Order created"` + `order_id=...`，而不是把 ID 拼进句子。

## 语义分级（别乱用 ERROR）

| 级别 | 用途 | 例 |
|---|---|---|
| DEBUG | 开发诊断 | 变量值、缓存命中 |
| INFO | 生命周期 | 请求起止、任务完成 |
| WARNING | 可恢复异常 | 重试中、降级生效、配额将满 |
| ERROR | 需人处理 | 未预期异常、下游不可用 |

铁律：**预期行为不打 ERROR**——用户输错密码是 INFO 级业务事件。ERROR 刷屏 = 狼来了。

## 关联 ID 全链穿透

入口生成（或接上游 `X-Correlation-ID`），存进 ContextVar，所有日志自动带上；出站调用把 ID 传给下游：

```python
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def set_correlation_id(cid: str | None = None) -> str:
    cid = cid or str(uuid.uuid4())
    correlation_id.set(cid)
    return cid
```

中间件里统一 set + 回写响应头。排障时一个 ID 串起整条请求的所有日志。

## 操作计时（上下文管理器）

```python
with timed_operation("fetch_user_orders", user_id=user.id):
    orders = await repo.get_by_user(user.id)
```

成功/失败都自动记耗时与结果——手动 `start = time.time()` 写八遍不如封装一个。

## 四大黄金信号（每个服务边界都埋）

1. **延迟**——请求耗时分布（直方图，不只平均值）
2. **流量**——请求速率（计数器按方法/路径/状态分桶）
3. **错误**——错误率（按错误类型细分）
4. **饱和度**——资源水位（连接池占用、队列深度）

装饰器统一埋点：进 `perf_counter()`，出 `observe` 耗时 + `inc` 计数，异常单独累计。**基数要有界**：user_id、订单号这类高基数值禁止进标签，否则监控系统撑爆。

## 收尾清单

日志结构化且字段统一 / 分级语义正确 / 关联 ID 穿透 / 关键操作有计时 / 四信号已埋 / 标签基数有界。
