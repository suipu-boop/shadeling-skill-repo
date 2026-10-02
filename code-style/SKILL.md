---
name: 代码风格
version: 1.0.0
author: Shadeling 策展
summary: 格式化交给工具，人只管命名清晰和文档完整
description: 统一 Python 代码风格、配置格式化与类型检查工具链时使用：自动格式化边界、PEP 8 命名要点、Google 文档字符串、import 排序。
category: 开发
tags: Python, 代码风格, 工具链
license: MIT
trigger: 代码风格 / 格式化 / lint 配置 / 命名规范
---

# 代码风格

大原则：**能自动化的绝不靠人**。格式化、import 排序、lint 全交工具，人的注意力只花在机器管不了的：命名是否达意、抽象是否合理。

## 工具链最小集

- **格式化**（Ruff format / Black）：零配置统一风格，装饰器空格、字符串引号这类争论就地消灭。
- **lint**（Ruff）：接替 flake8/isort/pyupgrade 一票工具；import 排序开 `I` 规则。
- **类型检查**（mypy/pyright）：从宽松配置起步，CI 里当门禁。

配置全进 `pyproject.toml`，一条 `ruff check --fix && ruff format` 收尾全部。

## 命名：清晰压倒简短

- 文件/模块/函数/变量：snake_case，**禁无意义缩写**（`user_repository` 不是 `usr_repo`）。
- 类：PascalCase；缩写词保持大写（`HTTPClientFactory`）。
- 常量：SCREAMING_SNAKE_CASE（`MAX_RETRY_ATTEMPTS = 3`）。
- 布尔变量读起来像断言：`is_valid`、`has_permission`、`retry_enabled`。
- 判断标准：三个月后的自己（或新人）看名字不用点进去就知道它干什么。

## 文档字符串：公共 API 全配

Google 风格（简洁、IDE 友好）：

```python
def process_batch(items: list[Item], max_workers: int = 4) -> BatchResult:
    """并发处理一批条目。

    Args:
        items: 待处理条目，不能为空。
        max_workers: 最大并发数，默认 4。

    Returns:
        BatchResult：成功项 + 失败项（带异常）。

    Raises:
        ValueError: items 为空时。
    """
```

- 私有函数一句话 docstring 即可；公共函数参数/返回/异常三段全写。
- 类型注解与 docstring 不重复——注解说类型，docstring 说语义（单位、边界、副作用）。

## import 与杂项

- 三组：标准库 / 三方 / 本地，组间空行——工具自动排序，评审不用管。
- 行长 88-100（格式化工具说了算，别手掰）。
- 禁裸 `except:`、禁 `print` 调试残留（lint 规则管）。

## 团队落地

规范写进 `pyproject.toml` + 贡献指南，CI 强制——**规范不进 CI 等于没有规范**；存量代码豁免渐改（新代码必须过，老代码改到哪算哪）。

## 收尾清单

格式化 lint 类型检查三件套在 CI / 配置进 pyproject / 命名无缩写 / 公共 API docstring 全 / import 自动排序 / 裸 except 与 print 已绝迹。
