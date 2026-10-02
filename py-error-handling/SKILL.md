---
name: Python 错误处理
version: 1.0.0
author: Shadeling 策展
summary: 早校验、具体异常、留上下文、批量分账
description: 要让 Python 程序失败得体面、调试省力时使用：入口早校验、异常分层具体、保留链条、批量失败分账收尾。
category: 开发
tags: Python, 错误处理, 异常
license: MIT
trigger: 处理异常 / 错误怎么抛 / 异常设计 / 失败处理
---

# Python 错误处理

目标：失败得体面、调试省力。四个原则：**快速失败、异常具体、保留上下文、局部失败不连坐。**

## 快速失败：入口先校验

任何昂贵操作之前，把参数挡在门口：

```python
def fetch_page(url: str, page_size: int) -> Page:
    if not url:
        raise ValueError("'url' is required")
    if not 1 <= page_size <= 100:
        raise ValueError(f"'page_size' must be 1-100, got {page_size}")
    # 到这里才安全
```

复杂结构用模式校验库（如 pydantic）一步到位，错误信息结构化。

## 异常要具体、带上下文

- 抛具体类型：`ValueError`/`TypeError`/自定义业务异常，不抛裸 `Exception`。
- 消息三件套：**什么错、为什么、怎么修**——`"page_size must be 1-100, got 500"` 优于 `"invalid"`。
- 保留链条：包装重抛时用 `raise NewError(...) from e`，原始堆栈不丢。

## 边界处转换类型

字符串进系统先转成领域类型（枚举、数据类），别让 `"prod"` / `None` 之类的原始值在代码里流窜——转换失败的异常天然集中在边界。

## 批量操作：失败分账

单项失败不该连坐整批：

```python
def process_batch(items) -> BatchResult:
    succeeded, failed = {}, {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

调用方拿两本账自行决定重试或上报；日志里把两本都写清。

## 日志与异常的分工

- 预期内的业务情况（用户输错密码）→ 正常返回值或业务异常，**不**打 ERROR。
- 真正需要人看的故障 → ERROR 且带上下文（ID、计数、状态）。
- 捕获后处理完就地记日志；重抛的不重复记（避免一条故障刷三遍）。

## 收尾清单

入口已校验 / 异常类型具体 / 消息含修法 / 链条未断（from e）/ 批量分账 / 文档列出了可能抛的异常 / 日志带上下文。
