---
name: 资源管理
version: 1.0.0
author: Shadeling 策展
summary: 上下文管理器管资源：进入即 acquire，退出必释放
description: Python 里管连接、文件、锁等有限资源时使用：上下文管理器协议、async 变体、无条件清理与异常安全的写法。
category: 开发
tags: Python, 资源, 上下文管理器
license: MIT
trigger: 资源泄漏 / 连接管理 / with 用法 / 上下文管理器
---

# 资源管理

资源（连接、文件、锁、信号量）有限且会泄漏。纪律一句话：**acquire 与 release 永远成对，交由上下文管理器托管**。

## 协议：`__enter__` / `__exit__`

```python
class DatabaseConnection:
    def __enter__(self) -> "DatabaseConnection":
        self._conn = connect(self._dsn)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()          # 无论成功失败、无论异常类型，必达
```

`with DatabaseConnection(dsn) as db:` ——`__exit__` 在三种情况下都会跑：正常结束、抛异常、with 体内 return/break。这就是「无条件清理」，手写 try/finally 容易漏，协议不会。

## 两种实现选型

- **类实现**（上面的）：资源状态复杂、要复用实例、需要多个方法时用。
- **@contextmanager 生成器**：简单的「前后脚」逻辑一气呵成——

```python
@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield                       # with 体的内容在这跑
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")
```

yield 前是 `__enter__`，finally 是 `__exit__`——**finally 必须包住 yield**，不然异常路径泄漏。

## 异步变体

async 资源用 `__aenter__` / `__aexit__`，配 `async with`；`@asynccontextmanager` 同理。连接池、异步锁的持有释放全部走它。

## 异常安全细节

- `__exit__` 返回 True 会**吞掉异常**——默认返回 None/False（不吞），除非明确在做「把异常翻译成领域错误」。
- acquire 之后、with 之前的代码会泄漏——**acquire 动作放进 `__enter__` 里**，别让「已 acquire 未托管」的窗口存在。
- 多资源嵌套用逗号合并：`with open(a) as fa, open(b) as fb:`。

## 收尾清单

资源全部 with 托管 / 类实现 close 幂等（重复关不炸）/ 装饰器实现 finally 包 yield / acquire 在 `__enter__` 内 / 异步资源用 async with / `__exit__` 不乱吞异常。
