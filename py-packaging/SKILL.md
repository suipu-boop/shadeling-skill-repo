---
name: Python 打包发布
version: 1.0.0
author: Shadeling 策展
summary: pyproject 一把梭：src 布局、构建、发布 PyPI
description: 要把 Python 代码做成可安装的包并发布时使用：src 布局防误导入、pyproject.toml 全量配置、本地构建、TestPyPI 试发布。
category: 开发
tags: Python, 打包, 发布
license: MIT
trigger: 打包发布 / 做 Python 包 / 发 PyPI / pyproject 配置
---

# Python 打包发布

现代打包全走 `pyproject.toml` 一个文件，不再用 setup.py 散装配置。

## 目录：src 布局（首选）

```
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       └── py.typed        # 有类型注解就放这个标记
└── tests/
    └── test_core.py
```

src 布局的好处：**必须先安装才能导入**——杜绝「在项目根目录能跑、装完就坏」的经典事故；测试测到的就是用户装到的。配套配置：

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

扁平布局（包目录放根下）仅用于不需要安装的内部小工具。

## pyproject.toml 最小集

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
description = "一句话说明"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.4"]
```

- 依赖约束写**下限**（`>=`），上限留给应用层锁。
- 可选依赖组（dev/docs/test）让用户按需装。
- 版本单一事实源：`__init__.py` 里 `__version__`，配置 `dynamic = ["version"]` 自动读取；或用 setuptools-scm 直接从 git tag 生成。

## 本地构建

```bash
python -m build        # 产出 dist/：.tar.gz 源码包 + .whl 轮子
twine check dist/*     # 元数据体检
```

两条产物都要有：轮子给用户快装，源码包给打包器回退。

## 发布：先试后真

```bash
twine upload --repository testpypi dist/*     # 1. 先发 TestPyPI
pip install --index-url https://test.pypi.org/simple/ my-package   # 2. 装回验证
twine upload dist/*                            # 3. 没问题再发 PyPI
```

- 认证用 API token（`~/.pypirc` 配 `username = __token__`），不配明文密码。
- 版本号只增不减；发错了就发新版本，别重传同名版本。
- CI 自动发布：打 tag 触发构建 + twine 上传，人只管打 tag。

## 收尾清单

src 布局 / pyproject 全量元数据 / 依赖写下限 / py.typed（若有注解）/ 本地 build+check 过 / TestPyPI 试装过 / token 认证。
