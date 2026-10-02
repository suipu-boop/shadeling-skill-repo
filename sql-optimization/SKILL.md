---
name: SQL 优化
version: 1.0.0
author: Shadeling 策展
summary: 先看执行计划，再上对索引，改写慢查询
description: SQL 查询慢要提速时使用：读 EXPLAIN 执行计划、按查询模式选索引类型、避免索引失效的写法、持续监控慢查询。
category: 开发
tags: SQL, 数据库, 性能
license: MIT
trigger: SQL 慢 / 查询优化 / 数据库调优 / 索引怎么建
---

# SQL 优化

顺序不能反：**先执行计划，再索引，再改写**。猜着优化 = 白干。

## 第一步：读执行计划

`EXPLAIN ANALYZE`（PostgreSQL）看真实执行：估计成本、实际耗时、扫描方式、连接方法。

关键字样速查：
- **Seq Scan**（全表扫）大表上基本就是病根
- **Index Scan / Index Only Scan**：走索引，后者最优（连表都不用回）
- **Nested Loop** 小数据集可，**Hash Join** 大数据集好，**Merge Join** 适合已排序数据
- 估计行数与实际行数差一个量级 = 统计信息过期，先 `ANALYZE` 表

## 第二步：索引策略

选型：**B-Tree** 默认（等值+范围）、**Hash** 仅等值、**GIN** 全文/数组/JSONB、**BRIN** 超大表且物理有序。

```sql
-- 组合索引：列序有讲究（最常过滤的在前）
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 部分索引：只索引关心的行，又小又快
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 表达式索引：查询用了函数就要配对
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- 覆盖索引：多带一列免回表
CREATE INDEX idx_users_email_covering ON users(email) INCLUDE (name);
```

纪律：索引不是越多越好——写放大、空间、优化器选错都可能。每个索引要能说出「服务哪条查询」。

## 第三步：查询改写（索引失效重灾区）

- **别 `SELECT *`**：只取要的列，配覆盖索引免回表。
- **列上套函数 = 索引作废**：`WHERE LOWER(email)=...` 要么建表达式索引，要么存归一化数据。
- **先过滤后连接**：把大表的过滤条件推到子查询/JOIN 早期，别笛卡尔积完再筛。
- **分页深翻**：`OFFSET 100000` 慢到哭；用游标分页（`WHERE id > last_id LIMIT n`）。
- **N+1**：应用层循环查库是数据库第一大杀手——合并成一次 IN 查询或 JOIN。

## 持续监控

慢查询日志常开（阈值按业务定）；`pg_stat_statements` 攒累计耗时排行；定期扫 Top N 治理。优化后**复测执行计划**，确认真的变了。

## 速查表

| 症状 | 第一嫌疑 |
|---|---|
| 大表 Seq Scan | 缺索引 / 列上套函数 |
| 估计行数偏差大 | 统计信息过期 |
| 深分页慢 | OFFSET 改游标 |
| 应用吞吐卡 | N+1 查询 |
| 写入变慢 | 索引过多 |
