---
name: Python 类型安全
version: 1.0.0
author: Shadeling 策展
summary: 注释当文档用：签名全标注、收窄、泛型、Result 模式
description: 要让类型检查器帮 Python 代码抓错时使用：公共签名全标注、现代联合语法、条件收窄、泛型容器与 Result 错误模式。
category: 开发
tags: Python, 类型, 类型检查
license: MIT
trigger: 加类型注解 / 类型检查 / mypy 报错 / 类型安全
---

# Python 类型安全

类型注解是**会被工具强制的文档**：写一次，静态检查替你抓一辈子的错。

## 公共签名全标注

所有公开函数：入参、返回值全注解。返回值最值钱——「可能没有」必须写成 `X | None`，调用方被迫处理 None 分支：

```python
def get_user(user_id: str) -> User | None:
    """返回值类型把「可能不存在」写成了显式契约。"""

user = get_user("123")
if user is None:
    raise UserNotFoundError("123")
print(user.name)   # 检查器知道这里 user 一定是 User
```

现代联合语法直接用 `X | None`（3.10+），不写 `Optional[X]`。集合永远带参数：`list[User]`、`dict[str, int]`。

## 条件收窄（narrowing）

检查器顺着条件分支缩类型：

```python
def process_user(user_id: str) -> UserData:
    user = find_user(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return UserData(name=user.name, ...)   # 这里已收窄为 User

def process_items(items: list[Item | None]) -> list[ProcessedItem]:
    valid = [i for i in items if i is not None]   # 收窄成 list[Item]
    return [process(i) for i in valid]
```

先断言/早抛，后面的代码就站在「已验证」的地基上——这是类型安全与快速失败的合流点。

## 泛型容器：Result 模式

错误处理里最实用的泛型：成功或失败二选一，类型系统强制调用方二选一地处理：

```python
T = TypeVar("T"); E = TypeVar("E", bound=Exception)

class Result(Generic[T, E]):
    def is_success(self) -> bool: ...
    def unwrap(self) -> T:            # 失败时抛出内含错误
        ...
    def unwrap_or(self, default: T) -> T: ...

def parse_config(path: str) -> Result[Config, ConfigError]: ...

result = parse_config("config.yaml")
if result.is_success:
    config = result.unwrap()          # 类型: Config
```

约束：value 与 error 恰好一个有值（构造时校验）。

## Protocol：面向能力而非继承

鸭子类型的静态版——函数声明「我需要什么方法」，不关心来路：

```python
class Closeable(Protocol):
    def close(self) -> None: ...

def cleanup(res: Closeable) -> None:
    res.close()      # 任何有 close() 的对象都收
```

## 渐进落地

- 老库不要求一口气全标——从公共 API 与最近改动区开始（对应架构普查的热区思路）。
- `py.typed` 标记文件放进包里，下游才能吃到你的注解。
- 配置：严格度随项目成长逐步上调；CI 里跑类型检查当门禁，红灯不过合并。
