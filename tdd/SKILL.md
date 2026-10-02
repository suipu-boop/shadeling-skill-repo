---
name: 测试先行
version: 1.0.0
author: Shadeling 策展
summary: 先写会失败的测试，再写刚好够的代码
description: 建新功能或修 bug 时用它建立测试先行节奏——先定测试边界，写失败测试，再最小实现，循环推进。
category: 开发
tags: 测试, TDD, 红绿循环
license: MIT
trigger: 测试先行 / 先写测试 / 红绿循环 / 帮我建测试
source: third_party
upstream: https://github.com/mattpocock/skills
upstream_commit: d81f3a183412
converted_at: 2026-10-01
converted_by: Shadeling 策展（设计意图参考 mattpocock/skills engineering/tdd，MIT）
---

测试先行——红 → 绿循环。这份参考让循环产出的测试值得保留：什么是好测试、测试放哪、反模式长什么样、循环规则。每一段在每个循环都用得上：写之前看，写的过程中看，不是写完再看。

## 什么是好测试

测试通过公开接口验证行为，不碰实现细节。代码可以整个重写，测试不该跟着改。好测试读起来像规格说明：「用户可以用有效购物车结账」——它告诉你存在什么能力，重构后依然成立，因为它根本不关心内部结构。

## 测试放哪：缝（seam）

**缝**是公开边界：你在不伸手进内部的前提下观察行为的接口位置。测试只打在缝上，永远不打内部。

**只在事先约定的缝上写测试。** 动笔前，先列出本次要测的缝并与用户确认。没确认的缝不写测试。测不完所有东西——事先把缝敲定，测试精力才会落在关键路径和复杂逻辑上，而不是撒到每个边角。

问一句：「公开接口是什么，该测哪几条缝？」

## 反模式

- **实现耦合**：mock 内部协作者、测私有方法、从旁路验证（绕过接口直接查数据库）。特征：一重构测试就红，但行为根本没变。
- **同义反复**：断言用和代码一样的方式重算期望值（`expect(add(a,b)).toBe(a+b)`），测试构造上就恒真，永远不可能反对代码。期望值必须来自独立事实源：已知正确的字面量、算好的例子、规格。
- **横切**：先写完所有测试再写所有实现。批量测试验证的是**想象中的行为**，测的是事物的形状而不是用户可见的行为。要纵切：一个测试 → 一份实现 → 重复，每个测试都是修正前进方向的曳光弹。

## 循环规则

- **先红后绿**：先写失败的测试，再写刚好让它通过的代码。不预支未来的测试，不加投机功能。
- **一次一片**：每个循环一条缝、一个测试、一份最小实现。
- **重构不在循环里**：重构属于审查阶段，不属于红 → 绿的实现循环。

## 附录一：好测试与坏测试的例子

**集成式好测试**——走真实接口，不 mock 内件：

```typescript
// 好：测可观察行为
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特征：测用户/调用方关心的行为；只用公开 API；内部重构后依然成立；说 WHAT 不说 HOW；一个测试一个逻辑断言。

**实现细节坏测试**——耦合内部结构：

```typescript
// 坏：测实现细节
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

红旗：mock 内部协作者；测私有方法；断言调用次数/顺序；重构不改行为测试就红；测试名说 HOW 不说 WHAT；绕过接口验证。

**同义反复坏测试**——期望值照抄实现：

```typescript
// 坏：期望值用代码同款方式算出来
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// 好：期望值是独立已知的字面量
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

**旁路坏测试**——绕过接口验证：

```typescript
// 坏：直接查库验证
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// 好：从接口验证
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

## 附录二：什么时候该 mock

只在**系统边界** mock：

- 外部 API（支付、邮件等）
- 数据库（有时——优先测试库）
- 时间/随机数
- 文件系统（有时）

不 mock：你自己写的类/模块、内部协作者、一切你能控制的东西。

**为可 mock 性而设计**：在系统边界上，把接口设计成好 mock 的形状。

1. **依赖注入**——外部依赖传进来，不在内部 new：

```typescript
// 好 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

2. **SDK 式接口优于通用 fetcher**——每个外部操作一个具体函数，而不是一个带条件分支的通用函数：

```typescript
// 好：每个函数独立可 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// 坏：mock 得在测试里写条件逻辑
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 式的好处：每个 mock 只返回一种形状；测试准备里没有条件逻辑；一眼看清测试打了哪些端点。
