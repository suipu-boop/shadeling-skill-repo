---
name: Python 测试模式
version: 1.0.0
author: Shadeling 策展
summary: pytest 实战套路：夹具、参数化、mock、异步、属性测试
description: 写 Python 测试、搭测试设施时使用：AAA 结构、fixture 作用域、参数化、mock 边界、异常断言、异步与属性测试全套模式。
category: 开发
tags: Python, 测试, pytest
license: MIT
trigger: 写测试 / pytest 怎么用 / 测试套路 / 补测试用例
---

# Python 测试模式

pytest 实战套路集。流程层的 TDD 见既有 tdd 技能——这里管**怎么写好单个测试与设施**。

## 结构与命名

- **AAA 结构**：Arrange 备数据 → Act 执行 → Assert 断言，一段一个目的。
- **命名公式**：`test_<单元>_<场景>_<预期>`——`test_create_user_with_duplicate_email_raises_conflict` 一眼可读。
- **一测一行为一**：一个测试只验证一个行为；错误路径单独开测试。
- 目录分层：`tests/` 下按 unit / integration / e2e 分包，`conftest.py` 放共享夹具。

## 夹具（fixture）

```python
@pytest.fixture
def db() -> Generator[Database, None, None]:
    database = Database("sqlite:///:memory:")
    database.connect()
    yield database          # 提供给测试
    database.disconnect()   # 收尾
```

- 作用域按成本选：默认每个测试新建；昂贵的资源用 `scope="module"` / `"session"`。
- `autouse=True` 的夹具做全局前置（如清库）；参数化夹具（`params=[...]`）让同一测试跑多种后端。

## 参数化

一组输入预期写成一个用例：

```python
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid.email", False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected
```

## Mock：只 mock 边界

网络、时钟、文件系统才 mock；业务逻辑走真实现。

```python
def test_get_user_not_found():
    client = APIClient("https://api.example.com")
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")
    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            client.get_user(999)
```

- 断言调用方式用 `assert_called_once_with(...)` / `call_args.kwargs`。
- 过度 mock 的信号：改实现测试全红但行为没坏——说明 mock 到了内部。

## 异常断言

```python
def test_zero_division():
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        divide(5, 0)
```

错误路径必测：非法输入、重复创建、边界值。

## 异步测试

```python
@pytest.mark.asyncio
async def test_concurrent_fetches():
    tasks = [fetch_data(u) for u in urls]
    results = await asyncio.gather(*tasks)
    assert all("data" in r for r in results)
```

异步夹具同样用 `yield`；并发行为用 `gather` 一次测。

## 冻结时间与打桩

- 时间敏感逻辑用 freezegun 冻结时钟，测试不随日期漂移。
- 环境变量/外部状态用 `monkeypatch.setenv` / `setattr`，测试结束自动还原。

## 属性测试（进阶）

不变量驱动：反转两次等于原串、排序后长度不变且有序。用 hypothesis 给随机输入，抓边角案例：

```python
@given(st.lists(st.integers()))
def test_sorted_properties(lst):
    s = sorted(lst)
    assert len(s) == len(lst) and set(s) == set(lst)
```

## 覆盖率

`pytest --cov` 看盲区，但覆盖率是体检指标不是目标——**测行为，不凑行数**。
