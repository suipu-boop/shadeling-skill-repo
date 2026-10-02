---
name: 配置管理
version: 1.0.0
author: Shadeling 策展
summary: 类型化配置：外置、启动即校验、缺了就崩
description: 管理 Python 应用配置（环境变量、.env、密钥）时使用：类型化 Settings 类、启动期失败、命名空间前缀、默认值分层。
category: 开发
tags: Python, 配置, 环境变量
license: MIT
trigger: 配置管理 / 环境变量 / settings / 读配置
---

# 配置管理

配置四原则：**外置**（代码不带环境差异）、**类型化**（读进来就是对的对象）、**快速失败**（缺配置活不到第一个请求）、**默认合理**（本地零配置能跑）。

## 类型化 Settings：一个类收口全部

```python
class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    api_secret_key: str = Field(alias="API_SECRET_KEY")
    enable_new_feature: bool = Field(default=False, alias="ENABLE_NEW_FEATURE")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

try:
    settings = Settings()          # 模块加载时构造
except ValidationError as e:
    print(f"配置错误:\n{e}")
    sys.exit(1)                    # 缺配置当场崩，别等运行时
```

全应用只 import `settings` 单例——配置入口唯一，审计与测试都简单。

## 快速失败

- 必填项没有默认值，缺了就在**启动时**炸——运行到一半才崩的配置错误是最贵的故障。
- 校验的不只是「有没有」：端口是 int、URL 是合法 Dsn、密钥非空——类型系统替你查。
- 密钥类配置绝不写代码、不进 git（.env 进 .gitignore），启动时必须存在。

## 命名空间前缀

环境变量按应用加前缀防撞车：`SHADELING_DB_HOST`、`SHADELING_LOG_LEVEL`。前缀统一收在 Settings 类里处理，业务代码读的是 `settings.db_host`，不感知前缀。

## 默认值分层

`代码默认值 < .env < 环境变量`（后者覆盖前者）。代码默认值 = 本地开发能直接跑；生产环境用环境变量盖上去。例外：**密钥与连接串不给代码默认值**——本地逼你显式配，防生产连到开发库这种事故。

## 测试与常见坑

- 测试里用 `Settings(_env_file=None)` + monkeypatch 环境变量，或直接构造 Settings 对象注入——测试不依赖真实环境。
- 坑：配置散落各处 `os.getenv`（收口到一个类）；bool 用字符串判断（"false" 是真值）；改配置要重启不知道（配置打印成日志——密钥打码）。

## 收尾清单

配置单类收口 / 启动期校验炸 / 必填项无危险默认 / 密钥不进 git / 环境变量带前缀 / 分层覆盖关系明确。
