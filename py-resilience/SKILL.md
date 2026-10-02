---
name: Python 韧性模式
version: 1.0.0
author: Shadeling 策展
summary: 瞬时故障白名单重试，指数退避加抖动加超时
description: Python 服务调外部依赖不可靠时使用：区分瞬时与永久故障、只重试白名单、指数退避带抖动、超时装饰器兜底。
category: 开发
tags: Python, 韧性, 重试
license: MIT
trigger: 加重试 / 网络抖动 / 服务不稳 / 超时处理
---

# Python 韧性模式

依赖不可靠时让系统站得住。核心认知：**不是所有错误都值得重试**。

## 先分诊：瞬时 vs 永久

- **瞬时**（值得重试）：连接超时、读超时、连接被重置、HTTP 429/500/502/503/504。
- **永久**（重试是浪费甚至有害）：`ValueError`/`TypeError`（是 bug 不是故障）、认证失败（凭证不会自己变对）、其他 4xx（请求本身错了）。

白名单制：只对明确列出的瞬时异常/状态码重试，其余立即失败。

## 重试三参数

- **有界次数**：3-5 次封顶，配总时长上限（如 60 秒）——防雪崩。
- **指数退避**：1s → 2s → 4s → …，给下游喘息。
- **加抖动（jitter）**：退避间隔随机化，防止千百个客户端同步重试打爆恢复中的服务。

```python
TRANSIENT = (ConnectionError, TimeoutError, OSError)

@retry(
    retry=retry_if_exception_type(TRANSIENT),
    stop=stop_after_attempt(5) | stop_after_delay(60),
    wait=wait_exponential_jitter(initial=1, max=30),
)
def fetch_data(url: str) -> dict:
    r = httpx.get(url, timeout=30)
    r.raise_for_status()
    return r.json()
```

## 异常 + 状态码双轨重试

HTTP 调用两类故障都要抓：抛异常的网络错误 + 返回 5xx/429 的响应。

```python
RETRY_STATUS = {429, 500, 502, 503, 504}

def is_retryable(resp) -> bool:
    return resp.status_code in RETRY_STATUS

@retry(
    retry=retry_if_exception_type(TRANSIENT) | retry_if_result(is_retryable),
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def robust_call(method: str, url: str, **kw):
    return httpx.request(method, url, timeout=30, **kw)
```

`before_sleep` 挂 WARNING 日志——每次重试留痕（第几次、等多久、什么错），排障有据。

## 超时：每个外呼都必须有

没有超时的调用 = 无限赌注。三层面兜底：

- **请求超时**：客户端级 `timeout=30`（连接+读取都有默认值兜底）。
- **函数超时**：异步函数套 `asyncio.wait_for` 封装成装饰器，统一策略。
- **全局纪律**：新写任何外呼，超时是和功能一起交付的，不是事后补。

## 收尾要点

- 重试只在**一层**做（配合反模式清单：双重重试是大坑）——先弄清底层基础设施（负载均衡、SDK）自带的容错再决定上层要不要加。
- 重试逻辑要**可测**：把「判断是否可重试」写成纯函数；测试里验证白名单边界（429 重试、404 不重试）。
- 幂等是重试的前提——非幂等操作先加幂等键，否则重试 = 重复下单。

## 收尾清单

白名单明确 / 次数与总时长有界 / 指数退避带抖动 / 每次重试留日志 / 全部外呼有超时 / 重试操作幂等。
